from django.contrib import admin
from .models import Movie, Genre, Person, Collection, MovieTranslations
from parler.admin import TranslatableAdmin


class MovieTranslationsAdmin(admin.TabularInline):
    model = MovieTranslations


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('orig_title', 'updated', 'imdb_rating', 'release_date', 'age_limit')
    list_display_links = ('orig_title',)
    # search_fields = ('orig_title', 'ru_title', 'description', 'tagline')
    list_editable = ['imdb_rating']
    inlines = [MovieTranslationsAdmin,]


@admin.register(Genre)
class GenreAdmin(TranslatableAdmin):
    list_display = ['title', 'slug']

    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('title',)
        }


@admin.register(Person)
class PersonAdmin(TranslatableAdmin):
    list_display = ['name', 'slug', 'career']

    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
	list_display = ['title', 'updated', 'created', 'owner']
