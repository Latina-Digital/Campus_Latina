from django import forms


class StyledFormMixin:
    """Aplica las clases del sistema de diseño a todos los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                css = "checkbox"
            elif isinstance(widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                css = "choice-list"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = "input select"
            elif isinstance(widget, forms.ClearableFileInput) or isinstance(widget, forms.FileInput):
                css = "input file"
            elif isinstance(widget, forms.Textarea):
                css = "input textarea"
                widget.attrs.setdefault("rows", 4)
            else:
                css = "input"
            widget.attrs["class"] = (widget.attrs.get("class", "") + " " + css).strip()
            if field.required and not isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("required", True)
