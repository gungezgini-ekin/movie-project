from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages

from movies.models import Movie, Review, Director, Genre
from users.forms import UserUpdateForm, ProfileUpdateForm, NewListForm
from users.models import LikedMovie, WantToWatchMovie, ListName, ElementOfList, Following, WatchedMovie, LikedList
from django.contrib.auth.models import User
from django.db.models import F
from django.utils import timezone
import datetime
from movies.search.search import MovieDocument, DirectorDocument, GenreDocument, UserDocument, ListDocument
from elasticsearch_dsl import Q
from django.core.paginator import Paginator
from .recommendations import recommend_movies_for_user, recommend_friends_for_user


class HomeView(View):
    def get(self, request):
        # movies = Movie.objects.all()
        now = timezone.now()
        most_liked_movies = Movie.objects.order_by('-likes', 'title')[:6]
        movies_of_this_year = Movie.objects.filter(year=now.year).order_by('-pub_date', 'title')[:6]

        if request.user.is_authenticated:
            movies_of_friends = request.user.profile.get_last_watched()[:6]
            recommendations = recommend_movies_for_user(request.user)[:6]
            similar_users = list(User.objects.filter(id__in=recommend_friends_for_user(request.user)))[:6]
            no_reviews = not Review.objects.filter(writer=request.user).exists()
        else:
            movies_of_friends = []
            recommendations = []
            similar_users = []
            no_reviews = True

        return render(request, "users/home.html", {"movies_of_this_year": movies_of_this_year,
                                                   "most_liked_movies": most_liked_movies,
                                                   "movies_of_friends": movies_of_friends,
                                                   "recommendations": recommendations,
                                                   "similar_users": similar_users,
                                                   'year': now.year, 'no_reviews': no_reviews})


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, "users/register.html", {'form': form})

    def post(self, request):
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('users:home'))
        else:
            messages.error(request, "Invalid username or password")
            return HttpResponseRedirect(reverse('users:register'))


class LoginView(View):
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('users:home'))
        else:
            messages.error(request, "Invalid username or password")
            return HttpResponseRedirect(reverse('users:login'))

    def get(self, request):
        form = AuthenticationForm()
        return render(request, "users/login.html", {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('users:login'))


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    def get(self, request):
        user_update_form = UserUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, 'users/profile_update.html',
                      {'user_update_form': user_update_form, 'profile_update_form': profile_update_form})

    def post(self, request):
        user_update_form = UserUpdateForm(request.POST, instance=request.user)
        profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_update_form.is_valid() and profile_update_form.is_valid():
            user_update_form.save()
            profile_update_form.save()
            messages.success(request, "Your profile has been updated!")
            return HttpResponseRedirect(reverse('users:profile', args=[request.user.username]))
        else:
            messages.error(request, "Please try to update again.")
            return HttpResponseRedirect(reverse('users:profile_update'))


class ProfileView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        now_year = timezone.now().year

        all_liked_movies = LikedMovie.objects.filter(user=user)
        liked_movies = all_liked_movies.order_by('-like_date', 'movie__title')[:4]
        liked_this_year_count = all_liked_movies.filter(like_date__year=now_year).count()
        all_liked_count = all_liked_movies.count()

        all_want_to_watch = WantToWatchMovie.objects.filter(user=user)
        want_to_watch = all_want_to_watch.order_by('-want_to_date', 'movie__title')[:4]

        all_watched_movies = WatchedMovie.objects.filter(user=user)
        watched_movies = all_watched_movies.order_by('-watch_date', 'movie__title')[:4]
        watched_this_year_count = all_watched_movies.filter(watch_date__year=now_year).count()
        all_watched_count = all_watched_movies.count()

        reviews_this_year_count = Review.objects.filter(writer=user, review_date__year=now_year).count()
        all_reviews_count = Review.objects.filter(writer=user).count()

        are_equal = request.user.username == username

        follows = (request.user.is_authenticated and Following.objects.filter(follower=request.user,
                                                                              following=user).exists())

        mutual_follow = (request.user.is_authenticated and Following.objects.filter(follower=request.user,
                                                                                    following=user).exists() and
                         Following.objects.filter(follower=user, following=request.user).exists())

        mutual_follow_or_equal = mutual_follow or are_equal
        followers_count = user.followers.count()
        following_count = user.followings.count()

        most_liked_lists = ListName.objects.filter(user=user, is_private=False).order_by("-likes", "name")[:3]

        return render(request, 'users/profile.html', {'liked_movies': liked_movies, 'want_to_watch': want_to_watch,
                                                      "user": user, "are_equal": are_equal, "follows": follows,
                                                      "mutual_follow_or_equal": mutual_follow_or_equal,
                                                      "followers_count": followers_count,
                                                      "following_count": following_count,
                                                      "watched_movies": watched_movies,
                                                      "all_watched_count": all_watched_count,
                                                      "watched_this_year_count": watched_this_year_count,
                                                      "reviews_this_year_count": reviews_this_year_count,
                                                      "all_reviews_count": all_reviews_count,
                                                      "all_liked_count": all_liked_count,
                                                      "liked_this_year_count": liked_this_year_count,
                                                      "year": now_year, "most_liked_lists": most_liked_lists})


class LikedMovieView(View):
    def get(self, request, username, year=0):
        user = get_object_or_404(User, username=username)
        if year == 0:
            movies = user.likedmovie_set.all().order_by('-like_date', 'movie__title')
        else:
            movies = user.likedmovie_set.filter(like_date__year=year).order_by('-like_date', 'movie__title')
        paginator = Paginator(movies, 24)
        page_number = request.GET.get('page')
        liked_movies = paginator.get_page(page_number)
        are_equal = request.user.username == username
        years = LikedMovie.objects.filter(user=user).values_list("like_date__year", flat=True).distinct().order_by(
            "-like_date__year")
        return render(request, 'users/liked_movies.html', {"liked_movies": liked_movies, "user": user,
                                                           "are_equal": are_equal, "year": year,
                                                           "all": year == 0, "years": years})


class WatchListView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        paginator = Paginator(user.wanttowatchmovie_set.all().order_by('-want_to_date', 'movie__title'), 24)
        page_number = request.GET.get('page')
        watch_list = paginator.get_page(page_number)
        are_equal = request.user.username == username
        return render(request, 'users/watchlist_movies.html', {"watch_list": watch_list, "user": user,
                                                               "are_equal": are_equal})


class WatchedMoviesView(View):
    def get(self, request, username, year=0):
        user = get_object_or_404(User, username=username)
        if year == 0:
            movies = user.watched_movies.all().order_by('-watch_date', 'movie__title')
        else:
            movies = user.watched_movies.filter(watch_date__year=year).order_by('-watch_date', 'movie__title')
        paginator = Paginator(movies, 24)
        page_number = request.GET.get('page')
        watched_movies = paginator.get_page(page_number)
        are_equal = request.user.username == username
        years = WatchedMovie.objects.filter(user=user).values_list('watch_date__year', flat=True).distinct().order_by(
            '-watch_date__year')
        return render(request, 'users/watched_movies.html', {"watched_movies": watched_movies,
                                                             "user": user, "are_equal": are_equal, 'year': year,
                                                             "all": year == 0, "years": years})


class CustomListView(View):
    def get(self, request, list_id, username):
        list_name_object = get_object_or_404(ListName, id=list_id)
        user = get_object_or_404(User, username=username)
        are_equal = request.user.username == username
        if list_name_object.is_private and request.user != user:
            my_list = ElementOfList.objects.none()
            messages.error(request, "You do not have permission to view this private list.")
        else:
            paginator = Paginator((ElementOfList.objects.filter(list_name=list_name_object, user=user).order_by(
                '-element_add_date', 'list_name__name')), 24)
            page_number = request.GET.get('page')
            my_list = paginator.get_page(page_number)
        permitted = not (list_name_object.is_private and request.user != user)

        if request.user.is_authenticated:
            liked = LikedList.objects.filter(user=request.user, list_name=list_name_object).exists()
        else:
            liked = False

        return render(request, 'users/listed_movies.html', {"list": my_list, "list_name": list_name_object.name,
                                                            "username": username, "are_equal": are_equal,
                                                            "permitted": permitted, "list_id": list_id, 'liked': liked,
                                                            'is_private': list_name_object.is_private})


@method_decorator(login_required, name='dispatch')
class CreateListView(View):
    def get(self, request):
        form = NewListForm()
        return render(request, 'users/create_new_list.html', {"form": form})

    def post(self, request):
        form = NewListForm(data=request.POST)
        if form.is_valid():
            new_list = form.save(commit=False)
            new_list.user = request.user
            new_list.save()
            messages.success(request, 'New list has been created!')
            return HttpResponseRedirect(reverse('users:profile', args=[request.user.username]))
        else:
            messages.error(request, "Please try to create a new list again.")
            return HttpResponseRedirect(reverse('users:create_new_list'))


class SeeAllListsView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        all_public_lists = ListName.objects.filter(user=user, is_private=False)
        if request.user == user:
            all_private_lists = ListName.objects.filter(user=user, is_private=True)
        else:
            all_private_lists = ListName.objects.none()
        all_lists = (all_public_lists | all_private_lists).order_by('name')
        are_equal = request.user.username == username

        return render(request, 'users/all_lists.html', {"all_lists": all_lists, "user": user, "are_equal": are_equal})


class AllReviewsView(View):
    def get(self, request, username, year=0):
        user = get_object_or_404(User, username=username)
        if year == 0:
            review_objects = user.review_set.all().order_by('-review_date', 'movie__title')
        else:
            review_objects = user.review_set.filter(review_date__year=year).order_by('-review_date', 'movie__title')

        paginator = Paginator(review_objects, 12)
        page_number = request.GET.get('page')
        reviews = paginator.get_page(page_number)
        are_equal = request.user == user
        years = user.review_set.values_list("review_date__year", flat=True).distinct().order_by('-review_date__year')
        return render(request, 'users/all_reviews.html', {"reviews": reviews, "user": user, "are_equal": are_equal,
                                                          'year': year, "all": year == 0, "years": years})


class SearchView(View):
    def post(self, request):
        query = request.POST['search_query']
        movies_results = (MovieDocument.search().query("bool", should=[Q("match", title=query), Q("fuzzy", title=query),
                                                                       Q("prefix", title=query)]).extra(size=12).execute
                          ().hits)
        directors = DirectorDocument.search().query("bool", should=[Q("match", name=query), Q("fuzzy", name=query),
                                                                    Q("prefix", name=query)]).execute().hits
        genres = GenreDocument.search().query("bool", should=[Q("match", name=query), Q("fuzzy", name=query),
                                                              Q("prefix", name=query)]).execute().hits
        users = UserDocument.search().query("bool", should=[Q("match", username=query), Q("fuzzy", username=query),
                                                            Q("prefix", username=query)]).execute().hits

        # movie.meta.id is the elasticsearch document id, it corresponds
        # to the primary key of the model instance in Django
        movie_ids = [movie.meta.id for movie in movies_results]
        movies = Movie.objects.filter(id__in=movie_ids)

        other_lists = ListDocument.search().query("bool", must=[
            {"prefix": {"name": query}},
            {"term": {"is_private": False}}
        ]).execute().hits

        if request.user.is_authenticated:
            your_lists_results = ListDocument.search().query("bool", must=[
                {"prefix": {"name": query}},
                {"term": {"user": request.user.id}}
            ]).execute().hits

            your_private_lists = ListDocument.search().query("bool", must=[
                {"prefix": {"name": query}},
                {"term": {"user": request.user.id}},
                {"term": {"is_private": True}}
            ]).execute().hits

        else:
            # they are empty search query objects
            your_lists_results = ListDocument.search().query('match_all')[:0].execute().hits
            your_private_lists = ListDocument.search().query('match_all')[:0].execute().hits

        all_lists_results = list(other_lists) + list(your_private_lists)
        all_lists_ids = [all_list.meta.id for all_list in all_lists_results]
        all_lists = ListName.objects.filter(id__in=all_lists_ids)

        your_lists_ids = [your_list.meta.id for your_list in your_lists_results]
        your_lists = ListName.objects.filter(id__in=your_lists_ids)

        return render(request, 'users/search_results.html',
                      {"movies": movies, "query": query, "your_lists": your_lists,
                       "users": users, "all_lists": all_lists, "directors": directors, "genres": genres})


@method_decorator(login_required, name='dispatch')
class DeleteMovieFromList(View):
    def post(self, request, list_id):
        selected_movie = Movie.objects.get(title=request.POST['movie_name'])
        list_name_object = get_object_or_404(ListName, id=list_id)
        if ElementOfList.objects.filter(user=request.user, movie=selected_movie, list_name=list_name_object).exists():
            deleted_movie = ElementOfList.objects.get(user=request.user, movie=selected_movie,
                                                      list_name=list_name_object)
            deleted_movie.delete()
        return HttpResponseRedirect(reverse('users:custom_list', args=[list_id, request.user.username]))


class FollowUserView(View):
    def post(self, request, username):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        user = get_object_or_404(User, username=username)
        if not Following.objects.filter(follower=request.user, following=user).exists():
            new_following = Following(follower=request.user, following=user)
            new_following.save()

        followers_count = user.followers.count()
        following_count = user.followings.count()

        mutual_follow = (request.user.is_authenticated and Following.objects.filter(follower=request.user,
                                                                                    following=user).exists() and
                         Following.objects.filter(follower=user, following=request.user).exists())

        are_equal = request.user == user

        return JsonResponse({
            'status': 'followed',
            'unfollow_url': reverse('users:unfollow', args=[user.username]),
            'followers_count': followers_count,
            'following_count': following_count,
            'message': f'You are now following {user.username}',
            'mutual_follow_or_equal': mutual_follow or are_equal
        })


class UnfollowUserView(View):
    def post(self, request, username):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        user = get_object_or_404(User, username=username)
        if Following.objects.filter(follower=request.user, following=user).exists():
            following = Following.objects.get(follower=request.user, following=user)
            following.delete()

        followers_count = user.followers.count()
        following_count = user.followings.count()

        mutual_follow = (request.user.is_authenticated and Following.objects.filter(follower=request.user,
                                                                                    following=user).exists() and
                         Following.objects.filter(follower=user, following=request.user).exists())

        are_equal = request.user == user

        return JsonResponse({
            'status': 'unfollowed',
            'follow_url': reverse('users:follow', args=[user.username]),
            'followers_count': followers_count,
            'following_count': following_count,
            'message': f'You are no longer following {user.username}',
            'mutual_follow_or_equal': mutual_follow or are_equal
        })


@method_decorator(login_required, name='dispatch')
class ProfileUnfollowUserView(View):
    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        if Following.objects.filter(follower=request.user, following=user).exists():
            following = Following.objects.get(follower=request.user, following=user)
            following.delete()

        return HttpResponseRedirect(reverse('users:all_followings', args=[request.user.username]))


class AllFollowersView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        followers = Following.objects.filter(following=user).order_by('follower__username')
        are_equal = request.user == user
        followers_count = user.followers.count()
        mutual_follow = (request.user.is_authenticated and Following.objects.filter(follower=request.user,
                                                                                    following=user).exists() and
                         Following.objects.filter(follower=user, following=request.user).exists())
        mutual_follow_or_equal = mutual_follow or are_equal
        if not mutual_follow_or_equal:
            messages.error(request, "You do not have permission to view the followers of " + user.username +
                           ". In order to do that, you should follow each other mutually.")
        return render(request, "users/all_followers.html", {"followers": followers, "are_equal": are_equal,
                                                            "user": user, "followers_count": followers_count,
                                                            "permitted": mutual_follow_or_equal})


class AllFollowingsView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        followings = Following.objects.filter(follower=user).order_by('following__username')
        are_equal = request.user == user
        following_count = user.followings.count()
        mutual_follow = (request.user.is_authenticated and Following.objects.filter(follower=request.user,
                                                                                    following=user).exists() and
                         Following.objects.filter(follower=user, following=request.user).exists())
        mutual_follow_or_equal = mutual_follow or are_equal
        if not mutual_follow_or_equal:
            messages.error(request, "You do not have permission to view the followings of " + user.username +
                           ". In order to do that, you should follow each other mutually.")
        return render(request, "users/all_followings.html", {"followings": followings, "are_equal": are_equal,
                                                             "user": user, "following_count": following_count,
                                                             "permitted": mutual_follow_or_equal})


@method_decorator(login_required, name='dispatch')
class DeleteFollowerView(View):
    def post(self, request):
        selected_follower = User.objects.get(username=request.POST['selected_follower'])
        if Following.objects.filter(follower=selected_follower, following=request.user).exists():
            deleted_follower = Following.objects.get(follower=selected_follower, following=request.user)
            deleted_follower.delete()
            messages.success(request, selected_follower.username + ' is no longer your follower.')
            return HttpResponseRedirect(reverse('users:all_followers', args=[request.user.username]))


@method_decorator(login_required, name='dispatch')
class ProfileDeleteReviewView(View):
    def post(self, request):
        try:
            selected_review = Review.objects.get(pk=request.POST['review_id'], writer=request.user)
        except (KeyError, Review.DoesNotExist):
            messages.error(request, "Review does not exist.")
            return HttpResponseRedirect(reverse('users:all_reviews', args=[request.user.username]))
        else:
            selected_review.delete()
            messages.success(request, "Review has been deleted.")
            return HttpResponseRedirect(reverse('users:all_reviews', args=[request.user.username]))


class ReviewDetailView(View):
    def get(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)
        movie = review.movie
        writer = review.writer
        return render(request, 'users/review_detail.html', {'review': review, 'movie': movie, 'writer': writer})


@method_decorator(login_required, name='dispatch')
class DeleteListView(View):
    def post(self, request):
        try:
            selected_list = ListName.objects.get(pk=request.POST['list_id'], user=request.user)
        except (KeyError, ListName.DoesNotExist):
            messages.error(request, "List does not exist.")
            return HttpResponseRedirect(reverse('users:all_lists', args=[request.user.username]))
        else:
            selected_list.delete()
            messages.success(request, "List has been deleted.")
            return HttpResponseRedirect(reverse('users:all_lists', args=[request.user.username]))


class MoviesOfYearView(View):
    def get(self, request, year):
        paginator = Paginator(Movie.objects.filter(year=year).order_by('-pub_date', 'title'), 24)
        page_number = request.GET.get('page')
        movies = paginator.get_page(page_number)
        years = list(range(1900, timezone.now().year + 1))
        years.reverse()
        return render(request, 'users/movies_of_year.html', {'movies': movies, 'year': year, 'years': years})


class MostLikedMoviesView(View):
    def get(self, request):
        paginator = Paginator(Movie.objects.order_by('-likes', 'title')[:72], 24)
        page_number = request.GET.get('page')
        movies = paginator.get_page(page_number)
        return render(request, 'users/most_liked_movies.html', {'movies': movies})


@method_decorator(login_required, name='dispatch')
class FriendsWatchedRecentlyView(View):
    def get(self, request):
        paginator = Paginator(request.user.profile.get_last_watched()[:48], 24)
        page_number = request.GET.get('page')
        movies = paginator.get_page(page_number)
        return render(request, 'users/friends_watched_recently.html', {'movies': movies})


@method_decorator(login_required, name='dispatch')
class RecommendedMoviesView(View):
    def get(self, request):
        paginator = Paginator(recommend_movies_for_user(request.user)[:48], 24)
        page_number = request.GET.get('page')
        movies = paginator.get_page(page_number)
        return render(request, 'users/recommended_movies.html', {'movies': movies})


@method_decorator(login_required, name='dispatch')
class SimilarUsersView(View):
    def get(self, request):
        paginator = Paginator(User.objects.filter(id__in=recommend_friends_for_user(request.user)), 24)
        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)
        return render(request, 'users/similar_users.html', {'users': users})


class AllGenresView(View):
    def get(self, request):
        genres = Genre.objects.all()
        for genre in genres:
            genre.movie = Movie.objects.filter(genre=genre).last()
        return render(request, 'users/all_genres.html', {'genres': genres})


class AddListLikeView(View):
    def post(self, request, list_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        the_list = get_object_or_404(ListName, pk=list_id)
        if not LikedList.objects.filter(user=request.user, list_name=the_list).exists():
            liked_list = LikedList(user=request.user, list_name=the_list)
            liked_list.save()
            the_list.likes = F('likes') + 1
            the_list.save()

        return JsonResponse({
            'status': 'liked',
            'unlike_url': reverse('users:delete_list_like', args=[list_id]),
            'message': f'You liked {the_list.name}.',
        })


class DeleteListLikeView(View):
    def post(self, request, list_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        the_list = get_object_or_404(ListName, pk=list_id)
        if LikedList.objects.filter(user=request.user, list_name=the_list).exists():
            unliked_list = LikedList.objects.get(user=request.user, list_name=the_list)
            unliked_list.delete()
            the_list.likes = F('likes') - 1
            the_list.save()

        return JsonResponse({
            'status': 'unliked',
            'like_url': reverse('users:add_list_like', args=[list_id]),
            'message': f'You unliked {the_list.name}.',
        })


class FavouriteListsView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        lists = LikedList.objects.filter(user=user, list_name__is_private=False).order_by('-like_date',
                                                                                          'list_name__name')
        are_equal = request.user == user

        return render(request, 'users/favourite_lists.html', {'lists': lists, 'are_equal': are_equal, 'user': user})


class MakeListPublicView(View):
    def post(self, request, list_id, username):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        user = get_object_or_404(User, username=username)
        the_list = get_object_or_404(ListName, pk=list_id, user=user)

        are_equal = request.user == user

        if are_equal and the_list.is_private:
            the_list.is_private = False
            the_list.save()

        return JsonResponse({
            'status': 'public',
            'make_private_url': reverse('users:make_private', args=[list_id, username]),
            'message': f' {the_list.name} is public now.',
        })


class MakeListPrivateView(View):
    def post(self, request, list_id, username):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        user = get_object_or_404(User, username=username)
        the_list = get_object_or_404(ListName, pk=list_id, user=user)

        are_equal = request.user == user

        if are_equal and not the_list.is_private:
            the_list.is_private = True
            the_list.save()

        return JsonResponse({
            'status': 'private',
            'make_public_url': reverse('users:make_public', args=[list_id, username]),
            'message': f' {the_list.name} is private now.',
        })

