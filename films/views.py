from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Movie, Genre, People, Collection
from . import serializers


class CollectionListView(APIView):
    # Представление списка коллекций
    def get(self, request):
        collections = Collection.objects.all()
        serializer = serializers.CollectionListSerializer(collections, many=True, context={'request': request})
        return Response(serializer.data)


class MovieDetailView(APIView):
    # Представление страницы фильма
    def get(self, request, slug):
        movie = Movie.objects.get(slug=slug)
        serializer = serializers.MovieDetailSerializer(movie, context={'request': request})
        return Response(serializer.data)


class CollectionDetailView(APIView):
    # Представление страницы коллекции
    def get(self, request, pk):
        collection = Collection.objects.get(id=pk)
        serializer = serializers.CollectionDetailSerializer(collection, context={'request': request})
        return Response(serializer.data)


class ActorDetailView(APIView):
    # Представление страницы актера
    def get(self, request, slug):
        actor = People.objects.get(slug=slug)
        serializer = serializers.ActorDetailSerializer(actor, context={'request': request})
        return Response(serializer.data)


class GenreView(APIView):
    # Представление страницы актера
    def get(self, request, slug):
        genre = Genre.objects.get(slug=slug)
        serializer = serializers.GenreDetailSerializer(genre, context={'request': request})
        return Response(serializer.data)
