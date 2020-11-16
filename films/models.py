from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from pytils.translit import slugify
from .documents import MovieDocument, ActorDocument
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import get_language, get_language_info
from django.utils.translation import gettext_lazy as _


class Movie(models.Model):
    """Информация о фильме"""
    orig_title = models.CharField(max_length=70, verbose_name=_('Оригинальное название'))
    slug = models.SlugField(max_length=70, db_index=True, blank=True, unique=True)
    directors = models.ManyToManyField('Person', related_name='movie_director',
                                       blank=True, verbose_name=_('Режиссеры'))
    age_limit = models.CharField(max_length=10, default='0+', null=True, blank=True,
                                 verbose_name=_('Возрастное ограничение'))
    imdb_rating = models.DecimalField(max_digits=4, decimal_places=1,
                    validators=[MinValueValidator(0), MaxValueValidator(10)],
                    default=0, verbose_name=_('Рейтинг IMDB'))
    release_date = models.DateField(null=True, blank=True,
                                    verbose_name=_('Дата выхода'))
    duration = models.PositiveIntegerField(null=True, blank=True,
                                           verbose_name=_('Длительность'))
    cast = models.ManyToManyField('Person', related_name='movie_cast', blank=True,
                                  verbose_name=_('Актерский совстав'))
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True,
                                    verbose_name=_('Жанр'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    fullness = models.PositiveIntegerField(default=0, verbose_name=_('Полнота содержания'),
                        validators=[MinValueValidator(0), MaxValueValidator(100)])

    # rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)],
    #                                   default=0, verbose_name='Рейтинг среди пользователей')
    class Meta:
        verbose_name_plural = _('Фильмы')
        verbose_name = _('Фильм')
        ordering = ['-updated']
        unique_together = [
            ('orig_title', 'release_date'),
        ]

    def save(self, *args, **kwargs):
        super(Movie, self).save()
        self.slug = slugify(f'{self.id}-{self.orig_title}')
        super(Movie, self).save()

    def __str__(self):
        return self.orig_title

    def get_cast(self):
        return self.cast.all()[:8]

    def get_translate(self):
        return self.translations.get(language_code=get_language())

    def get_available_translations(self):
        return self.translations.all()

    def indexing(self):
        doc = MovieDocument(
            meta={'id': self.id},
            translations=[t.title for t in self.translations.all()],
            orig_title=self.orig_title,
            id=self.id
        )
        doc.save()
        return doc.to_dict(include_meta=True)


class MovieTranslations(models.Model):
    """Переводы для фильмов"""
    language_code = models.CharField(max_length=3, verbose_name=_('Языковой код'))
    movie = models.ForeignKey(Movie, related_name='translations', on_delete=models.CASCADE, verbose_name=_('Фильм'))
    title = models.CharField(max_length=70, verbose_name=_('Название'))
    description = models.TextField(max_length=2500, null=True, blank=True,
                                       verbose_name=_('Краткое содержание'))
    country = models.CharField(max_length=100, null=True, blank=True,
                                   verbose_name=_('Страна'))
    tagline = models.CharField(max_length=200, null=True, blank=True,
                                   verbose_name=_('Слоган'))
    poster = models.ImageField(upload_to='movie/posters/', null=True, blank=True,
                                   verbose_name=_('Постер'))

    class Meta:
        verbose_name_plural = _('Первеводы фильмов')
        verbose_name = _('Первеводы фильма')
        ordering = ['movie']
        unique_together = [
            ('movie', 'language_code'),
        ]

    def __str__(self):
        return self.title

    def translate_detail(self):
        return get_language_info(self.language_code)


class Genre(TranslatableModel):
    """Жанр фильма"""
    translations = TranslatedFields(
          title = models.CharField(max_length=50),
          slug = models.SlugField(max_length=50, db_index=True)
    )

    class Meta:
        verbose_name_plural = _('Жанр')
        verbose_name = _('Жанр')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Genre, self).save()


class Person(TranslatableModel):
    """Человек связанный с производством фильма например актер, оператор и т.д."""
    translations = TranslatedFields(
        name = models.CharField(max_length=50, verbose_name=_('Полное имя')),
        slug = models.SlugField(max_length=50, db_index=True),
        career = models.CharField(max_length=100, verbose_name=_('Карьера')),
        gender = models.CharField(max_length=15, null=True, blank=True,
                                  verbose_name=_('Пол')),
        biography = models.TextField(max_length=3000, null=True, blank=True,
                                     verbose_name=_('Биография')),
        birth_place = models.CharField(max_length=50, null=True, blank=True,
                                       verbose_name=_('Место рождения'))
    )
    photo = models.ImageField(upload_to='movie/actors/', null=True, blank=True,
                              verbose_name=_('Фото'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('Дата рождения'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name_plural = _('Люди')
        verbose_name = _('Человек')
        ordering = ['-updated']
        unique_together = [
            ('photo', 'birth_date'),
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
            name=[t.name for t in self.translations.all()],
            id=self.id
        )
        doc.save()
        return doc.to_dict(include_meta=True)


class Collection(models.Model):
    """Коллекция фильмов"""
    title = models.CharField(max_length=50, verbose_name=_('Название колекции'))
    movies = models.ManyToManyField(Movie, related_name='collections', verbose_name=_('Фильмы'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.DO_NOTHING, verbose_name=_('Автор'))
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                        related_name='collections', verbose_name=_('Последователи'))
    image = models.ImageField(upload_to='movie/collections/', null=True, blank=True, verbose_name=_('Изображение'))

    class Meta:
        verbose_name_plural = _('Коллекции')
        verbose_name = _('Коллекция')
        ordering = ['-updated']

    def __str__(self):
        return self.title

    def get_films(self):
        return self.movies.all()[:8]
