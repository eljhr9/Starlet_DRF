from datetime import date
from multiprocessing import Pool
from .tmdb_parse import get_html, get_links, parse_content
from .models import Movie, Person, Genre, MovieTranslations
from urllib.parse import urlparse
import requests
from django.core.files.base import ContentFile
from django.utils.translation import get_language, get_language_info


URL = 'https://www.themoviedb.org/movie/'


def get_formated_date(data):
    if data:
        formated_date = date(
            int(data[0]),
            int(data[1]),
            int(data[2])
        )
    else:
        formated_date = None
    return formated_date


def save_img(url, model):
    name = urlparse(url).path.split('/')[-1]
    response = requests.get(url)
    if response.status_code == 200:
        model.save(name, ContentFile(response.content), save=True)
        return True
    return False


def get_or_create_person(data):
    try:
        person = Person.objects.get(translations__name=data['name'])
        created = False
    except:
        person  = Person.objects.create(
            name=data['name'],
            biography = data['biography'],
            career = data['career'],
            gender =  data['gender'],
            birth_date = get_formated_date(data['birth_date']),
            birth_place = data['birth_place']
        )
        created = True
    return person, created


def load_to_db(movies):
    movie_details = {}

    for movie in movies:
        if get_language() == 'en':
            movie['release_date'] = [movie['release_date'][1], movie['release_date'][0], movie['release_date'][2]]
        film, created = Movie.objects.get_or_create(
            orig_title=movie['orig_title'],
            defaults={
                'release_date': get_formated_date(movie['release_date'][::-1]),
                'age_limit': movie['age_limit'],
                'imdb_rating': movie['imdb_rating'],
                'duration': movie['duration'],
                'fullness': 50,
            }
        )

        movie_details[movie['translated_title']] = {}
        movie_detail = movie_details[movie['translated_title']]
        movie_detail['status'] = 'created' if created else 'exists'
        movie_detail['changed'] = 'no changes'
        movie_detail['genres'] = 'no changes'

        if created:
            translate = MovieTranslations.objects.create(
                language_code=get_language(),
                movie=film,
                title=movie['translated_title'],
                description=movie['description'],
                tagline=movie['tagline']
            )
            poster = save_img(movie['poster'], translate.poster)

            for genre in movie['genres']:
                try:
                    genre_obj = Genre.objects.get(translations__title=genre)
                except:
                    genre_obj  = Genre.objects.create(title=genre)
                film.genres.add(genre_obj)

            for director in movie['directors']:
                persona, created = get_or_create_person(director)
                film.directors.add(persona)

                if created and director['photo'] is not None:
                    saved = save_img(director['photo'], persona.photo)

            for person in movie['cast'][::-1]:
                persona, created = get_or_create_person(person)
                film.cast.add(persona)

                if created and person['photo'] is not None:
                    saved = save_img(person['photo'], persona.photo)

        elif film.fullness <= 60:
            movie_detail['changed'] = []

            movie_translate, created = MovieTranslations.objects.get_or_create(
                language_code=get_language(),
                movie=film,
                defaults={
                    'title': movie['translated_title'],
                    'description': movie['description'],
                    'tagline': movie['tagline']
                }
            )
            poster = save_img(movie['poster'], movie_translate.poster)
            if created:
                film.fullness += 5

            if not film.age_limit or film.age_limit == '0+':
                film.age_limit = movie['age_limit']
                movie_detail['changed'].append('age_limit')
            if not film.imdb_rating:
                film.imdb_rating = movie['imdb_rating']
                movie_detail['changed'].append('imdb_rating')
            if not film.release_date:
                film.release_date = get_formated_date(movie['release_date'][::-1])
                movie_detail['changed'].append('release_date')
            if not film.duration:
                film.duration = movie['duration']
                movie_detail['changed'].append('duration')

            if not film.genres.all():
                movie_detail['genres'] = {}

                for genre in movie['genres']:
                    try:
                        genre_obj = Genre.objects.get(translations__title=genre)
                    except:
                        genre_obj  = Genre.objects.create(title=genre)
                    film.genres.add(genre_obj)

            if not film.directors.all():
                movie_detail['directors'] = {}

                for director in movie['directors']:
                    persona, created = get_or_create_person(director)
                    movie_detail['directors'][persona.name] = 'created' if created else 'added'
                    film.directors.add(persona)

                    if created and director['photo'] is not None:
                        saved = save_img(director['photo'], persona.photo)

            if not film.cast.all():
                movie_detail['cast'] = {}

                for person in movie['cast'][::-1]:
                    persona, created = get_or_create_person(person)

                    movie_detail['cast'][persona.name] = 'created' if created else 'added'
                    film.cast.add(persona)

                    if created and person['photo'] is not None:
                        saved = save_img(person['photo'], persona.photo)

            film.save()
    return movie_details


def parse(quantity=1):
    movie_links = []
    for page in range(1, quantity+1):
        params = {
            'page': page,
            'language': get_language()
        }
        html = get_html(URL, params)
        if html.status_code == 200:
            movie_links.extend(get_links(html.text))
        else:
            print('Error')

    movies = []
    # for link in movie_links[:5]:
    #     movies.append(parse_content(link))
    #
    with Pool(20) as p:
        movies = p.map(parse_content, movie_links)

    details = load_to_db(movies)
    return details
