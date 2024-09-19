from django.db import models
from django.utils import timezone
import datetime
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Director(models.Model):
    name = models.CharField(max_length=255)
    birth_year = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255, unique=True)
    year = models.IntegerField()
    pub_date = models.DateTimeField('date published', default=timezone.now)
    duration = models.IntegerField(default=0)
    director = models.ForeignKey(Director, on_delete=models.CASCADE)
    poster = models.ImageField(upload_to="movie_posters", default='poster.jpg')
    genre = models.ManyToManyField(Genre, blank=True)
    synopsis = models.TextField(blank=True)
    likes = models.IntegerField(default=0)
    trailer_id = models.CharField(max_length=255, blank=True, null=True)

    def get_avg_rating(self):
        if self.review_set.count() > 0:
            return "{:.1f}".format(self.review_set.aggregate(models.Avg('rating')).get('rating__avg'))
        else:
            return 0

    def come_out_this_year(self):
        now = timezone.now()
        return now.year == self.year

    def __str__(self):
        return self.title


class Actor(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    movies = models.ManyToManyField(Movie)

    def __str__(self):
        return self.name


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.review

