from django.core.management.base import BaseCommand
from django.utils import timezone
from movies.models import Review
from users.models import WatchedMovie


class Command(BaseCommand):
    help = 'Add watched movies based on reviews'

    def handle(self, *args, **options):
        reviews = Review.objects.all()
        for review in reviews:
            if not WatchedMovie.objects.filter(user=review.writer, movie=review.movie).exists():
                WatchedMovie.objects.get_or_create(
                    user=review.writer,
                    movie=review.movie,
                    watch_date=review.review_date  # or any other date you prefer
                )
        self.stdout.write(self.style.SUCCESS('Successfully added watched movies based on reviews.'))
