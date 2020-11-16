from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .parser import parse
from . import serializers
from .models import Movie, Genre, Person, Collection, MovieTranslations
from .documents import MovieDocument, ActorDocument
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.generic import UpdateView



class MovieSearchViewSet(APIView):
    # Представление для поиска Фильмов
    def get(self, request):
        query = request.query_params.get('search')
        ids = []
        if query:
            try:
                s = MovieDocument.search()
                s = s.query('multi_match', query=query, fields=["orig_title", "translations"])
                response = s.execute()
                response_dict = response.to_dict()
                hits = response_dict['hits']['hits']
                ids = [hit['_source']['id'] for hit in hits]
                try:
                    quantity = int(request.query_params.get('q'))
                    queryset = Movie.objects.filter(id__in=ids)[:quantity]
                except:
                    queryset = Movie.objects.filter(id__in=ids)
                movie_list = list(queryset)
                movie_list.sort(key=lambda movie: ids.index(movie.id))
                serializer = serializers.MovieListSerializer(movie_list, many=True)
            except Exception as e:
                print(e)
                movies = Movie.objects.filter(
                    Q(translations__title__icontains=query) |
                    Q(orig_title__icontains=query)
                ).distinct()
                serializer = serializers.MovieListSerializer(movies, many=True)
            return Response(serializer.data)


class ActorSearchViewSet(APIView):
    # Представление для поиска Людей
    def get(self, request):
        query = request.query_params.get('search')
        ids = []
        if query:
            try:
                s = ActorDocument.search()
                s = s.query('multi_match', query=query, fields=["name",])
                response = s.execute()
                response_dict = response.to_dict()
                hits = response_dict['hits']['hits']
                ids = [hit['_source']['id'] for hit in hits]
                try:
                    quantity = int(request.query_params.get('q'))
                    queryset = Person.objects.filter(id__in=ids)[:quantity]
                except:
                    queryset = Person.objects.filter(id__in=ids)
                actor_list = list(queryset)
                actor_list.sort(key=lambda actor: ids.index(actor.id))
                serializer = serializers.ActorListSerializer(actor_list, many=True)
            except Exception as e:
                print(e)
                actors = Person.objects.filter(translations__name__icontains=query)
                serializer = serializers.ActorListSerializer(actors, many=True)
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
        serializer = serializers.MovieDetailSerializer(movie)
        return Response(serializer.data)


class CollectionDetailView(APIView):
    # Представление страницы коллекции
    def get(self, request, pk):
        collection = Collection.objects.get(id=pk)
        serializer = serializers.CollectionDetailSerializer(collection)
        return Response(serializer.data)


class ActorDetailView(APIView):
    # Представление страницы актера
    def get(self, request, slug):
        actor = Person.objects.get(translations__slug=slug)
        serializer = serializers.ActorDetailSerializer(actor)
        return Response(serializer.data)


class GenreView(APIView):
    # Представление страницы актера
    def get(self, request, slug):
        genre = Genre.objects.get(translations__slug=slug)
        serializer = serializers.GenreDetailSerializer(genre)
        return Response(serializer.data)


class MovieTranslateView(APIView):
    # Представление страницы актера
    def get(self, request, slug):
        language = request.query_params.get('language')
        movie = Movie.objects.get(slug=slug)
        translate = MovieTranslations.objects.get(language_code=language, movie=movie)
        serializer = serializers.MovieTranslateSerializer(translate)
        return Response(serializer.data)


class MovieParser(APIView):
    # Парсит запрошенное кол-во страниц
    def post(self, request):
        data = JSONParser().parse(request)
        detail = parse(data['quantity'])
        return JsonResponse(detail, status=201)
