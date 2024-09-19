import requests
from django.core.management.base import BaseCommand
from movies.models import Movie, Review
from users.models import User
from django.utils import timezone

# Replace with your actual OAuth2 access token
TRAKT_ACCESS_TOKEN = 'your_actual_access_token'
TRAKT_API_URL = 'https://api.trakt.tv'


class Command(BaseCommand):
    help = 'Fetch and update reviews from Trakt'

    def get_trakt_headers(self):
        return {
            'Authorization': f'Bearer {TRAKT_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'trakt-api-version': '2'
        }

    def fetch_reviews_from_trakt(self, movie_id):
        url = f"{TRAKT_API_URL}/movies/{movie_id}/reviews"
        response = requests.get(url, headers=self.get_trakt_headers())
        if response.status_code == 200:
            return response.json()
        else:
            self.stdout.write(
                self.style.ERROR(f"Error fetching reviews for movie ID {movie_id}: {response.status_code}"))
            return []

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching and updating reviews from Trakt...')

        movies = Movie.objects.all()
        for movie in movies:
            reviews = self.fetch_reviews_from_trakt(movie.id)
            for review in reviews:
                # Extract review data safely
                review_user = review.get('user', {})
                username = review_user.get('username', 'unknown_user')
                email = review_user.get('email', '')

                # Create or update the user
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': email}
                )

                # Parse review date if available
                review_date_str = review.get('date', timezone.now().isoformat())
                try:
                    review_date = timezone.make_aware(
                        timezone.datetime.strptime(review_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    )
                except ValueError:
                    review_date = timezone.now()

                # Create or update the review
                Review.objects.update_or_create(
                    movie=movie,
                    writer=user,
                    defaults={
                        'review': review.get('review', 'No review content'),
                        'rating': review.get('rating', 5),  # Default rating if not provided
                        'review_date': review_date
                    }
                )

        self.stdout.write(self.style.SUCCESS('Reviews updated successfully.'))

