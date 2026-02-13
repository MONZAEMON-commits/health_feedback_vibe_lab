from django.urls import path

from . import views

app_name = "conditions"

urlpatterns = [
    path("input/", views.input_view, name="input"),
    path("submit/", views.submit_view, name="submit"),
    path("history/", views.history_view, name="history"),
]
