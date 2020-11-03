from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from pytils.translit import slugify

from .document import MovieDocument, ActorDocument


class Movie(models.Model):
    """Информация о фильме"""
    orig_title = models.CharField(max_length=70, null=True, blank=True,
                                  verbose_name='Оригинальное название')
    ru_title = models.CharField(max_length=70, verbose_name='Название на русском')
    slug = models.SlugField(max_length=70, db_index=True, blank=True, unique=True)
    description = models.TextField(max_length=2500, null=True, blank=True,
                                   verbose_name='Краткое содержание')
    country = models.CharField(max_length=100, null=True, blank=True,
                               verbose_name='Страна')
    directors = models.ManyToManyField('Person', related_name='movie_director',
                                       blank=True, verbose_name='Режиссер')
    age_limit = models.CharField(max_length=10, default='0+', null=True, blank=True,
                                 verbose_name='Возрастное ограничение')
    tagline = models.CharField(max_length=200, null=True, blank=True,
                               verbose_name='Слоган')
    imdb_rating = models.DecimalField(max_digits=4, decimal_places=1,
                    validators=[MinValueValidator(0), MaxValueValidator(10)],
                    default=0, verbose_name='Рейтинг IMDB')
    release_date = models.DateField(null=True, blank=True,
                                    verbose_name='Дата выхода')
    duration = models.PositiveIntegerField(null=True, blank=True,
                                           verbose_name='Длительность')
    cast = models.ManyToManyField('Person', related_name='movie_cast', blank=True,
                                  verbose_name='Актерский совстав')
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True,
                                    verbose_name='Жанр')
    poster = models.ImageField(upload_to='movie/posters/', null=True, blank=True,
                               verbose_name='Постер')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    fullness = models.PositiveIntegerField(default=0, verbose_name='Полнота содержания',
                        validators=[MinValueValidator(0), MaxValueValidator(100)])

    # user_rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)],
    #                                   default=0, verbose_name='Рейтинг среди пользователей')
    class Meta:
        verbose_name_plural = 'Фильмы'
        verbose_name = 'Фильм'
        ordering = ['-updated']
        unique_together = [
            ('orig_title', 'ru_title', 'release_date'),
        ]

    def save(self, *args, **kwargs):
        super(Movie, self).save()
        self.slug = slugify(f'{self.id}-{self.ru_title}')
        super(Movie, self).save()

    def __str__(self):
        return self.ru_title

    def get_cast(self):
        return self.cast.all()[:8]

    def indexing(self):
        doc = MovieDocument(
            meta={'id': self.id},
            ru_title=self.ru_title,
            orig_title=self.orig_title,
            id=self.id
        )
        doc.save()
        return doc.to_dict(include_meta=True)


class Genre(models.Model):
    """Жанр фильма"""
    title = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, db_index=True, unique=True)

    class Meta:
        verbose_name_plural = 'Жанр'
        verbose_name = 'Жанр'
        ordering = ['title']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Genre, self).save()

    def __str__(self):
        return self.title


class Person(models.Model):
    """Человек связанный с производством фильма например актер, оператор и т.д."""

    GENDER_CHOICES = (
        ('Мужской', "Мужской"),
        ('Женский', "Женский"),
    )

    name = models.CharField(max_length=50, verbose_name='Полное имя')
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    photo = models.ImageField(upload_to='movie/actors/', null=True, blank=True,
                              verbose_name='Фото')
    biography = models.TextField(max_length=3000, null=True, blank=True,
                                 verbose_name='Биография')
    career = models.CharField(max_length=100, verbose_name='Карьера')
    gender = models.CharField(max_length=15, null=True, blank=True,
                              choices=GENDER_CHOICES, verbose_name='Пол')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    birth_place = models.CharField(max_length=50, null=True, blank=True,
                                   verbose_name='Место рождения')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name_plural = 'Люди'
        verbose_name = 'Человек'
        ordering = ['-updated']
        unique_together = [
            ('name', 'birth_date', 'birth_place'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Person, self).save()
        self.slug = slugify(f'{self.id}-{self.name}')
        super(Person, self).save()

    def indexing(self):
        doc = ActorDocument(
            meta={'id': self.id},
            name=self.name,
            slug=self.slug,
            id=self.id
        )
        doc.save()
        return doc.to_dict(include_meta=True)


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
