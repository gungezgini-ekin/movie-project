import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from movies.models import Movie, Director, Genre  # Adjust the import paths
from django.core.files.base import ContentFile
import urllib.request


class Command(BaseCommand):
    help = 'Fetch and import movies from TMDb API'

    def handle(self, *args, **kwargs):
        api_key = 'cb3bc30b926d655f2e3e1d0507265fd8'
        url = 'https://api.themoviedb.org/3/movie/popular'
        try:
            response = requests.get(url, params={'api_key': api_key})
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Request failed: {e}"))
            return

        existing_genres = {genre.id: genre for genre in Genre.objects.all()}

        for movie_data in data['results']:
            title = movie_data['title']
            year = int(movie_data['release_date'].split('-')[0])
            duration = movie_data.get('runtime', 0)
            synopsis = movie_data.get('overview', '')
            poster_url = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}"

            # Fetch or create director
            director_name = movie_data.get('director', 'Unknown')  # Adjust if director info is available
            director, created = Director.objects.get_or_create(name=director_name)

            # Create or get genres

            genre_ids = movie_data.get('genre_ids', [])
            genres = [existing_genres.get(genre_id) or Genre.objects.create(id=genre_id, name='Unknown') for genre_id
                      in genre_ids]

            # Download and save poster
            poster_file_name = poster_url.split('/')[-1]
            try:
                poster_image = ContentFile(urllib.request.urlopen(poster_url).read(), poster_file_name)
            except Exception as e:
                poster_image = None
                self.stdout.write(self.style.WARNING(f"Failed to fetch poster: {e}"))

            # Create or update movie record
            Movie.objects.update_or_create(
                title=title,
                defaults={
                    'year': year,
                    'duration': duration,
                    'synopsis': synopsis,
                    'poster': poster_image,
                    'director': director,
                    'likes': 0,  # Set default likes
                }
            )
            # Assign genres
            movie = Movie.objects.get(title=title)
            movie.genre.set(genres)

        self.stdout.write(self.style.SUCCESS('Successfully imported movies'))