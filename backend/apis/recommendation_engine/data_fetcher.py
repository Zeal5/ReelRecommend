# Movie Data Fetcher - Multiple data sources for movie information
# This module helps you fetch and process movie data from various sources

import requests
import pandas as pd
import json
import time
import logging
from typing import Dict, List, Optional
from django.conf import settings
import os
from datetime import datetime

from sklearn.preprocessing import add_dummy_feature

logger = logging.getLogger(__name__)


class MovieDataFetcher:
    """Fetches movie data from multiple sources."""

    def __init__(self):
        # You'll need to get API keys from these services
        self.tmdb_api_key = getattr(settings, "TMDB_API_KEY", None)
        self.omdb_api_key = getattr(settings, "OMDB_API_KEY", None)

        # Base URLs
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.omdb_base_url = "http://www.omdbapi.com/"

        # Rate limiting
        self.request_delay = 0.10  # 4 requests per second for TMDB

    def fetch_tmdb_popular_movies(self, num_pages=20):
        """Fetch popular movies from TMDB."""
        if not self.tmdb_api_key:
            logger.error("TMDB API key not configured")
            return []

        all_movies = []

        for page in range(1, num_pages + 1):
            print(f"Fetching TMDB page {page}")
            try:
                url = f"{self.tmdb_base_url}/movie/popular"
                params = {
                    "api_key": self.tmdb_api_key,
                    "page": page,
                    "language": "en-US",
                }

                response = requests.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                movies = data.get("results", [])

                for movie in movies:
                    processed_movie = self._process_tmdb_movie(movie)
                    if processed_movie:
                        all_movies.append(processed_movie)

                time.sleep(self.request_delay)

            except requests.RequestException as e:
                logger.error(f"Error fetching TMDB page {page}: {e}")
                continue

        return all_movies

    def fetch_tmdb_movie_details(self, movie_id):
        """Fetch detailed information for a specific TMDB movie."""
        if not self.tmdb_api_key:
            return None

        try:
            url = f"{self.tmdb_base_url}/movie/{movie_id}"
            params = {
                "api_key": self.tmdb_api_key,
                "append_to_response": "credits,keywords",
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return self._process_detailed_tmdb_movie(data)

        except requests.RequestException as e:
            logger.error(f"Error fetching TMDB movie {movie_id}: {e}")
            return None

    def _process_tmdb_movie(self, movie_data):
        """Process basic TMDB movie data."""
        try:
            return {
                "tmdb_id": movie_data["id"],
                "title": movie_data["title"],
                "overview": movie_data.get("overview", ""),
                "genres": "|".join([str(g) for g in movie_data.get("genre_ids", [])]),
                "year": int(movie_data.get("release_date", "2000-01-01")[:4]),
                "poster_url": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}",
                "popularity": movie_data.get("popularity", 0),
                "vote_average": movie_data.get("vote_average", 0),
                "vote_count": movie_data.get("vote_count", 0),
                "backdrop_url": f"https://image.tmdb.org/t/p/w500{movie_data.get('backdrop_path', '')}",
            }
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Error processing TMDB movie: {e}")
            return None

    def _process_detailed_tmdb_movie(self, movie_data):
        """Process detailed TMDB movie data with cast and crew."""
        try:
            # Extract cast (top 5 actors)
            cast = movie_data.get("credits", {}).get("cast", [])
            top_actors = [actor["name"] for actor in cast[:5]]

            # Extract director
            crew = movie_data.get("credits", {}).get("crew", [])
            directors = [
                member["name"] for member in crew if member["job"] == "Director"
            ]

            # Extract keywords
            keywords = movie_data.get("keywords", {}).get("keywords", [])
            plot_keywords = [kw["name"] for kw in keywords[:10]]

            return {
                "tmdb_id": movie_data["id"],
                "imdb_id": movie_data.get("imdb_id", ""),
                "title": movie_data["title"],
                "overview": movie_data.get("overview", ""),
                "genres": "|".join([g["name"] for g in movie_data.get("genres", [])]),
                "year": int(movie_data.get("release_date", "2000-01-01")[:4]),
                "director": "|".join(directors),
                "actors": "|".join(top_actors),
                "plot_keywords": "|".join(plot_keywords),
                "poster_url": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}",
                "backdrop_url": f"https://image.tmdb.org/t/p/w500{movie_data.get('backdrop_path', '')}",
                "popularity": movie_data.get("popularity", 0),
                "vote_average": movie_data.get("vote_average", 0),
                "vote_count": movie_data.get("vote_count", 0),
                "runtime": movie_data.get("runtime", 0),
                "budget": movie_data.get("budget", 0),
                "revenue": movie_data.get("revenue", 0),
            }
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Error processing detailed TMDB movie: {e}")
            return None

    def search_movie(self, query):
        """Search for movies by title."""
        if not self.tmdb_api_key:
            return []

        try:
            url = f"{self.tmdb_base_url}/search/movie"
            params = {"api_key": self.tmdb_api_key, "query": query, "language": "en-US"}

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            movies = data.get("results", [])

            return [self._process_tmdb_movie(movie) for movie in movies]

        except requests.RequestException as e:
            logger.error(f"Error searching for movie '{query}': {e}")
            return []


class DataProcessor:
    """Process and update movie data in Django."""

    def __init__(self):
        self.movie_fetcher = MovieDataFetcher()

    def populate_database_from_tmdb(self, num_movies=1000):
        """Populate database with movies from TMDB."""
        from apis.models import Movie  # Adjust import path

        # Calculate how many pages we need (20 movies per page)
        num_pages = (num_movies // 20) + 1

        movies = self.movie_fetcher.fetch_tmdb_popular_movies(num_pages)

        created_count = 0
        updated_count = 0

        for movie_data in movies[:num_movies]:
            try:
                # Get detailed information
                detailed_movie = self.movie_fetcher.fetch_tmdb_movie_details(
                    movie_data["tmdb_id"]
                )

                if detailed_movie:
                    movie_data.update(detailed_movie)

                print(
                    f"{movie_data.get('title'):<50}CREATED: {created_count} | UPDATED: {updated_count} | TOTAL: {created_count + updated_count}",
                )
                # Create or update movie in database
                movie, created = Movie.objects.update_or_create(
                    tmdb_id=movie_data["tmdb_id"],
                    defaults={
                        "title": movie_data["title"],
                        "genres": movie_data.get("genres", ""),
                        "director": movie_data.get("director", ""),
                        "actors": movie_data.get("actors", ""),
                        "year": movie_data.get("year"),
                        "plot_keywords": movie_data.get("plot_keywords", ""),
                        "poster_url": movie_data.get("poster_url", ""),
                        "overview": movie_data.get("overview", ""),
                        "imdb_id": movie_data.get("imdb_id", ""),
                        "backdrop_url": movie_data.get("backdrop_url", ""),
                        "popularity": movie_data.get("popularity", 0),
                        "vote_average": movie_data.get("vote_average", 0),
                        "vote_count": movie_data.get("vote_count", 0),
                    },
                )
                new_backdrop_url = movie_data.get("backdrop_url", "")
                popularity = movie_data.get("popularity", 0)
                vote_average = movie_data.get("vote_average", 0)
                vote_count = movie_data.get("vote_count", 0)
                adult = movie_data.get("adult", False)

                print(adult, movie.adult)
                if movie.adult != adult:
                    movie.adult = adult
                    movie.save(update_fields=["adult"])

                if popularity and movie.popularity != popularity:
                    movie.popularity = popularity
                    movie.save(update_fields=["popularity"])

                if vote_average and movie.vote_average != vote_average:
                    movie.vote_average = vote_average
                    movie.save(update_fields=["vote_average"])

                if vote_count and movie.vote_count != vote_count:
                    movie.vote_count = vote_count
                    movie.save(update_fields=["vote_count"])

                if new_backdrop_url and movie.backdrop_url != new_backdrop_url:
                    movie.backdrop_url = new_backdrop_url
                    movie.save(update_fields=["backdrop_url"])

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                time.sleep(0.04)  # Rate limiting

            except Exception as e:
                logger.error(f"Error processing movie {movie_data.get('title')}: {e}")
                continue

        logger.info(
            f"Database population completed: {created_count} created, {updated_count} updated"
        )
        return created_count, updated_count

    def update_movie_details(self, movie_id):
        """Update detailed information for a specific movie."""
        from apis.models import Movie

        try:
            movie = Movie.objects.get(id=movie_id)

            if movie.tmdb_id:
                detailed_data = self.movie_fetcher.fetch_tmdb_movie_details(
                    movie.tmdb_id
                )

                if detailed_data:
                    for key, value in detailed_data.items():
                        if hasattr(movie, key) and value:
                            setattr(movie, key, value)

                    movie.save()
                    logger.info(f"Updated movie: {movie.title}")
                    return True

        except Movie.DoesNotExist:
            logger.error(f"Movie with ID {movie_id} not found")
        except Exception as e:
            logger.error(f"Error updating movie {movie_id}: {e}")

        return False


# Real-time update processor for user interactions
class RealtimeUpdateProcessor:
    """Process real-time user interactions and update recommendations."""

    def __init__(self, recommendation_service):
        self.recommendation_service = recommendation_service

    def process_rating(self, user_id, movie_id, rating):
        """Process a new rating."""
        try:
            # Save to database (this should be done in your view)
            from apis.models import Rating
            from django.contrib.auth.models import User

            user = User.objects.get(id=user_id)
            movie = Movie.objects.get(id=movie_id)

            rating_obj, created = Rating.objects.update_or_create(
                user=user, movie=movie, defaults={"rating": rating}
            )

            # Update recommendation service
            self.recommendation_service.update_with_rating(user_id, movie_id, rating)

            # Clear user's cached recommendations
            from django.core.cache import cache

            cache.delete_pattern(f"recommendations_{user_id}_*")

            return True

        except Exception as e:
            logger.error(f"Error processing rating: {e}")
            return False

    def process_view(self, user_id, movie_id):
        """Process a movie view."""
        return self._process_interaction(user_id, movie_id, "view", 1.0)

    def process_like(self, user_id, movie_id):
        """Process a movie like."""
        return self._process_interaction(user_id, movie_id, "like", 4.0)

    def process_dislike(self, user_id, movie_id):
        """Process a movie dislike."""
        return self._process_interaction(user_id, movie_id, "dislike", 2.0)

    def _process_interaction(
        self, user_id, movie_id, interaction_type, implicit_rating
    ):
        """Process a generic interaction."""
        try:
            from apis.models import UserInteraction, Movie
            from django.contrib.auth import get_user_model

            User = get_user_model()

            user = User.objects.get(id=user_id)
            movie = Movie.objects.get(id=movie_id)

            # Save interaction
            UserInteraction.objects.create(
                user=user, movie=movie, interaction_type=interaction_type
            )

            # Update recommendation system with implicit rating
            self.recommendation_service.update_with_rating(
                user_id, movie_id, implicit_rating
            )

            return True

        except Exception as e:
            logger.error(f"Error processing {interaction_type}: {e}")
            return False
