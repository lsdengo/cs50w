from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>/", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("newpage/", views.newpage, name="newpage"),
    path("wiki/<str:title>/editpage/", views.editpage, name="editpage"),
    path("random/", views.random_page, name="random")
]
