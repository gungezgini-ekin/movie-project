from django.urls import path, include

from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile_update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/details/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('liked_movies/<str:username>/', views.LikedMovieView.as_view(), name='liked_movies'),
    path('watchlist/<str:username>/', views.WatchListView.as_view(), name='watchlist'),
    path('profile/create_new_list/', views.CreateListView.as_view(), name='create_new_list'),
    path('list_details/<int:list_id>/<str:username>/', views.CustomListView.as_view(), name='custom_list'),
    path('all_lists/<str:username>/', views.SeeAllListsView.as_view(), name='all_lists'),
    path('all_reviews/<str:username>/', views.AllReviewsView.as_view(), name='all_reviews'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('delete_movie/<int:list_id>/', views.DeleteMovieFromList.as_view(), name='delete_movie'),
    path('follow/<str:username>/', views.FollowUserView.as_view(), name='follow'),
    path('unfollow/<str:username>/', views.UnfollowUserView.as_view(), name='unfollow'),
    path('all_followers/<str:username>/', views.AllFollowersView.as_view(), name='all_followers'),
    path('all_followings/<str:username>/', views.AllFollowingsView.as_view(), name='all_followings'),
    path('delete_follower/', views.DeleteFollowerView.as_view(), name='delete_follower'),
    path('watched_movies/<str:username>/', views.WatchedMoviesView.as_view(), name='watched_movies'),
    path('delete_review/', views.ProfileDeleteReviewView.as_view(), name='delete_review'),
    path('review_detail/<int:review_id>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('delete_list/', views.DeleteListView.as_view(), name='delete_list'),
    path('unfollow_from_profile/<str:username>/', views.ProfileUnfollowUserView.as_view(), name='unfollow_from_profile')
    ,
    path('movies_of_year/<int:year>/', views.MoviesOfYearView.as_view(), name='movies_of_year'),
    path('most_liked_movies/', views.MostLikedMoviesView.as_view(), name='most_liked_movies'),
    path('friends_watched_recently/', views.FriendsWatchedRecentlyView.as_view(), name='friends_watched_recently'),
    path('recommended_movies/', views.RecommendedMoviesView.as_view(), name='recommended_movies'),
    path('similar_users/', views.SimilarUsersView.as_view(), name='similar_users'),
    path('all_genres/', views.AllGenresView.as_view(), name='all_genres'),
    path('add_list_like/<int:list_id>/', views.AddListLikeView.as_view(), name='add_list_like'),
    path('delete_list_like/<int:list_id>/', views.DeleteListLikeView.as_view(), name='delete_list_like'),
    path('favourite_lists/<str:username>/', views.FavouriteListsView.as_view(), name='favourite_lists'),
    path('watched_movies/<str:username>/<int:year>/', views.WatchedMoviesView.as_view(), name='watched_movies'),
    path('all_reviews/<str:username>/<int:year>/', views.AllReviewsView.as_view(), name='all_reviews'),
    path('liked_movies/<str:username>/<int:year>', views.LikedMovieView.as_view(), name='liked_movies'),
    path('make_public/<int:list_id>/<str:username>/', views.MakeListPublicView.as_view(), name='make_public'),
    path('make_private/<int:list_id>/<str:username>/', views.MakeListPrivateView.as_view(), name='make_private'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

