"""Certificado en PDF (A4 horizontal) con la identidad de Campus Latina y código QR de verificación.

A la izquierda, una franja con el patrón de la marca y, debajo, el QR que lleva a la
página de verificación. A la derecha, el texto del certificado, la medalla y las firmas.
"""
import io
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.utils import formats, timezone
from PIL import Image
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

NAVY = HexColor("#0A1C40")
RED = HexColor("#E3000F")
GOLD = HexColor("#FACC00")
INK = HexColor("#1F2937")
MUTED = HexColor("#6B7280")

IMG_DIR = settings.BASE_DIR / "static" / "img"
BAND_W = 172          # ancho de la franja izquierda
BAND_BOTTOM = 182     # debajo de la franja va el QR


@lru_cache(maxsize=4)
def _band(width, height):
    """La franja recortada a la proporción exacta del espacio (sin estirarla)."""
    img = Image.open(IMG_DIR / "certificado" / "franja.jpg")
    alto = round(img.width * height / width)
    img = img.crop((0, 0, img.width, min(alto, img.height)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=92)
    buf.seek(0)
    return ImageReader(buf)


def _image(path):
    return ImageReader(str(path)) if path.exists() else None


def _fit_text(c, text, font, size, max_width, min_size=12):
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 1
    return size


def _draw_fitted(c, img, x, y, max_w, max_h, center=True):
    """Dibuja una imagen dentro de la caja (x, y, max_w, max_h) sin deformarla."""
    w, h = img.getSize()
    scale = min(max_w / w, max_h / h)
    dw, dh = w * scale, h * scale
    dx = x + (max_w - dw) / 2 if center else x
    c.drawImage(img, dx, y, dw, dh, mask="auto")


def render_certificate(certificate, verify_url):
    buf = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setTitle(f"Certificado {certificate.code}")
    c.setAuthor(settings.CAMPUS_COMPANY)
    c.setSubject(certificate.course_title)

    # Franja de marca y, debajo, el QR de verificación
    band_h = height - BAND_BOTTOM
    c.drawImage(_band(BAND_W, band_h), 0, BAND_BOTTOM, BAND_W, band_h)
    qr_size = 116
    widget = QrCodeWidget(verify_url)
    widget.barBorder = 0
    x0, y0, x1, y1 = widget.getBounds()
    drawing = Drawing(qr_size, qr_size, transform=[qr_size / (x1 - x0), 0, 0, qr_size / (y1 - y0), 0, 0])
    drawing.add(widget)
    qr_x = (BAND_W - qr_size) / 2
    renderPDF.draw(drawing, c, qr_x, 50)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawCentredString(BAND_W / 2, 37, "Escanea para verificar")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(BAND_W / 2, 25, certificate.code)

    # Franja tricolor al pie del contenido
    third = (width - BAND_W) / 3
    for i, color in enumerate((NAVY, RED, GOLD)):
        c.setFillColor(color)
        c.rect(BAND_W + i * third, 0, third, 7, stroke=0, fill=1)

    left, right = BAND_W + 40, width - 40
    cx = (left + right) / 2

    # Logo y medalla
    logo = _image(IMG_DIR / "logo-latina-fondo.png")
    if logo:
        _draw_fitted(c, logo, cx - 90, height - 40 - 64, 180, 64)
    medal = _image(IMG_DIR / "certificado" / "medalla.png")
    if medal:
        _draw_fitted(c, medal, right - 88, height - 30 - 120, 88, 120)

    # Títulos
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(cx, height - 152, "CERTIFICADO")
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(cx, height - 173, "D E   A P R O B A C I Ó N")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, height - 208, f"{settings.CAMPUS_COMPANY}, a través de {settings.CAMPUS_NAME}, certifica que")

    # Nombre
    name = certificate.holder_name.upper()
    size = _fit_text(c, name, "Helvetica", 27, right - left - 40)
    c.setFillColor(INK)
    c.setFont("Helvetica", size)
    c.drawCentredString(cx, height - 252, name)

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, height - 284, "aprobó satisfactoriamente el curso:")

    # Curso: hasta dos líneas
    title = certificate.course_title.upper()
    size = 20
    lines = simpleSplit(title, "Helvetica-Bold", size, right - left - 60)
    while len(lines) > 2 and size > 13:
        size -= 1
        lines = simpleSplit(title, "Helvetica-Bold", size, right - left - 60)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", size)
    y = height - 314
    for line in lines[:2]:
        c.drawCentredString(cx, y, line)
        y -= size + 5

    # Barra degradada con los colores de la marca
    bar_w, bar_y = 470, y - 4
    c.saveState()
    path = c.beginPath()
    path.roundRect(cx - bar_w / 2, bar_y, bar_w, 6, 3)
    c.clipPath(path, stroke=0, fill=0)
    c.linearGradient(cx - bar_w / 2, bar_y, cx + bar_w / 2, bar_y, (NAVY, RED, GOLD), (0, 0.6, 1), extend=False)
    c.restoreState()

    issued = formats.date_format(timezone.localtime(certificate.issued_at), "j \\d\\e F \\d\\e Y")
    details = [f"Emitido el {issued}", f"Duración: {str(certificate.hours).rstrip('0').rstrip('.')} h"]
    if certificate.score is not None:
        details.insert(1, f"Calificación: {certificate.score}%")
    c.setFillColor(INK)
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(cx, bar_y - 22, "   •   ".join(details))

    # Firmas
    line_y = 96
    for x, (nombre, cargo, firma) in zip((cx - 150, cx + 150), settings.CAMPUS_SIGNERS):
        img = _image(Path(settings.MEDIA_ROOT) / firma)
        if img:
            # Como en papel: la firma pisa un poco la línea.
            _draw_fitted(c, img, x - 95, line_y - 8, 190, 92)
        c.setStrokeColor(NAVY)
        c.setLineWidth(0.7)
        c.line(x - 105, line_y, x + 105, line_y)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawCentredString(x, line_y - 15, nombre)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawCentredString(x, line_y - 28, cargo)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(x, line_y - 40, settings.CAMPUS_COMPANY)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf
