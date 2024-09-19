import random
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from movies.models import Movie
from users.models import LikedMovie
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generate liked movies'

    def handle(self, *args, **options):
        movies = list(Movie.objects.all())
        users = User.objects.exclude(id__in=[1, 2, 3, 4, 5])
        for user in users:
            liked_movies = random.sample(movies, random.randint(5, 30))
            for movie in liked_movies:
                LikedMovie.objects.get_or_create(user=user, movie=movie, like_date=timezone.now())

            self.stdout.write(self.style.SUCCESS('Successfully generated liked movies for ' + str(user.id)))
