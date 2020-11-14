from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Movie, Person
from .documents import MovieDocument, ActorDocument

@receiver(post_save, sender=Movie)
def movie_handler(sender, instance, **kwargs):
    # Индексация сохраняемого Фильма
    instance.indexing()

@receiver(post_save, sender=Person)
def actor_handler(sender, instance, **kwargs):
    # Индексация сохраняемого Человека
    instance.indexing()
