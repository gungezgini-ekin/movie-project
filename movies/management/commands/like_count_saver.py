
from django.core.management import BaseCommand

from movies.models import Movie


class Command(BaseCommand):
    help = 'Arrange like counts'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        for movie in movies:
            movie.likes = movie.liked.count()
            movie.save()

            self.stdout.write(self.style.SUCCESS('Successfully saved like count movies for ' + movie.title))
