from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search_daily/<str:ticker>", views.search_daily, name="search_daily"),
]
