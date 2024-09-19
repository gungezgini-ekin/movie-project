from django.db import models
from django.contrib.auth.models import User

from movies.models import Movie
from django.utils import timezone
from django.db.models import Max, Subquery, OuterRef


class Following(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings', default=None)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True)

    def get_last_watched(self):
        followings = Following.objects.filter(follower=self.user)
        friends = User.objects.filter(id__in=followings.values_list('following', flat=True))

        latest_watch_dates = WatchedMovie.objects.filter(
            user__in=friends
        ).values('movie').annotate(
            latest_watch_date=Max('watch_date')
        ).values('movie', 'latest_watch_date')

        last_watched = WatchedMovie.objects.filter(
            user__in=friends,
            movie__in=Subquery(latest_watch_dates.values('movie')),
            watch_date__in=Subquery(
                latest_watch_dates.filter(movie=OuterRef('movie')).values('latest_watch_date')
            )
        ).order_by('-watch_date')

        return last_watched

    def __str__(self):
        return self.user.username


class LikedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='liked')
    like_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.movie.title


class WantToWatchMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    want_to_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.movie.title


class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watched_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watch_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.movie.title


class ListName(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ElementOfList(models.Model):
    list_name = models.ForeignKey(ListName, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element_add_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.movie.title


class LikedList(models.Model):
    list_name = models.ForeignKey(ListName, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like_date = models.DateTimeField(default=timezone.now)

