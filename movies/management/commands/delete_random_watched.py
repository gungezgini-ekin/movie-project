from django.core.management.base import BaseCommand
from users.models import WatchedMovie


class Command(BaseCommand):
    help = 'Delete all watched movies'

    def handle(self, *args, **options):
        WatchedMovie.objects.all().exclude(user_id__in=[1, 2, 3, 4, 5]).delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all watched movies.'))
