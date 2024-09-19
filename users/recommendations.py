from django.db.models import Count

from .utils import calculate_user_similarity
from users.models import User, LikedMovie, WatchedMovie
from movies.models import Review, Movie
import numpy as np
from django.db.models import Avg, Count, Case, When


def recommend_friends_for_user(current_user, top_n_similar_users=15):
    users = list(User.objects.all())
    similarity_matrix = calculate_user_similarity(users)

    current_user_index = users.index(current_user)
    similar_users_indices = np.argsort(-similarity_matrix[current_user_index])  # Sort users by similarity

    similar_users_ids = [
        users[idx].id for idx in similar_users_indices[1:top_n_similar_users + 1]
    ]

    return similar_users_ids


def recommend_movies_for_user(current_user, num_recommendations=48):
    similar_users_ids = recommend_friends_for_user(current_user)
    has_reviews = Review.objects.filter(writer=current_user).exists()

    if has_reviews:
        recommended_movies = (
            Review.objects.filter(writer_id__in=similar_users_ids, rating__gte=8)
            .exclude(movie__in=Review.objects.filter(writer=current_user).values('movie'))
            .exclude(movie__in=LikedMovie.objects.filter(user=current_user).values('movie'))
            .exclude(movie__in=WatchedMovie.objects.filter(user=current_user).values('movie'))
            .values('movie')
            .annotate(num_high_ratings=Count('id'), avg_rating=Avg('rating'))
            .order_by('-num_high_ratings', '-avg_rating')
            .values_list('movie', flat=True)
            .distinct()[:num_recommendations]
        )

        recommended_movies = list(recommended_movies)  # Convert to list to maintain order
        ordered_movies = Movie.objects.filter(id__in=recommended_movies).order_by(
            Case(*[When(id=movie_id, then=pos) for pos, movie_id in enumerate(recommended_movies)])
        )
        return list(ordered_movies)

    else:
        recommended_movies = Movie.objects.order_by('-likes', 'title')[:num_recommendations]
        return list(recommended_movies)


