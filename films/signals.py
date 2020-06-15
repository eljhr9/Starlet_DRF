from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Movie
from .document import MovieDocument

@receiver(post_save, sender=Movie)
def my_handler(sender, instance, **kwargs):
    instance.indexing()
