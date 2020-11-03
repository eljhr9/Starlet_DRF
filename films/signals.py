from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Movie, Person
from .document import MovieDocument, ActorDocument

@receiver(post_save, sender=Movie)
def my_handler(sender, instance, **kwargs):
    instance.indexing()

@receiver(post_save, sender=Person)
def my_handler(sender, instance, **kwargs):
    instance.indexing()
