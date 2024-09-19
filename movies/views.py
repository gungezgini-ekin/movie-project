from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages

from .forms import ReviewForm
from .models import Movie, Director, Genre, Review
from django.db.models import F
from users.models import User, LikedMovie, WantToWatchMovie, ElementOfList, ListName, WatchedMovie
from django.core.paginator import Paginator

# Create your views here.


class MovieDetailView(View):
    def get(self, request, name):
        movie = get_object_or_404(Movie, title=name)
        if request.user.is_authenticated:
            user_lists = ListName.objects.filter(user=request.user)
            liked = LikedMovie.objects.filter(movie=movie, user=request.user).exists()
            want_to_watch = WantToWatchMovie.objects.filter(movie=movie, user=request.user).exists()
            watched = WatchedMovie.objects.filter(movie=movie, user=request.user).exists()
        else:
            user_lists = []
            liked = False
            want_to_watch = False
            watched = False
        paginator = Paginator(movie.review_set.all().order_by('-review_date'), 5)
        page_number = request.GET.get('page')
        reviews = paginator.get_page(page_number)
        avg_rating = movie.get_avg_rating()
        return render(request, 'movies/movie_detail.html', {'movie': movie, 'user_lists': user_lists,
                                                            'liked': liked, 'want_to_watch': want_to_watch,
                                                            'watched': watched, "avg_rating": avg_rating,
                                                            'reviews': reviews})


@method_decorator(login_required, name='dispatch')
class AddReviewView(View):
    def get(self, request, name):
        movie = get_object_or_404(Movie, title=name)
        form = ReviewForm()
        return render(request, 'movies/add_review.html', {'movie': movie, 'form': form})

    def post(self, request, name):
        movie = get_object_or_404(Movie, title=name)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            # we didn't save to database now because we'll also add movie and writer
            review.movie = movie
            review.writer = request.user
            review.save()
            messages.success(request, 'Your review has been added.')
            return HttpResponseRedirect(reverse('movies:movie_detail', args=[movie.title]))
        else:
            messages.error(request, 'Error, please add the review again.')
            return HttpResponseRedirect(reverse('movies:add_review', args=[movie.title]))


class AddLikeMovieView(View):
    def post(self, request, name):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        movie = get_object_or_404(Movie, title=name)
        if not LikedMovie.objects.filter(user=request.user, movie=movie).exists():
            liked_movie = LikedMovie(user=request.user, movie=movie)
            liked_movie.save()
            movie.likes = F("likes") + 1
            movie.save()

        return JsonResponse({
            'status': 'liked',
            'unlike_url': reverse('movies:delete_like', args=[movie.title]),
            'message': f'You liked {movie.title}.',
        })


class AddWantToWatchView(View):
    def post(self, request, name):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        movie = get_object_or_404(Movie, title=name)
        if not WantToWatchMovie.objects.filter(user=request.user, movie=movie).exists():
            want_movie = WantToWatchMovie(user=request.user, movie=movie)
            want_movie.save()

        return JsonResponse({
            'status': 'want_to_watch',
            'delete_want_to_url': reverse('movies:delete_from_watchlist', args=[movie.title]),
            'message': f'{movie.title} is added to watchlist.',
        })


@method_decorator(login_required, name='dispatch')
class AddMovieToList(View):
    def post(self, request, name):
        movie = get_object_or_404(Movie, title=name)
        try:
            selected_list = ListName.objects.get(id=request.POST['list_id'], user=request.user)
        except (KeyError, ListName.DoesNotExist):
            return render(
                request,
                "movies/movie_detail.html",
                {
                    "movie": movie,
                    "user_lists": ListName.objects.filter(user=request.user),
                },
            )
        else:
            if not ElementOfList.objects.filter(list_name=selected_list, movie=movie, user=request.user).exists():
                new_element = ElementOfList(movie=movie, list_name=selected_list, user=request.user)
                new_element.save()
                selected_list.save()
            return HttpResponseRedirect(reverse("movies:movie_detail", args=[movie.title]))


class DeleteLikedMovieView(View):
    def post(self, request, name):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        movie = get_object_or_404(Movie, title=name)
        if LikedMovie.objects.filter(user=request.user, movie=movie).exists():
            liked_movie = LikedMovie.objects.get(user=request.user, movie=movie)
            liked_movie.delete()
            movie.likes = F("likes") - 1
            movie.save()

        return JsonResponse({
            'status': 'unliked',
            'like_url': reverse('movies:like_movie', args=[movie.title]),
            'message': f'You unliked {movie.title}.',
        })


class DeleteWantToWatchMovieView(View):
    def post(self, request, name):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        movie = get_object_or_404(Movie, title=name)
        if WantToWatchMovie.objects.filter(user=request.user, movie=movie).exists():
            want_movie = WantToWatchMovie.objects.get(user=request.user, movie=movie)
            want_movie.delete()

        return JsonResponse({
            'status': 'not_want_to_watch',
            'add_want_to_url': reverse('movies:want_to_watch', args=[movie.title]),
            'message': f'{movie.title} is deleted from watchlist.',
        })


class DirectorDetailView(View):
    def get(self, request, name):
        director = get_object_or_404(Director, name=name)
        movies = Movie.objects.filter(director=director).order_by('year')
        return render(request, 'movies/director_detail.html', {'movies': movies, 'director': director})


class GenreDetailView(View):
    def get(self, request, name):
        genre = get_object_or_404(Genre, name=name)
        paginator = Paginator(genre.movie_set.all().order_by('title'), 24)
        page_number = request.GET.get('page')
        movies = paginator.get_page(page_number)
        return render(request, 'movies/genre_detail.html', {'movies': movies, 'genre': genre})


class AddWatchedMovieView(View):
    def post(self, request, name):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        movie = get_object_or_404(Movie, title=name)
        if not WatchedMovie.objects.filter(user=request.user, movie=movie).exists():
            watched_movie = WatchedMovie(user=request.user, movie=movie)
            watched_movie.save()

        return JsonResponse({
            'status': 'watched',
            'delete_watched_url': reverse('movies:delete_from_watched', args=[movie.title]),
            'message': f'{movie.title} is marked as watched.',
        })


class DeleteWatchedMovieView(View):
    def post(self, request, name):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You are not authenticated'}, status=401)

        movie = get_object_or_404(Movie, title=name)
        if WatchedMovie.objects.filter(user=request.user, movie=movie).exists():
            watched_movie = WatchedMovie.objects.get(user=request.user, movie=movie)
            watched_movie.delete()

        return JsonResponse({
            'status': 'not_watched',
            'add_watched_url': reverse('movies:add_watched', args=[movie.title]),
            'message': f'{movie.title} is deleted from watched movies.',
        })


@method_decorator(login_required, name='dispatch')
class DeleteReviewView(View):
    def post(self, request, name):
        movie = get_object_or_404(Movie, title=name)
        try:
            selected_review = Review.objects.get(pk=request.POST['review_id'], writer=request.user, movie=movie)
        except (KeyError, Review.DoesNotExist):
            messages.error(request, "Review does not exist.")
            return HttpResponseRedirect(reverse('movies:movie_detail', args=[name]))
        else:
            selected_review.delete()
            messages.success(request, "Review has been deleted.")
            return HttpResponseRedirect(reverse('movies:movie_detail', args=[name]))


class ReviewDetailView(View):
    def get(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)
        movie = review.movie
        writer = review.writer
        return render(request, 'movies/review_detail.html', {'review': review, 'movie': movie, 'writer': writer})




