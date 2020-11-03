from django.contrib import admin
from .models import Movie, Genre, Person, Collection


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
	list_display = ('ru_title', 'updated', 'imdb_rating', 'release_date', 'age_limit')
	list_display_links = ('ru_title',)
	search_fields = ('orig_title', 'ru_title', 'description', 'tagline')
	list_editable = ['imdb_rating']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug']
	prepopulated_fields = {'slug': ('title',)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug', 'career']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
	list_display = ['title', 'updated', 'created', 'owner']
