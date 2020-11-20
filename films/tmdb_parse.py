import requests
from bs4 import BeautifulSoup
from django.utils.translation import gettext as _


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
    'accept': '*/*'
}
HOST = 'https://www.themoviedb.org'


def get_text_if_not_None(data):
    if data is not None:
        return data.get_text(strip=True)
    else:
        return None


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='card style_1')

    movie_links = []
    for item in items:
        movie_links.append(
            HOST + item.find('a', class_='image').get('href')
        )
    return movie_links


def get_directors(soup):
    peoples = soup.find_all('li', class_='profile')
    profiles = []
    for person in peoples:
        character = person.find('p', class_='character').get_text()
        if 'Director' in character or _('Создатель') in character:
            link = HOST + person.find('a').get('href')
            html = get_html(link)
            if html.status_code == 200:
                profiles.append(get_person(html.text))
            else:
                print(_('Error in parsing directors'))
    return profiles


def get_cast(soup):
    peoples = soup.find_all('li', class_='card')
    cast = []
    for person in peoples:
        link = HOST + person.find('a').get('href')
        html = get_html(link)
        if html.status_code == 200:
            cast.append(get_person(html.text))
        else:
            print(_('Error in parsing cast'))
    return cast


def get_movie(html):
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('div', class_='title ott_false')

    print(title)

    translated_title = title.find_next('a').get_text()
    orig_title = soup.find('p', class_='wrap')
    if orig_title:
        orig_title = orig_title.get_text().replace(_('Original Title '), '')
    else:
        orig_title = translated_title
    description = get_text_if_not_None(soup.find('div', class_='overview'))
    age_limit = get_text_if_not_None(title.find_next('span', class_='certification'))
    tagline = get_text_if_not_None(soup.find('h3', class_='tagline'))
    try:
        imdb_rating = int(soup.find('span', class_='icon').get('class')[1].replace('icon-r', '')) / 10
    except ValueError:
        imdb_rating = '0+'
    release = get_text_if_not_None(title.find_next('span', class_='release'))
    release_date = release.split(' ')[0].split('/') if release else None
    duration = title.find_next('span', class_='runtime')
    if duration:
        duration = duration.get_text(strip=True).split(' ')
        if len(duration) == 2:
            duration_minutes = int(duration[0].replace('h', '')) * 60
            duration_minutes += int(duration[1].replace('m', ''))
        elif len(duration) == 1:
            duration_minutes = int(duration[0].replace('m', ''))
    else:
        duration_minutes = None
    genres = title.find('span', class_='genres').find_all('a')
    directors = get_directors(soup.find('ol', class_='people'))
    cast = get_cast(soup.find('ol', class_='people scroller'))
    poster = soup.find('img', class_='poster').get('src')

    movie = {
        'orig_title': orig_title,
        'translated_title': translated_title,
        'description': description,
        'directors': directors,
        'age_limit': age_limit,
        'tagline': tagline,
        'imdb_rating': imdb_rating,
        'release_date': release_date,
        'duration': duration_minutes,
        'cast': cast,
        'genres': [genre.get_text() for genre in genres],
        'poster': 'https:' + poster.replace('w300_and_h450_bestv2_filter(blur)', 'original')
    }
    return movie


def get_person(html):
    soup = BeautifulSoup(html, 'html.parser')
    facts = soup.find('section', class_='facts').find_next('section').find_all('p')
    data = []
    for fact in facts:
        fact_title = fact.find('strong').get_text()
        fact = fact.get_text(strip=True).replace(fact_title, '')
        data.append(None if fact == '-' else fact)

    if data[3]:
        birth_date = data[3].split(' ')[0].split('-')
    else:
        birth_date = None

    photo_img = soup.find('img', class_='profile')
    if photo_img:
        photo = 'https:' + photo_img.get('src').replace('w300_and_h450_bestv2_filter(blur)', 'original')
    else:
        photo = None

    person = {
        'name': soup.find('h2', class_='title').get_text(strip=True),
        'biography': get_text_if_not_None(soup.find('div', class_='biography').find_next('div', class_='text')),
        'career': data[0],
        'gender': data[2],
        'birth_date': birth_date,
        'birth_place': data[4],
        'photo': photo
    }
    return person


def parse_content(url):
    html = get_html(url)
    if html.status_code == 200:
        return get_movie(html.text)
    else:
        print(_('Error in parsing content'))
