from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import MovieSearchViewSet, ActorSearchViewSet


urlpatterns = [
    path('', MovieSearchViewSet.as_view()),
    path('actors/', ActorSearchViewSet.as_view()),
    path('collections/', views.CollectionListView.as_view()),
    path('collection/<int:pk>/', views.CollectionDetailView.as_view()),
    path('actor/<slug:slug>/', views.ActorDetailView.as_view()),
    path('genre/<slug:slug>/', views.GenreView.as_view()),
    path('<slug:slug>/', views.MovieDetailView.as_view()),
]
