from rest_framework import serializers
from .models import Movie, Genre, Person, Collection, MovieTranslations
from users.serializers import UserListSerializer



class ActorListSerializer(serializers.ModelSerializer):
    # Сериализация списка актеров

    class Meta:
        model = Person
        fields = ('name', 'slug', 'photo')


class GenreSerializer(serializers.ModelSerializer):
    # Сериализация жанра

    class Meta:
        model = Genre
        fields = ('title', 'slug')


class TranslateDetailSerializer(serializers.Serializer):
    # Сериализация информации о языке
    bidi = serializers.BooleanField()
    code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=20)
    name_local = serializers.CharField(max_length=20)
    name_translated = serializers.CharField(max_length=20)


class AvailableTranslations(serializers.ModelSerializer):
    # Сериализация доступных переводов фильма
     translate_detail = TranslateDetailSerializer()

     class Meta:
         model = MovieTranslations
         fields = ('language_code', 'translate_detail')


class MovieTranslateSerializer(serializers.ModelSerializer):
    # Сериализация перевода для фильма
    translate_detail = TranslateDetailSerializer()

    class Meta:
        model = MovieTranslations
        fields = "__all__"


class MovieListSerializer(serializers.ModelSerializer):
    # Сериализация для списка фильмов
    get_translate = MovieTranslateSerializer()

    class Meta:
        model = Movie
        fields = ('orig_title', 'slug', 'age_limit', 'imdb_rating', 'release_date', 'get_translate')


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
        model = Person
        fields = ('name', 'slug', 'photo', 'birth_date', 'career', 'gender',
                  'biography', 'birth_place', 'movie_cast')


class MovieDetailSerializer(serializers.ModelSerializer):
    # Сериализация для страницы фильма
    get_cast = ActorListSerializer(many=True)
    directors = ActorListSerializer(many=True)
    genres = GenreSerializer(many=True)
    get_translate = MovieTranslateSerializer()
    get_available_translations = AvailableTranslations(many=True)

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
