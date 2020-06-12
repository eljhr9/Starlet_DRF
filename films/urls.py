from django.urls import path
from . import views


urlpatterns = [
    path('collections/', views.CollectionListView.as_view()),
    path('collection/<int:pk>/', views.CollectionDetailView.as_view()),
    path('actor/<slug:slug>/', views.ActorDetailView.as_view()),
    path('genre/<slug:slug>/', views.GenreView.as_view()),
    path('<slug:slug>/', views.MovieDetailView.as_view()),
]
