"""Certificado en PDF (A4 horizontal) con la identidad de Industrial Latina y código QR de verificación."""
import io
from functools import lru_cache

from django.conf import settings
from django.utils import formats, timezone
from PIL import Image
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

NAVY = HexColor("#0A1C40")
BLUE = HexColor("#12408F")
RED = HexColor("#E3000F")
GOLD = HexColor("#FACC00")
GOLD_DARK = HexColor("#C9A200")
INK = HexColor("#1F2937")
MUTED = HexColor("#6B7280")

IMG_DIR = settings.BASE_DIR / "static" / "img"


@lru_cache(maxsize=1)
def _watermark():
    mark = Image.open(IMG_DIR / "logo-mark.png").convert("RGBA")
    alpha = mark.getchannel("A").point(lambda a: int(a * 0.06))
    mark.putalpha(alpha)
    buf = io.BytesIO()
    mark.save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf)


def _fit_text(c, text, font, size, max_width, min_size=12):
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 1
    return size


def render_certificate(certificate, verify_url):
    buf = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setTitle(f"Certificado {certificate.code}")
    c.setAuthor(settings.CAMPUS_COMPANY)
    c.setSubject(certificate.course_title)

    # Fondo y marcos
    c.setFillColor(HexColor("#FBFBFD"))
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(white)
    c.rect(14, 14, width - 28, height - 28, stroke=0, fill=1)
    c.setStrokeColor(RED)
    c.setLineWidth(1.4)
    c.rect(24, 24, width - 48, height - 48, stroke=1, fill=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.rect(29, 29, width - 58, height - 58, stroke=1, fill=0)

    # Franja tricolor inferior (identidad Latina)
    band_w = (width - 58) / 3
    for i, color in enumerate((NAVY, RED, GOLD)):
        c.setFillColor(color)
        c.rect(29 + i * band_w, 29, band_w, 6, stroke=0, fill=1)

    # Marca de agua
    wm = 330
    c.drawImage(_watermark(), (width - wm * 0.68) / 2, (height - wm) / 2 - 10, wm * 0.68, wm, mask="auto")

    # Logo y código
    logo = ImageReader(str(IMG_DIR / "logo-latina.png"))
    lw, lh = logo.getSize()
    logo_h = 54
    c.drawImage(logo, 56, height - 56 - logo_h, logo_h * lw / lh, logo_h, mask="auto")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MUTED)
    c.drawRightString(width - 56, height - 64, "CÓDIGO DE VERIFICACIÓN")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NAVY)
    c.drawRightString(width - 56, height - 79, certificate.code)

    cx = width / 2
    # Títulos
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(cx, height - 168, "CERTIFICADO")
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, height - 190, "D E   A P R O B A C I Ó N")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, height - 228, f"{settings.CAMPUS_COMPANY}, a través de {settings.CAMPUS_NAME}, certifica que")

    # Nombre
    name = certificate.holder_name
    size = _fit_text(c, name, "Times-BoldItalic", 40, width - 200)
    c.setFillColor(INK)
    c.setFont("Times-BoldItalic", size)
    c.drawCentredString(cx, height - 278, name)
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(1.2)
    c.line(cx - 210, height - 292, cx + 210, height - 292)

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, height - 318, "aprobó satisfactoriamente el curso")
    title = certificate.course_title
    size = _fit_text(c, title, "Helvetica-Bold", 24, width - 220)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", size)
    c.drawCentredString(cx, height - 350, title)

    issued = formats.date_format(timezone.localtime(certificate.issued_at), "j \\d\\e F \\d\\e Y")
    details = [f"Emitido el {issued}", f"Duración: {str(certificate.hours).rstrip('0').rstrip('.')} h"]
    if certificate.score is not None:
        details.insert(1, f"Calificación: {certificate.score}%")
    c.setFillColor(INK)
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, height - 378, "   •   ".join(details))

    # Firmas
    sig_y = 112
    for x, label in ((cx - 190, settings.CAMPUS_SIGNER_1), (cx + 190, settings.CAMPUS_SIGNER_2)):
        c.setStrokeColor(NAVY)
        c.setLineWidth(0.8)
        c.line(x - 105, sig_y, x + 105, sig_y)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawCentredString(x, sig_y - 15, label)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(x, sig_y - 28, settings.CAMPUS_COMPANY)

    # Sello
    seal_x, seal_y, r = 104, 112, 36
    c.setFillColor(GOLD)
    c.circle(seal_x, seal_y, r, stroke=0, fill=1)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2.2)
    c.circle(seal_x, seal_y, r - 5, stroke=1, fill=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(seal_x, seal_y + 8, "CAMPUS")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(seal_x, seal_y - 4, "LATINA")
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(seal_x, seal_y - 15, f"{timezone.localtime(certificate.issued_at):%Y}")
    c.setFillColor(RED)
    p = c.beginPath()
    p.moveTo(seal_x - 20, seal_y - r + 6); p.lineTo(seal_x - 30, seal_y - r - 26); p.lineTo(seal_x - 18, seal_y - r - 20)
    p.lineTo(seal_x - 8, seal_y - r - 30); p.lineTo(seal_x - 4, seal_y - r + 2); p.close()
    c.drawPath(p, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(seal_x + 20, seal_y - r + 6); p.lineTo(seal_x + 30, seal_y - r - 26); p.lineTo(seal_x + 18, seal_y - r - 20)
    p.lineTo(seal_x + 8, seal_y - r - 30); p.lineTo(seal_x + 4, seal_y - r + 2); p.close()
    c.drawPath(p, stroke=0, fill=1)

    # QR de verificación
    qr_size = 78
    widget = QrCodeWidget(verify_url)
    x0, y0, x1, y1 = widget.getBounds()
    drawing = Drawing(qr_size, qr_size, transform=[qr_size / (x1 - x0), 0, 0, qr_size / (y1 - y0), 0, 0])
    drawing.add(widget)
    qr_x = width - 56 - qr_size
    renderPDF.draw(drawing, c, qr_x, 70)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawCentredString(qr_x + qr_size / 2, 60, "Escanea para verificar")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf
