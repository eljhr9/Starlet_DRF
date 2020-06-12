from django.contrib import admin
from .models import Film, Genre, People, Collection

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
	list_display = ('ru_title', 'updated', 'imdb_rating', 'release_date', 'age_limit')
	list_display_links = ('ru_title',)
	search_fields = ('orig_title', 'ru_title', 'description', 'tagline')
	list_editable = ['imdb_rating']
	prepopulated_fields = {'slug': ('orig_title',)}

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug']
	prepopulated_fields = {'slug': ('title',)}


@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug', 'career']
	prepopulated_fields = {'slug': ('name',)}

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
	list_display = ['title', 'updated', 'created', 'owner']
