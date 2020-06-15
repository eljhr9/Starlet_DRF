from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Movie, Genre, People, Collection
from . import serializers
from .document import MovieDocument


class MovieViewSet(APIView):
    def get(self, request):
        query = request.query_params.get('search')
        ids = []
        if query:
            try:
                s = MovieDocument.search()
                s = s.query('multi_match', query=query, fields=["orig_title", "ru_title"])
                response = s.execute()
                response_dict = response.to_dict()
                hits = response_dict['hits']['hits']
                ids = [hit['_source']['id'] for hit in hits]
                queryset = Movie.objects.filter(id__in=ids)
                movie_list = list(queryset)
                movie_list.sort(key=lambda movie: ids.index(movie.id))
                serializer = serializers.MovieListSerializer(movie_list, many=True, context={'request': request})
            except Exception as e:
                print(e)
                movies = Movie.objects.filter(
                    Q(ru_title__icontains=query) |
                    Q(orig_title__icontains=query)
                ).distinct()
                serializer = serializers.MovieListSerializer(movies, many=True, context={'request': request})
            return Response(serializer.data)


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
