from django.urls import path

from . import views

app_name = "backoffice"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("lager/", views.stock_list, name="stock_list"),
    path("bestellung/<int:order_id>/", views.order_detail, name="order_detail"),
    path("bestellung/<int:order_id>/status/", views.order_set_status, name="order_set_status"),
]
