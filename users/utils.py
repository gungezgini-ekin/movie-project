from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.db.models import Q
from users.models import User, LikedMovie
from movies.models import Movie, Review
from django.db.models import Max


def get_user_movie_matrix(users, movies, like_weight=0.3, rating_weight=0.7):
    user_ids = [user.id for user in users]
    movie_ids = [movie.id for movie in movies]

    user_movie_matrix = np.zeros((len(users), len(movies)))

    most_recent_reviews = (
        Review.objects.filter(writer_id__in=user_ids, movie_id__in=movie_ids)
        .values('writer_id', 'movie_id')
        .annotate(most_recent_id=Max('id'))
    )

    recent_reviews = Review.objects.filter(id__in=[item['most_recent_id'] for item in most_recent_reviews])

    user_idx_map = {user.id: idx for idx, user in enumerate(users)}
    movie_idx_map = {movie.id: idx for idx, movie in enumerate(movies)}

    for review in recent_reviews:
        user_idx = user_idx_map[review.writer_id]
        movie_idx = movie_idx_map[review.movie_id]

        user_movie_matrix[user_idx][movie_idx] = review.rating

    return user_movie_matrix


def calculate_user_similarity(users):
    movies = list(Movie.objects.all())
    user_movie_matrix = get_user_movie_matrix(users, movies)

    similarity_matrix = cosine_similarity(user_movie_matrix)

    return similarity_matrix
