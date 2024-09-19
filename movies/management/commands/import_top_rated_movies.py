import requests
from django.core.management.base import BaseCommand
from movies.models import Movie, Director, Genre, Review  # Adjust the import paths
from users.models import User
from django.core.files.base import ContentFile
import urllib.request
from django.utils import timezone
from dateutil import parser


class Command(BaseCommand):
    help = 'Fetch and import top-rated movies from TMDb API'

    def handle(self, *args, **kwargs):
        api_key = 'cb3bc30b926d655f2e3e1d0507265fd8'
        base_url = 'https://api.themoviedb.org/3/movie/top_rated'
        page = 176
        max_page = 200  # Set the maximum number of pages you want to fetch

        while page <= max_page:
            response = requests.get(base_url, params={'api_key': api_key, 'page': page})
            data = response.json()

            if 'results' not in data:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data from page {page}."))
                break

            # Fetch existing genres from the database
            existing_genres = {genre.id: genre for genre in Genre.objects.all()}

            for movie_data in data['results']:
                title = movie_data['title']
                year = int(movie_data['release_date'].split('-')[0])
                synopsis = movie_data.get('overview', '')
                poster_url = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}"
                movie_id = movie_data['id']

                # Fetch movie details to get the runtime (duration)
                movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                movie_details_response = requests.get(movie_details_url, params={'api_key': api_key})
                movie_details = movie_details_response.json()
                duration = movie_details.get('runtime', 0)  # Runtime is in minutes

                # Fetch director info using the movie ID
                credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
                credits_response = requests.get(credits_url, params={'api_key': api_key})
                credits_data = credits_response.json()

                # Find the director in the credits
                director_name = 'Unknown'
                director_id = None
                for crew_member in credits_data.get('crew', []):
                    if crew_member['job'] == 'Director':
                        director_name = crew_member['name']
                        director_id = crew_member['id']  # Get the director's TMDb ID
                        break

                # Fetch or create director
                if director_id:
                    director_details_url = f"https://api.themoviedb.org/3/person/{director_id}"
                    director_response = requests.get(director_details_url, params={'api_key': api_key})
                    director_data = director_response.json()

                    birth_year = director_data.get('birthday', '')[:4] if director_data.get('birthday') else None
                    bio = director_data.get('biography', '')

                    director, created = Director.objects.update_or_create(
                        name=director_name,
                        defaults={
                            'birth_year': int(birth_year) if birth_year else None,
                            'bio': bio
                        }
                    )
                else:
                    director, created = Director.objects.get_or_create(name=director_name)

                # Create or get genres
                genre_ids = movie_data.get('genre_ids', [])
                genres = [existing_genres.get(genre_id) or Genre.objects.create(id=genre_id, name='Unknown')
                          for genre_id in genre_ids]

                # Download and save poster
                poster_file_name = poster_url.split('/')[-1]
                try:
                    poster_image = ContentFile(urllib.request.urlopen(poster_url).read(), poster_file_name)
                except Exception as e:
                    poster_image = None
                    self.stdout.write(self.style.WARNING(f"Failed to fetch poster: {e}"))

                # Create or update movie record
                movie, created = Movie.objects.update_or_create(
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
                movie.genre.set(genres)

                # Fetch and save reviews
                reviews_url = f'https://api.themoviedb.org/3/movie/{movie_id}/reviews'
                reviews_response = requests.get(reviews_url, params={'api_key': api_key})
                reviews_data = reviews_response.json()

                if 'results' in reviews_data and reviews_data['results']:
                    for review_data in reviews_data['results']:
                        author_name = review_data.get('author', 'Anonymous')
                        review_content = review_data.get('content', '')
                        rating = review_data.get('author_details', {}).get('rating', None)
                        review_date = parser.parse(review_data.get('created_at', timezone.now()))

                        if not rating:
                            rating = 5  # Set a default rating if none is provided

                        user, created = User.objects.get_or_create(username=author_name)

                        Review.objects.create(
                            movie=movie,
                            review=review_content,
                            rating=rating,
                            writer=user,
                            review_date=review_date,
                        )
                else:
                    self.stdout.write(self.style.WARNING(f"No reviews found for {title}"))

            self.stdout.write(self.style.SUCCESS(f'Successfully imported page {page}'))
            page += 1

