from rest_framework import serializers
from .models import Movie, Genre, People, Collection
from users.serializers import UserListSerializer



class ActorListSerializer(serializers.ModelSerializer):
    # Сериализация списка актеров

    class Meta:
        model = People
        fields = ('name', 'slug', 'photo')


class GenreSerializer(serializers.ModelSerializer):
    # Сериализация жанра

    class Meta:
        model = Genre
        fields = ('title', 'slug')


class MovieListSerializer(serializers.ModelSerializer):
    # Сериализация для списка фильмов
    poster = serializers.SerializerMethodField() # Удалить при подключениии AWS S3

    class Meta:
        model = Movie
        fields = ('ru_title', 'age_limit', 'imdb_rating', 'release_date', 'poster', 'slug')

    def get_poster(self, obj):
         # Удалить при подключениии AWS S3
        return self.context['request'].build_absolute_uri( obj.poster.url)


class GenreDetailSerializer(serializers.ModelSerializer):
    # Сериализация жанра
    movies = MovieListSerializer(many=True)

    class Meta:
        model = Genre
        fields = ('title', 'slug', 'movies')


class ActorDetailSerializer(serializers.ModelSerializer):
    # Сериализация страницы актера
    movie_cast = MovieListSerializer(many=True)

    class Meta:
        model = People
        fields = "__all__"


class MovieDetailSerializer(serializers.ModelSerializer):
    # Сериализация для страницы фильма
    get_cast = ActorListSerializer(many=True)
    directors = ActorListSerializer(many=True)
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = "__all__"


class CollectionListSerializer(serializers.ModelSerializer):
    # Сериализация для списка коллекций
    get_films = MovieListSerializer(many=True)

    class Meta:
        model = Collection
        fields = ('title', 'get_films', 'id')

class CollectionDetailSerializer(serializers.ModelSerializer):
    # Сериализация для страницы коллекции
    movies = MovieListSerializer(many=True)
    owner = UserListSerializer()

    class Meta:
        model = Collection
        fields = "__all__"
