from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search_daily",
         views.search_daily_view, name="search_daily"),

    # Grabs data
    path("api_search_daily/<str:ticker>",
         views.api_search_daily, name="api_search_daily"),
]
