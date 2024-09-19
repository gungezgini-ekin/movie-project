import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from movies.models import Movie, Director, Genre  # Adjust the import paths
from django.core.files.base import ContentFile
import urllib.request


class Command(BaseCommand):
    help = 'Fetch and import movie genres from TMDb API'

    def handle(self, *args, **kwargs):
        api_key = 'cb3bc30b926d655f2e3e1d0507265fd8'
        url = 'https://api.themoviedb.org/3/genre/movie/list'
        response = requests.get(url, params={'api_key': api_key})
        data = response.json()

        for genre in data['genres']:
            Genre.objects.update_or_create(
                id=genre['id'],
                defaults={'name': genre['name']}
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported genres'))
