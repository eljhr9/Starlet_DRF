from django.shortcuts import render, get_object_or_404
from .models import Film, Genre, People, Collection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def film_page(request, film_slug):
    film = get_object_or_404(Film, slug=film_slug)
    collections = Collection.objects.all()[:3]
    context = {'film': film}
    return render(request, 'movie/film_page.html', context)

def person_page(request, person_slug):
    persona = get_object_or_404(People, slug=person_slug)
    context = {'persona': persona}
    return render(request, 'movie/person_page.html', context)

def collections_list(request):
    films = Film.objects.all().order_by('-release_date')[:8]
    collections = Collection.objects.all()[:10]
    context = {'films': films, 'collections': collections}
    return render(request, 'movie/collections_list.html', context)

def collection_detail(request, pk):
    collections = Collection.objects.all()[:5]
    collection = get_object_or_404(Collection, pk=pk)
    context = {'collection': collection, 'collections': collections}
    return render(request, 'movie/collection_detail.html', context)

def genre_page(request, genre_slug):
    genre = get_object_or_404(Genre, slug=genre_slug)
    films = genre.films.all().order_by('-release_date')
    paginator = Paginator(films, 42)
    page = request.GET.get('page')
    try:
        films = paginator.page(page)
    except PageNotAnInteger:
        films = paginator.page(1)
    except EmptyPage:
        films = paginator.page(paginator.num_pages)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    last_page = paginator.num_pages
    page = paginator.get_page(page_num)
    context = {'genre': genre, 'films': films, 'page': page, 'last_page': last_page}
    return render(request, 'movie/genre_page.html', context)
