from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static


app_name = 'movies'

urlpatterns = [

    path('<str:name>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('<str:name>/add_review/', views.AddReviewView.as_view(), name='add_review'),
    path('<str:name>/like_movie/', views.AddLikeMovieView.as_view(), name='like_movie'),
    path('<str:name>/want_to_watch/', views.AddWantToWatchView.as_view(), name='want_to_watch'),
    path('<str:name>/add_to_list/', views.AddMovieToList.as_view(), name='add_to_list'),
    path('<str:name>/delete_like/', views.DeleteLikedMovieView.as_view(), name='delete_like'),
    path('<str:name>/delete_from_watchlist/', views.DeleteWantToWatchMovieView.as_view(), name='delete_from_watchlist'),
    path('<str:name>/director/', views.DirectorDetailView.as_view(), name='director_detail'),
    path('<str:name>/genre/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('<str:name>/delete_from_watched/', views.DeleteWatchedMovieView.as_view(), name='delete_from_watched'),
    path('<str:name>/add_watched/', views.AddWatchedMovieView.as_view(), name='add_watched'),
    path('<str:name>/delete_review/', views.DeleteReviewView.as_view(), name='delete_review'),
    path('<int:review_id>/review_detail/', views.ReviewDetailView.as_view(), name='review_detail')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
