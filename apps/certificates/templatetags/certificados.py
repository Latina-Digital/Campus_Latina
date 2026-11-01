"""Piezas del certificado en pantalla: el QR de verificación y las firmas."""
import re
from functools import lru_cache

from django import template
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.safestring import mark_safe
from reportlab.graphics import renderSVG
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

from ..views import public_url

register = template.Library()


@lru_cache(maxsize=256)
def _qr_svg(url):
    widget = QrCodeWidget(url)
    widget.barBorder = 0
    x0, y0, x1, y1 = widget.getBounds()
    drawing = Drawing(x1 - x0, y1 - y0)
    drawing.add(widget)
    svg = renderSVG.drawToString(drawing)
    svg = svg[svg.index("<svg"):]
    # Que ocupe el espacio que le dé el CSS.
    return re.sub(r'<svg([^>]*?) width="[^"]*" height="[^"]*"', r'<svg\1 width="100%" height="100%"', svg, count=1)


@register.simple_tag(takes_context=True)
def cert_qr(context, certificate):
    """QR que lleva a la página de verificación con el código del certificado."""
    return mark_safe(_qr_svg(public_url(context["request"], certificate.get_verify_path())))


@register.simple_tag
def cert_signers():
    return [
        {"nombre": nombre, "cargo": cargo, "url": default_storage.url(firma) if default_storage.exists(firma) else None}
        for nombre, cargo, firma in settings.CAMPUS_SIGNERS
    ]
