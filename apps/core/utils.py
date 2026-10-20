from django.utils.text import slugify


def unique_slug(instance, value, field="slug", max_length=80):
    """Genera un slug único para `instance` a partir de `value`."""
    base = slugify(value)[:max_length] or "item"
    slug = base
    model = type(instance)
    n = 2
    while model.objects.filter(**{field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


def format_minutes(minutes):
    minutes = int(minutes or 0)
    if minutes < 60:
        return f"{minutes} min"
    h, m = divmod(minutes, 60)
    return f"{h} h {m} min" if m else f"{h} h"
