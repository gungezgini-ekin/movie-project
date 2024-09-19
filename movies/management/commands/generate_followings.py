import random
from django.contrib.auth.models import User
from users.models import Following
from django.utils import timezone
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate random followings'

    def handle(self, *args, **options):
        users = list(User.objects.exclude(id__in=[1, 2, 3, 4, 5]))
        for user in users:
            following_users = random.sample(users, random.randint(5, 20))
            for following_user in following_users:
                if following_user != user:
                    Following.objects.get_or_create(follower=user, following=following_user)

            self.stdout.write(self.style.SUCCESS('Successfully generated followings for ' + str(user.id)))
