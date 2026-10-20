from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.core.utils import format_minutes

register = template.Library()

BRAND_CLASSES = {"latina": "brand-latina", "induless": "brand-induless", "corporativo": "brand-corp"}
BRAND_LABELS = {"latina": "Industrial Latina", "induless": "Induless", "corporativo": "Corporativo"}


@register.simple_tag
def brand_badge(brand):
    return format_html('<span class="brand-badge {}">{}</span>', BRAND_CLASSES.get(brand, ""), BRAND_LABELS.get(brand, brand))


@register.simple_tag
def icon(name, size=18, extra=""):
    return format_html('<i data-lucide="{}" class="icon {}" style="width:{}px;height:{}px" aria-hidden="true"></i>', name, extra, size, size)


@register.simple_tag
def stars(value, size=14):
    value = float(value or 0)
    out = []
    for i in range(1, 6):
        cls = "on" if value >= i - 0.25 else ("half" if value >= i - 0.75 else "")
        out.append(f'<span class="star {cls}" style="font-size:{int(size)}px">★</span>')
    return mark_safe('<span class="stars" aria-label="%.1f de 5">%s</span>' % (value, "".join(out)))


@register.filter
def minutes(value):
    return format_minutes(value)


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None


WIDE_WIDGETS = {"textarea", "checkboxselectmultiple", "clearablefile", "file", "selectmultiple"}


@register.filter
def is_wide(bound_field):
    """Campos que ocupan las dos columnas del formulario."""
    return bound_field.widget_type in WIDE_WIDGETS or bound_field.name in {"summary", "body", "title"}


@register.simple_tag(takes_context=True)
def query_replace(context, **kwargs):
    """Conserva los filtros GET al paginar: ?{% query_replace page=2 %}"""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    return query.urlencode()


@register.simple_tag
def avatar(user, size=40, extra=""):
    if getattr(user, "avatar", None):
        return format_html(
            '<img class="avatar {}" src="{}" alt="{}" style="width:{}px;height:{}px">', extra, user.avatar.url, user.display_name, size, size
        )
    return format_html(
        '<span class="avatar avatar-initials {}" style="width:{}px;height:{}px;font-size:{}px" aria-hidden="true">{}</span>',
        extra, size, size, max(11, int(size * 0.38)), user.initials,
    )
