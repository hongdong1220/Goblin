from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api_stock_price/<str:ticker>",
         views.api_stock_price, name="api_stock_price"),
]
