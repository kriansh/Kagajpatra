from django.contrib import admin
from django.urls import include, path

from nagarik.views import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lang/<str:code>/", set_language, name="set_language"),
    path("api/", include("assistant.urls")),
    path("", include("services.urls")),
]
