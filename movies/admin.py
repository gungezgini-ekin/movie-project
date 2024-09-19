from django.contrib import admin
from .models import Movie, Genre, Director, Review
# Register your models here.

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Director)
admin.site.register(Review)
