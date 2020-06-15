from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from elasticsearch_dsl import Search, Index, connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch, RequestsHttpConnection
from films.models import Movie
from films.document import MovieDocument
from requests_aws4auth import AWS4Auth

class Command(BaseCommand):
    help = 'Indexes Skills in Elastic Search'
    def handle(self, *args, **options):
        region = 'us-west-2'
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
