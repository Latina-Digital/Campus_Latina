from django.urls import path

from . import views

app_name = "panel"


def crud_urls(prefix, slug, views_tuple):
    lst, create, update, delete = views_tuple
    return [
        path(f"{slug}/", lst, name=f"{prefix}_list"),
        path(f"{slug}/nuevo/", create, name=f"{prefix}_create"),
        path(f"{slug}/<int:pk>/", update, name=f"{prefix}_edit"),
        path(f"{slug}/<int:pk>/eliminar/", delete, name=f"{prefix}_delete"),
    ]


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Usuarios
    path("usuarios/", views.UserList.as_view(), name="user_list"),
    path("usuarios/nuevo/", views.UserCreate.as_view(), name="user_create"),
    path("usuarios/<int:pk>/", views.UserUpdate.as_view(), name="user_edit"),
    path("usuarios/<int:pk>/eliminar/", views.UserDelete.as_view(), name="user_delete"),
    path("usuarios/importar/", views.user_import, name="user_import"),
    path("usuarios/plantilla.csv", views.user_template, name="user_template"),
    # Cursos
    path("cursos/", views.CourseList.as_view(), name="course_list"),
    path("cursos/nuevo/", views.CourseCreate.as_view(), name="course_create"),
    path("cursos/<int:pk>/", views.course_builder, name="course_builder"),
    path("cursos/<int:pk>/editar/", views.CourseUpdate.as_view(), name="course_edit"),
    path("cursos/<int:pk>/eliminar/", views.CourseDelete.as_view(), name="course_delete"),
    path("cursos/<int:course_pk>/lecciones/nueva/", views.lesson_form, name="lesson_create"),
    path("cursos/<int:course_pk>/lecciones/<int:pk>/", views.lesson_form, name="lesson_edit"),
    path("cursos/<int:course_pk>/preguntas/", views.questions, name="questions"),
    path("modulos/<int:pk>/", views.module_edit, name="module_edit"),
    path("ordenar/<str:kind>/<int:pk>/", views.reorder, name="reorder"),
    path("materiales/<int:pk>/eliminar/", views.resource_delete, name="resource_delete"),
    path("preguntas/<int:pk>/", views.question_edit, name="question_edit"),
    path("preguntas/plantilla.csv", views.question_template, name="question_template"),
    # Rutas
    path("rutas/", views.PathList.as_view(), name="path_list"),
    path("rutas/nueva/", views.path_form, name="path_create"),
    path("rutas/<int:pk>/", views.path_form, name="path_edit"),
    path("rutas/<int:pk>/eliminar/", views.PathDelete.as_view(), name="path_delete"),
    # Resultados y certificados
    path("resultados/", views.results, name="results"),
    path("resultados/<int:pk>/informe/", views.attempt_report, name="attempt_report"),
    path("certificados/", views.certificates, name="certificates"),
    path("certificados/<int:pk>/estado/", views.certificate_toggle, name="certificate_toggle"),
]
urlpatterns += crud_urls("category", "categorias", views.category_views)
urlpatterns += crud_urls("line", "lineas", views.line_views)
urlpatterns += crud_urls("product", "productos", views.product_views)
urlpatterns += crud_urls("announcement", "anuncios", views.announcement_views)
