from django.db.models.signals import post_save, post_delete  # Import a post_save signal when a user is created
from django.contrib.auth.models import User  # Import the built-in User model, which is a sender
from django.dispatch import receiver  # Import the receiver
from .models import Profile, ListName
from django.core.exceptions import ObjectDoesNotExist
from movies.models import Movie, Director, Genre
from movies.search.search import MovieDocument, DirectorDocument, GenreDocument, UserDocument, ListDocument


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Movie)
def update_movie_index(sender, instance, **kwargs):
    MovieDocument().update(instance)


@receiver(post_delete, sender=Movie)
def delete_movie_index(sender, instance, **kwargs):
    MovieDocument().delete(instance)


@receiver(post_save, sender=Director)
def update_movie_index(sender, instance, **kwargs):
    DirectorDocument().update(instance)


@receiver(post_delete, sender=Director)
def delete_movie_index(sender, instance, **kwargs):
    DirectorDocument().delete(instance)


@receiver(post_save, sender=Genre)
def update_movie_index(sender, instance, **kwargs):
    GenreDocument().update(instance)


@receiver(post_delete, sender=Genre)
def delete_movie_index(sender, instance, **kwargs):
    GenreDocument().delete(instance)


@receiver(post_save, sender=User)
def update_movie_index(sender, instance, **kwargs):
    UserDocument().update(instance)


@receiver(post_delete, sender=User)
def delete_movie_index(sender, instance, **kwargs):
    UserDocument().delete(instance)


@receiver(post_save, sender=ListName)
def update_movie_index(sender, instance, **kwargs):
    ListDocument().update(instance)


@receiver(post_delete, sender=ListName)
def delete_movie_index(sender, instance, **kwargs):
    ListDocument().delete(instance)
