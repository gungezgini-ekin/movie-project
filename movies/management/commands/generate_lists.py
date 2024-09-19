import random
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from movies.models import Movie
from users.models import ListName, ElementOfList
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generates lists of movies for users'

    def handle(self, *args, **options):
        # Fetch all users excluding specific ones if necessary
        users = User.objects.exclude(id__in=[1, 2, 3, 4, 5])  # Exclude admin or specific users if needed
        movies = list(Movie.objects.all())

        for user in users:
            # Create a random number of lists for each user
            for i in range(random.randint(1, 5)):  # 1 to 5 lists per user
                list_name = f"{user.username}'s List {i+1}"
                is_private = random.choice([True, False])

                # Create the list
                movie_list = ListName.objects.create(name=list_name, user=user, is_private=is_private)

                # Add a random number of movies to the list
                for movie in random.sample(movies, random.randint(5, 35)):  # 5 to 20 movies per list
                    ElementOfList.objects.create(list_name=movie_list, movie=movie, user=user, element_add_date=timezone
                                                 .now())

            self.stdout.write(self.style.SUCCESS(f'Successfully generated lists for ' + str(user.id)))
