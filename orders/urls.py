from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("warenkorb/", views.cart_detail, name="cart"),
    path("warenkorb/hinzufuegen/<int:blend_id>/", views.cart_add, name="cart_add"),
    path("warenkorb/menge/<int:blend_id>/<str:size>/", views.cart_update, name="cart_update"),
    path("warenkorb/entfernen/<int:blend_id>/<str:size>/", views.cart_remove, name="cart_remove"),
    path("kasse/", views.checkout, name="checkout"),
    path("bestellung/<int:order_id>/", views.confirmation, name="confirmation"),
]
