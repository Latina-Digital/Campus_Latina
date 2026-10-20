from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.home, name="home"),
    path("explorar/", views.explore, name="explore"),
    path("mi-aprendizaje/", views.my_learning, name="my_learning"),
    path("rutas/", views.paths, name="paths"),
    path("rutas/<slug:slug>/", views.path_detail, name="path_detail"),
    path("curso/<slug:slug>/", views.course_detail, name="detail"),
    path("curso/<slug:slug>/comenzar/", views.course_start, name="start"),
    path("curso/<slug:slug>/guardar/", views.toggle_save, name="toggle_save"),
    path("curso/<slug:slug>/resena/", views.review_submit, name="review"),
    path("curso/<slug:slug>/leccion/<int:lesson_id>/", views.lesson_view, name="lesson"),
    path("leccion/<int:lesson_id>/completar/", views.lesson_complete, name="lesson_complete"),
    path("leccion/<int:lesson_id>/posicion/", views.lesson_position, name="lesson_position"),
]
