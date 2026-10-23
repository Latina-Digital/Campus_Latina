"""
Importación masiva de preguntas y usuarios.

Formato de texto / Word para preguntas:

    1. ¿Cuál es el tiempo de curado del enlucido?
    a) De 5 a 10 días
    b) De 15 a 20 días
    *c) De 28 a 31 días          <- el asterisco marca la correcta
    d) De 40 a 50 días
    Explicación: el enlucido debe curar casi un mes.   (opcional)

También se acepta "Respuesta: C" en lugar del asterisco.
Excel/CSV: columnas pregunta, a, b, c, d (hasta f), correcta (letra), explicacion.
"""
import csv
import io
import re
import unicodedata

from django.db import transaction

from apps.assessments.models import Choice, Question

Q_RE = re.compile(r"^\s*(?:\d+\s*[.)\-]|P\s*\d*\s*[:.)])\s*(.+)$", re.I)
OPT_RE = re.compile(r"^\s*(\*)?\s*([a-fA-F])\s*[).\-]\s*(\*)?\s*(.+?)\s*(\*|\(correcta\)|✓|✔)?\s*$", re.I)
ANS_RE = re.compile(r"^\s*(?:respuesta|correcta|resp)\s*(?:correcta)?\s*[:=]\s*([a-fA-F])\b", re.I)
EXP_RE = re.compile(r"^\s*(?:explicaci[oó]n|justificaci[oó]n)\s*[:=]\s*(.+)$", re.I)


def normalize(text):
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def parse_question_text(text):
    questions, current, errors = [], None, []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        opt = OPT_RE.match(line)
        if opt and current is not None and not Q_RE.match(line):
            star_before, letter, star_after, body, mark = opt.groups()
            current["choices"].append([body.strip(), bool(star_before or star_after or mark)])
            continue
        ans = ANS_RE.match(line)
        if ans and current is not None:
            idx = "abcdef".index(ans.group(1).lower())
            for i, choice in enumerate(current["choices"]):
                choice[1] = i == idx
            continue
        exp = EXP_RE.match(line)
        if exp and current is not None:
            current["explanation"] = exp.group(1).strip()
            continue
        q = Q_RE.match(line)
        if q or current is None or current["choices"]:
            current = {"text": (q.group(1) if q else line).strip(), "choices": [], "explanation": ""}
            questions.append(current)
        else:
            current["text"] += " " + line
    valid = []
    for n, q in enumerate(questions, start=1):
        if len(q["choices"]) < 2:
            errors.append(f"Pregunta {n} («{q['text'][:40]}…») no tiene al menos 2 opciones.")
        elif sum(1 for c in q["choices"] if c[1]) != 1:
            errors.append(f"Pregunta {n} («{q['text'][:40]}…») debe tener exactamente una respuesta correcta.")
        else:
            valid.append(q)
    return valid, errors


def _rows_from_table(file):
    name = file.name.lower()
    if name.endswith(".xlsx"):
        from openpyxl import load_workbook

        sheet = load_workbook(file, read_only=True, data_only=True).active
        rows = [[("" if v is None else str(v)).strip() for v in row] for row in sheet.iter_rows(values_only=True)]
    else:
        content = file.read().decode("utf-8-sig", errors="replace")
        dialect = csv.Sniffer().sniff(content[:2048], delimiters=",;\t") if content.strip() else csv.excel
        rows = [[c.strip() for c in row] for row in csv.reader(io.StringIO(content), dialect)]
    rows = [r for r in rows if any(r)]
    if not rows:
        return []
    header = [normalize(h) for h in rows[0]]
    return [dict(zip(header, row)) for row in rows[1:]]


def parse_question_table(file):
    questions, errors = [], []
    for n, row in enumerate(_rows_from_table(file), start=2):
        text = row.get("pregunta") or row.get("question")
        letters = [l for l in "abcdef" if row.get(l) or row.get(f"opcion_{l}")]
        choices = [row.get(l) or row.get(f"opcion_{l}") for l in letters]
        correct = (row.get("correcta") or row.get("respuesta") or "").strip().lower()[:1]
        if not text or len(choices) < 2 or correct not in letters:
            errors.append(f"Fila {n}: revisa la pregunta, las opciones o la columna 'correcta'.")
            continue
        questions.append(
            {"text": text, "choices": [[c, l == correct] for c, l in zip(choices, letters)], "explanation": row.get("explicacion", "")}
        )
    return questions, errors


def read_questions(file=None, text=""):
    if file is not None:
        name = file.name.lower()
        if name.endswith(".docx"):
            from docx import Document

            doc = Document(file)
            lines = [p.text for p in doc.paragraphs]
            for table in doc.tables:
                for row in table.rows:
                    lines.extend(cell.text for cell in row.cells)
            return parse_question_text("\n".join(lines))
        if name.endswith((".xlsx", ".csv")):
            return parse_question_table(file)
        return parse_question_text(file.read().decode("utf-8-sig", errors="replace"))
    return parse_question_text(text)


@transaction.atomic
def save_questions(quiz, questions, replace=False):
    if replace:
        quiz.questions.all().delete()
    start = quiz.questions.count()
    for i, q in enumerate(questions, start=start + 1):
        question = Question.objects.create(quiz=quiz, text=q["text"], explanation=q.get("explanation", ""), order=i)
        for j, (text, ok) in enumerate(q["choices"]):
            Choice.objects.create(question=question, text=text[:400], is_correct=ok, order=j)
    return len(questions)
