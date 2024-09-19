import requests
from django.core.management.base import BaseCommand
from movies.models import Movie


class Command(BaseCommand):
    help = 'Fetch YouTube trailer IDs for movies using the TMDb API'

    def handle(self, *args, **kwargs):
        api_key = 'cb3bc30b926d655f2e3e1d0507265fd8'  # Fetch TMDb API key from settings

        base_url = "https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}"

        # Loop through all movies in your database
        for movie in Movie.objects.all():
            if movie.trailer_id:  # Skip if the movie already has a trailer ID
                self.stdout.write(self.style.NOTICE(f'Skipping {movie.title}: already has a trailer.'))
                continue

            # First, find the movie ID on TMDb using its title
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie.title}"
            response = requests.get(search_url)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to search for {movie.title}.'))
                continue

            results = response.json().get('results', [])
            if not results:
                self.stdout.write(self.style.ERROR(f'No results found for {movie.title}.'))
                continue

            # Assume the first result is correct (handle edge cases with care)
            tmdb_movie_id = results[0]['id']

            # Now, fetch the videos (trailers) for this movie
            video_url = base_url.format(movie_id=tmdb_movie_id, api_key=api_key)
            video_response = requests.get(video_url)

            if video_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to fetch videos for {movie.title}.'))
                continue

            videos = video_response.json().get('results', [])
            youtube_trailer_id = None

            # Look for a YouTube trailer
            for video in videos:
                if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                    youtube_trailer_id = video['key']
                    break

            if youtube_trailer_id:
                # Save the trailer ID to the movie model
                movie.trailer_id = youtube_trailer_id
                movie.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully added trailer for {movie.title}.'))
            else:
                self.stdout.write(self.style.WARNING(f'No YouTube trailer found for {movie.title}.'))
