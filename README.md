# Movie Application

This is a movie management web application built using **Django**. It allows users to create profiles, follow other users, create and manage movie lists, write reviews, like/unlike movies, and search for movies, directors, genres, and more using **Elasticsearch**. The application also features **AJAX** for seamless interactions without page reloads.

## Features

- **User Authentication**: Users can sign up, log in, and manage their profiles.
- **Movie Management**:
  - Users can create movie lists (public or private), write reviews, rate movies, and mark movies as watched.
  - Users can like/unlike movies.
- **Social Features**:
  - Users can follow/unfollow each other.
  - AJAX-based interactions to follow/unfollow, like/unlike movies, and manage lists.
- **Search Functionality**:
  - Powered by **Elasticsearch** for movie, director, genre, and user search.
  - Supports fuzzy and partial matches.
- **Recommendations**:
  - Basic user-user collaborative filtering for movie recommendations.
  - Shows recommended movies based on user preferences.
- **Trailers**: Movie details pages include trailers fetched from TMDb, displayed in a modal window.
