from django.core.management.base import BaseCommand
from django.utils import timezone
from movies.models import Review
from users.models import LikedMovie


class Command(BaseCommand):
    help = 'Add watched movies based on reviews'

    def handle(self, *args, **options):
        reviews = Review.objects.filter(rating__gte=7)
        for review in reviews:
            if not LikedMovie.objects.filter(user=review.writer, movie=review.movie).exists():
                LikedMovie.objects.get_or_create(
                    user=review.writer,
                    movie=review.movie,
                    like_date=review.review_date  # or any other date you prefer
                )
        self.stdout.write(self.style.SUCCESS('Successfully added liked movies based on reviews.'))
