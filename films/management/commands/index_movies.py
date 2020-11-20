from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from elasticsearch_dsl import Search, Index, connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch, RequestsHttpConnection
from films.models import Movie, Person
from films.documents import MovieDocument, ActorDocument
from requests_aws4auth import AWS4Auth

class Command(BaseCommand):
    """
    Команда для обновления всех индексов Elastic search
    python manage.py index_movies
    """

    help = 'Indexes Movies and Persons in Elastic Search'
    def handle(self, *args, **options):
        if settings.IS_DEPLOYED:
            region = settings.AWS_REGION
            service = 'es'
            awsauth = AWS4Auth(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY, region, service)
            es = Elasticsearch(
                [{'host': settings.ES_HOST, 'port': settings.ES_PORT, 'url_prefix': 'es', 'use_ssl': True}],
                index="movie",
                http_auth = awsauth,
                use_ssl = True,
                verify_certs = True,
                connection_class = RequestsHttpConnection
            )
        else:
            es = Elasticsearch(
                [{'host': 'localhost', 'port': '9200'}],
                index="movie",
            )
        movie_index = Index('movie', using='default')
        movie_index.document(MovieDocument)
        if movie_index.exists():
            movie_index.delete()
            print('Deleted movie index.')
        MovieDocument.init()
        result = bulk(
            client=es,
            actions=(movie.indexing() for movie in Movie.objects.all().iterator())
        )
        print('Indexed movies.')
        print(result)

        if settings.IS_DEPLOYED:
            region = settings.AWS_REGION
            service = 'es'
            awsauth = AWS4Auth(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY, region, service)
            es = Elasticsearch(
                [{'host': settings.ES_HOST, 'port': settings.ES_PORT, 'url_prefix': 'es', 'use_ssl': True}],
                index="actor",
                http_auth = awsauth,
                use_ssl = True,
                verify_certs = True,
                connection_class = RequestsHttpConnection
            )
        else:
            es = Elasticsearch(
                [{'host': 'localhost', 'port': '9200'}],
                index="actor",
            )
        actor_index = Index('actor', using='default')
        actor_index.document(ActorDocument)
        if actor_index.exists():
            actor_index.delete()
            print('Deleted actor index.')
        ActorDocument.init()
        result = bulk(
            client=es,
            actions=(actor.indexing() for actor in Person.objects.all().iterator())
        )
        print('Indexed actors.')
        print(result)
