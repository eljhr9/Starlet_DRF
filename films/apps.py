from django.apps import AppConfig
from elasticsearch_dsl import connections
from django.conf import settings

class FilmsConfig(AppConfig):
    name = 'films'
    verbose_name = 'Фильмы'

    def ready(self):
        import films.signals
        try:
          connections.create_connection(
              'default',
              hosts=[{'host': settings.ES_HOST, 'port': settings.ES_PORT, 'url_prefix': 'es', 'use_ssl': True}])
        except Exception as e:
          print(e)
