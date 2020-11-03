from datetime import date
from multiprocessing import Pool
from .tmdb_parse import get_html, get_links, parse_content
from .models import Movie, Person, Genre

from urllib.parse import urlparse
import requests
from django.core.files.base import ContentFile

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


def load_to_db(movies):
    movie_details = {}

    for movie in movies:
        film, created = Movie.objects.get_or_create(
            ru_title=movie['ru_title'],
            defaults={
                'orig_title': movie['orig_title'],
                'release_date': get_formated_date(movie['release_date'][::-1]),
                'description': movie['description'],
                'age_limit': movie['age_limit'],
                'tagline': movie['tagline'],
                'imdb_rating': movie['imdb_rating'],
                'duration': movie['duration'],
                'fullness': 70,
            }
        )

        movie_details[movie['ru_title']] = {}
        movie_detail = movie_details[movie['ru_title']]
        movie_detail['status'] = 'created' if created else 'exists'
        movie_detail['changed'] = 'no changes'
        movie_detail['genres'] = 'no changes'

        if created:
            for genre in movie['genres']:
                film.genres.add(Genre.objects.get_or_create(title=genre)[0])

            for director in movie['directors']:
                persona, created = Person.objects.get_or_create(
                    name = director['name'],
                    biography = director['biography'],
                    career = director['career'],
                    gender = director['gender'],
                    birth_date = get_formated_date(director['birth_date']),
                    birth_place = director['birth_place']
                )
                film.directors.add(persona)

                if created and director['photo'] is not None:
                    saved = save_img(director['photo'], persona.photo)


            for person in movie['cast'][::-1]:
                persona, created = Person.objects.get_or_create(
                    name = person['name'],
                    biography = person['biography'],
                    career = person['career'],
                    gender = person['gender'],
                    birth_date = get_formated_date(person['birth_date']),
                    birth_place = person['birth_place']
                )
                film.cast.add(persona)

                if created and person['photo'] is not None:
                    saved = save_img(person['photo'], persona.photo)

            poster = save_img(movie['poster'], film.poster)

        elif film.fullness <= 60:
            movie_detail['changed'] = []
            film.fullness = 70

            if not film.orig_title:
                film.orig_title = movie['orig_title']
                movie_detail['changed'].append('orig_title')
            if not film.description:
                film.description = movie['description']
                movie_detail['changed'].append('description')
            if not film.age_limit or film.age_limit == '0+':
                film.age_limit = movie['age_limit']
                movie_detail['changed'].append('age_limit')
            if not film.tagline:
                film.tagline = movie['tagline']
                movie_detail['changed'].append('tagline')
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
                    genre_obj, created = Genre.objects.get_or_create(title=genre)
                    movie_detail['genres'][genre] = 'created' if created else 'added'
                    film.genres.add(genre_obj)

            if not film.directors.all():
                movie_detail['directors'] = {}

                for director in movie['directors']:
                    persona, created = Person.objects.get_or_create(
                        name = director['name'],
                        biography = director['biography'],
                        career = director['career'],
                        gender = director['gender'],
                        birth_date = get_formated_date(director['birth_date']),
                        birth_place = director['birth_place']
                    )
                    movie_detail['directors'][persona.name] = 'created' if created else 'added'
                    film.directors.add(persona)

                    if created and director['photo'] is not None:
                        saved = save_img(director['photo'], persona.photo)

            if not film.cast.all():
                movie_detail['cast'] = {}

                for person in movie['cast'][::-1]:
                    persona, created = Person.objects.get_or_create(
                        name = person['name'],
                        biography = person['biography'],
                        career = person['career'],
                        gender = person['gender'],
                        birth_date = get_formated_date(person['birth_date']),
                        birth_place = person['birth_place']
                    )

                    movie_detail['cast'][persona.name] = 'created' if created else 'added'
                    film.cast.add(persona)

                    if created and person['photo'] is not None:
                        saved = save_img(person['photo'], persona.photo)

            if not film.poster:
                poster = save_img(movie['poster'], film.poster)
                movie_detail['changed'].append('poster')
            else:
                film.save()

    return movie_details


def parse(quantity=1):
    movie_links = []
    for page in range(1, quantity+1):
        params = {
            'page': page,
            'language': 'ru'
        }
        html = get_html(URL, params)
        if html.status_code == 200:
            movie_links.extend(get_links(html.text))
        else:
            print('Error')

    with Pool(20) as p:
        movies = p.map(parse_content, movie_links)

    details = load_to_db(movies)
    return details
