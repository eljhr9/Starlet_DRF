from django.apps import AppConfig
from elasticsearch_dsl import connections
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class FilmsConfig(AppConfig):
    name = 'films'
    verbose_name = _('Фильмы')

    def ready(self):
        import films.signals
        try:
            if settings.IS_DEPLOYED:
                connections.create_connection(
                    'default',
                    hosts=[{'host': settings.ES_HOST, 'port': settings.ES_PORT, 'url_prefix': 'es', 'use_ssl': True}])
            else:
                connections.create_connection(
                    'default',
                    hosts=[{'host': 'localhost', 'port': '9200'}])

        except Exception as e:
          print(e)
