from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("mix/<int:blend_id>/", views.blend_detail, name="blend_detail"),
    path("konfigurator/", views.configurator, name="configurator"),
    path("konfigurator/vorschau/", views.configurator_summary, name="configurator_summary"),
]
