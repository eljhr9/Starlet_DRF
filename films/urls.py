from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('', views.MovieSearchViewSet.as_view()),                       # Поиск Фильмов
    path('parse/', views.MovieParser.as_view()),                        # Парсинг указанного кол-ва страниц на tmdb
    path('actors/', views.ActorSearchViewSet.as_view()),                # Поиск Людей
    path('collections/', views.CollectionListView.as_view()),           # Список Коллекций
    path('collection/<int:pk>/', views.CollectionDetailView.as_view()), # Детали Коллекции
    path('actor/<slug:slug>/', views.ActorDetailView.as_view()),        # Информация о Человеке
    path('genre/<slug:slug>/', views.GenreView.as_view()),              # Фильмы указанного Жанра
    path('translate/<slug:slug>/', views.MovieTranslateView.as_view()), # Перевод указанного Фильма
    path('<slug:slug>/', views.MovieDetailView.as_view()),              # Информация о Фильме
]
