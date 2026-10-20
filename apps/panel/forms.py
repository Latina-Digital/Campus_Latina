from django import forms
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import User
from apps.assessments.models import Quiz
from apps.catalog.models import Product, ProductLine
from apps.core.forms import StyledFormMixin
from apps.core.models import Announcement
from apps.courses.models import Category, Course, LearningPath, Lesson, Module, PathStep, Resource


class UserForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Contraseña", required=False, widget=forms.TextInput(attrs={"autocomplete": "new-password"}),
        help_text="Déjala vacía para no cambiarla.",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "role", "supervisor", "area", "city", "headline", "is_active"]
        labels = {"first_name": "Nombres", "last_name": "Apellidos", "username": "Usuario (login)", "email": "Correo", "is_active": "Cuenta activa"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["username"].help_text = ""
        self.fields["supervisor"].widget.attrs["list"] = "supervisores"
        if not self.instance.pk:
            self.fields["password"].required = True
            self.fields["password"].help_text = "Mínimo 6 caracteres. Compártela con el usuario de forma segura."
            self.fields["password"].widget.attrs["required"] = True

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
            user.origin = User.Origin.LOCAL
        if commit:
            user.save()
        return user


class ImportFileForm(StyledFormMixin, forms.Form):
    file = forms.FileField(label="Archivo", help_text="Excel (.xlsx) o CSV.")


class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "icon", "order"]


class CourseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title", "summary", "brand", "category", "level", "description", "outcomes", "cover",
            "instructor_name", "instructor_title", "related_products", "is_published", "is_featured", "is_mandatory", "order",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "outcomes": forms.Textarea(attrs={"rows": 5, "placeholder": "Identificar las diferencias entre…\nRecomendar el producto ideal para…"}),
            "related_products": forms.CheckboxSelectMultiple,
        }


class ModuleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title", "description", "order"]


class LessonForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["module", "title", "kind", "duration_minutes", "video", "youtube_url", "document", "content", "require_full_watch", "order"]
        widgets = {"content": forms.Textarea(attrs={"rows": 10, "data-rich-editor": "1"})}

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        if course:
            self.fields["module"].queryset = course.modules.all()
        self.fields["kind"].widget.attrs["x-model"] = "kind"

    def clean(self):
        data = super().clean()
        kind = data.get("kind")
        if kind == Lesson.Kind.VIDEO and not (data.get("video") or self.instance.video):
            self.add_error("video", "Sube el archivo de video.")
        if kind == Lesson.Kind.YOUTUBE and not data.get("youtube_url"):
            self.add_error("youtube_url", "Pega el enlace del video de YouTube.")
        if kind == Lesson.Kind.DOCUMENTO and not (data.get("document") or self.instance.document):
            self.add_error("document", "Sube el documento PDF.")
        if kind == Lesson.Kind.LECTURA and not data.get("content"):
            self.add_error("content", "Escribe el contenido de la lectura.")
        return data


class ResourceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["title", "file", "url"]

    def clean(self):
        data = super().clean()
        if not data.get("file") and not data.get("url"):
            raise forms.ValidationError("Sube un archivo o escribe un enlace.")
        return data


class QuizForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "instructions", "time_limit_minutes", "questions_per_attempt", "passing_score", "max_attempts", "show_review"]
        widgets = {"instructions": forms.Textarea(attrs={"rows": 3})}


class QuestionForm(StyledFormMixin, forms.Form):
    MAX_CHOICES = 6
    text = forms.CharField(label="Pregunta", widget=forms.Textarea(attrs={"rows": 2}))
    explanation = forms.CharField(label="Explicación (opcional)", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    correct = forms.TypedChoiceField(
        label="Respuesta correcta", coerce=int, choices=[(i, f"Opción {'ABCDEF'[i]}") for i in range(MAX_CHOICES)]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(self.MAX_CHOICES):
            field = forms.CharField(label=f"Opción {'ABCDEF'[i]}", required=i < 2, max_length=400)
            field.widget.attrs.update({"class": "input", "placeholder": "Opcional" if i >= 2 else ""})
            self.fields[f"choice_{i}"] = field

    @property
    def choice_fields(self):
        return [self[f"choice_{i}"] for i in range(self.MAX_CHOICES)]

    def clean(self):
        data = super().clean()
        correct = data.get("correct")
        if correct is not None and not data.get(f"choice_{correct}"):
            self.add_error("correct", "La opción marcada como correcta está vacía.")
        return data

    def choices(self):
        return [
            (self.cleaned_data[f"choice_{i}"], i == self.cleaned_data["correct"])
            for i in range(self.MAX_CHOICES)
            if self.cleaned_data.get(f"choice_{i}")
        ]


class QuestionImportForm(StyledFormMixin, forms.Form):
    file = forms.FileField(label="Archivo", required=False, help_text="Word (.docx), Excel (.xlsx), CSV o texto (.txt).")
    text = forms.CharField(label="…o pega las preguntas", required=False, widget=forms.Textarea(attrs={"rows": 8}))
    replace = forms.BooleanField(label="Reemplazar el banco actual", required=False)

    def clean(self):
        data = super().clean()
        if not data.get("file") and not data.get("text", "").strip():
            raise forms.ValidationError("Sube un archivo o pega el texto de las preguntas.")
        return data


class PathForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ["title", "summary", "description", "brand", "cover", "is_published", "order"]


PathStepFormSet = forms.inlineformset_factory(
    LearningPath, PathStep, fields=["course", "order"], extra=3, can_delete=True,
)


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "brand", "line", "summary", "description", "features", "uses", "presentations", "image", "datasheet", "is_active", "order"]
        widgets = {"features": forms.Textarea(attrs={"rows": 4}), "uses": forms.Textarea(attrs={"rows": 3})}


class ProductLineForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProductLine
        fields = ["name", "icon", "order"]


class AnnouncementForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "body", "tone", "link_url", "link_label", "is_active"]
