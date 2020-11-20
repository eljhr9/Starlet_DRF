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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



class MovieSearchViewSet(APIView):
    """
    View for Search among Movies

    get:
        Return a list of matching movies.
    """

    @swagger_auto_schema(
        operation_id='movie_search',
        operation_summary='Search among movies',
        manual_parameters=[
            openapi.Parameter(
                name='search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Movie search query'
            )
        ],
        responses={200: serializers.MovieListSerializer(many=True)}
    )
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
                serializer = serializers.MovieListSerializer(movie_list, many=True, context={'request': request})
            except Exception as e:
                print(e)
                movies = Movie.objects.filter(
                    Q(translations__title__icontains=query) |
                    Q(orig_title__icontains=query)
                ).distinct()
                serializer = serializers.MovieListSerializer(movies, many=True, context={'request': request})
            return Response(serializer.data)



class ActorSearchViewSet(APIView):
    """
    View for Search for people

    get:
        Return a list of matching persons.
    """

    @swagger_auto_schema(
        operation_id='actor_search',
        operation_summary='Search among people',
        manual_parameters=[
            openapi.Parameter(
                name='search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Person search query'
            )
        ],
        responses={
            200: serializers.ActorListSerializer(many=True)
        }
    )
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
                serializer = serializers.ActorListSerializer(actors, many=True, context={'request': request})
            return Response(serializer.data)



class CollectionListView(APIView):
    """
    View for list of Collections

    get:
        Return all collections, ordered by most recently updated.
    """

    @swagger_auto_schema(
        operation_summary='Take list of collections',
        responses={200: serializers.CollectionListSerializer(many=True)}
    )
    def get(self, request):
        collections = Collection.objects.all()
        serializer = serializers.CollectionListSerializer(collections, many=True, context={'request': request})
        return Response(serializer.data)



class MovieDetailView(APIView):
    """
    View for requested Movie

    get:
        Return detail for requested movie.
    """

    @swagger_auto_schema(
        operation_id='movie_detail',
        operation_summary='Take detail about the movie',
        responses={200: serializers.MovieDetailSerializer()}
    )
    def get(self, request, slug):
        movie = Movie.objects.get(slug=slug)
        serializer = serializers.MovieDetailSerializer(movie, context={'request': request})
        return Response(serializer.data)



class CollectionDetailView(APIView):
    """
    View for requested Collection
    """

    @swagger_auto_schema(
        operation_id='collection_detail',
        operation_summary='Take detail about the collection',
        operation_description='Return detail for requested collection.',
        responses={200: serializers.CollectionDetailSerializer()}
    )
    def get(self, request, pk):
        collection = Collection.objects.get(id=pk)
        serializer = serializers.CollectionDetailSerializer(collection, context={'request': request})
        return Response(serializer.data)



class ActorDetailView(APIView):
    """
    View for requested Person

    get:
        Return detail for requested person.
    """

    @swagger_auto_schema(
        operation_id='actor_detail',
        operation_summary='Take detail about the person',
        responses={200: serializers.CollectionDetailSerializer()}
    )
    def get(self, request, slug):
        actor = Person.objects.get(translations__slug=slug)
        serializer = serializers.ActorDetailSerializer(actor, context={'request': request})
        return Response(serializer.data)



class GenreView(APIView):
    """
    View for requested Genre

    get:
        Return detail for requested genre and list of related movies.
    """

    @swagger_auto_schema(
        operation_id='genre_detail',
        operation_summary='Take detail about the genre',
        responses={200: serializers.GenreDetailSerializer()}
    )
    def get(self, request, slug):
        genre = Genre.objects.get(translations__slug=slug)
        serializer = serializers.GenreDetailSerializer(genre)
        return Response(serializer.data)



class MovieTranslateView(APIView):
    """
    View for translations of the requested movie

    get:
        Return translation of the requested movie.
    """

    @swagger_auto_schema(
        operation_id='movie_translate',
        operation_summary='Take translation to the movie',
        manual_parameters=[
            openapi.Parameter(
                name='language',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Language code in translation'
            )
        ],
        responses={200: serializers.MovieTranslateSerializer()}
    )
    def get(self, request, slug):
        language = request.query_params.get('language')
        movie = Movie.objects.get(slug=slug)
        translate = MovieTranslations.objects.get(language_code=language, movie=movie)
        serializer = serializers.MovieTranslateSerializer(translate, context={'request': request})
        return Response(serializer.data)



class MovieParser(APIView):
    """
    View for TMDB Movie parser

    post:
        Return a list of parsed movies and some detail about them.
    """

    @swagger_auto_schema(
        operation_id='movie_parser',
        operation_summary='Parse movies',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quantity': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Number of pages to parse.'),

            }
        ),
        responses={
            201: 'Detail about parsing',
            400: "Error: Quantity exceeds the maximum allowed value",
        }
    )
    def post(self, request):
        data = JSONParser().parse(request)
        quantity = data['quantity']
        if quantity > 500:
            return JsonResponse("Error: Quantity exceeds the maximum allowed value", status=400)
        else:
            detail = parse()
            return JsonResponse(detail, status=201)
