from django.urls import path

from . import views

app_name = "assistant"

urlpatterns = [
    path("ask/", views.ask_view, name="ask"),
    path("ask/stream/", views.ask_stream_view, name="ask_stream"),
]
