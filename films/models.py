from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.conf import settings


class Movie(models.Model):
    """Информация о фильме"""
    orig_title = models.CharField(max_length=50, verbose_name='Оригинальное название')
    ru_title = models.CharField(max_length=50, verbose_name='Название на русском')
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    description = models.TextField(max_length=1500, null=True, blank=True, verbose_name='Краткое содержание')
    country = models.CharField(max_length=100, verbose_name='Страна')
    directors = models.ManyToManyField('People', related_name='movie_director',
        blank=True, verbose_name='Режиссер')
    age_limit = models.PositiveIntegerField(default=0, verbose_name='Возрастное ограничение')
    tagline = models.CharField(max_length=200, null=True, blank=True, verbose_name='Слоган')
    imdb_rating = models.DecimalField(max_digits=4, decimal_places=1,
                    validators=[MinValueValidator(0), MaxValueValidator(10)],
                                      default=0, verbose_name='Рейтинг IMDB')
    release_date = models.DateField(verbose_name='Дата выхода')
    duration = models.PositiveIntegerField(verbose_name='Длительность', null=True, blank=True)
    cast = models.ManyToManyField('People', related_name='movie_cast', blank=True,
                                  verbose_name='Актерский совстав')
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True,
                                   verbose_name='Жанр')
    poster = models.ImageField(upload_to='movie/posters/', verbose_name='Постер')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    # trailer

    # user_rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)],
    #                                   default=0, verbose_name='Рейтинг среди пользователей')
    class Meta:
        verbose_name_plural = 'Фильмы'
        verbose_name = 'Фильм'
        ordering = ['-updated']

    def __str__(self):
        return self.ru_title

    def get_cast(self):
        return self.cast.all()[:10]


class Genre(models.Model):
    """Жанр фильма"""
    title = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, db_index=True, unique=True)

    class Meta:
        verbose_name_plural = 'Жанр'
        verbose_name = 'Жанр'
        ordering = ['title']

    def __str__(self):
        return self.title


class People(models.Model):
    """Человек связанный с производством фильма например актер, оператор и т.д."""
    name = models.CharField(max_length=50, verbose_name='Полное имя')
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    photo = models.ImageField(upload_to='movie/actors/', null=True, blank=True, verbose_name='Фото')
    biography = models.TextField(max_length=1500, null=True, blank=True, verbose_name='Биография')
    career = models.CharField(max_length=100, verbose_name='Карьера')
    birth_date = models.DateField(verbose_name='Дата рождения')
    birth_place = models.CharField(max_length=50, verbose_name='Место рождения')

    class Meta:
        verbose_name_plural = 'Люди'
        verbose_name = 'Человек'
        ordering = ['name']

    def __str__(self):
        return self.name
        

class Collection(models.Model):
    """Коллекция фильмов"""
    title = models.CharField(max_length=50, verbose_name='Название колекции')
    movies = models.ManyToManyField(Movie, related_name='collections', verbose_name='Фильмы')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.DO_NOTHING, verbose_name='Автор')
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                        related_name='collections', verbose_name='Последователи')
    image = models.ImageField(upload_to='movie/collections/', null=True, blank=True, verbose_name='Изображение')

    class Meta:
        verbose_name_plural = 'Коллекции'
        verbose_name = 'Коллекция'
        ordering = ['-updated']

    def __str__(self):
        return self.title

    def get_films(self):
        return self.movies.all()[:8]
