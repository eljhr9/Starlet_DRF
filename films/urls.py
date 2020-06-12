from django.urls import path, include
from . import views

app_name = 'movie'

urlpatterns = [
    path('', views.collections_list, name='list'),
    path('collection/<int:pk>/', views.collection_detail, name='collection'),
    path('<slug:film_slug>/', views.film_page, name='detail'),
    path('persona/<slug:person_slug>/', views.person_page, name='person_page'),
    path('genre/<slug:genre_slug>/', views.genre_page, name='genre_page'),
]
