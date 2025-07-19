# Django integration for the hybrid recommendation system

from django.conf import settings
from django.core.cache import cache
import pandas as pd
import os
import threading
from datetime import datetime, timedelta
import logging

# Import your recommender (adjust the import path as needed)
from .recommender_system import HybridRecommender

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service class to handle recommendations in Django."""

    def __init__(self):
        self.recommender = None
        self.model_path = os.path.join(
            settings.BASE_DIR, "models", "hybrid_recommender.pkl"
        )
        self.last_trained = None
        self.training_lock = threading.Lock()

    def initialize(self):
        """Initialize the recommendation service."""
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        # Try to load existing model
        if os.path.exists(self.model_path):
            try:
                self.recommender = HybridRecommender()
                self.recommender.load_model(self.model_path)
                self.last_trained = datetime.fromtimestamp(
                    os.path.getmtime(self.model_path)
                )
                logger.info("Loaded existing recommendation model")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.recommender = None

        # If no model exists or loading failed, try to train a new one
        if self.recommender is None:
            self.train_model()

    def get_movies_dataframe(self):
        """Convert Django Movie model to pandas DataFrame."""
        from apis.models import Movie  # Adjust import path

        movies = Movie.objects.all().values(
            "id", "title", "genres", "director", "actors", "year", "plot_keywords"
        )

        df = pd.DataFrame(movies)
        if not df.empty:
            df.rename(columns={"id": "movie_id"}, inplace=True)

            # Handle null values
            df["genres"] = df["genres"].fillna("")
            df["director"] = df["director"].fillna("")
            df["actors"] = df["actors"].fillna("")
            df["plot_keywords"] = df["plot_keywords"].fillna("")
            df["year"] = pd.to_numeric(df["year"], errors="coerce")

        return df

    def get_ratings_dataframe(self):
        """Convert Django Rating model to pandas DataFrame."""
        from apis.models import Rating  # Adjust import path

        ratings = Rating.objects.all().values("user_id", "movie_id", "rating")
        df = pd.DataFrame(ratings)

        return df

    def train_model(self):
        """Train the recommendation model."""
        with self.training_lock:
            try:
                logger.info("Starting model training...")

                # Get data
                movies_df = self.get_movies_dataframe()
                ratings_df = self.get_ratings_dataframe()

                if movies_df.empty:
                    logger.warning("No movies in database - cannot train model")
                    return False

                if ratings_df.empty:
                    logger.warning("No ratings in database - training content-based only")
                    # Initialize recommender and train only content-based
                    self.recommender = HybridRecommender()
                    self.recommender.content_recommender.fit(movies_df)
                    self.recommender.is_trained = True  # Mark as partially trained
                else:
                    # Initialize and train full hybrid model
                    self.recommender = HybridRecommender()
                    self.recommender.fit(movies_df, ratings_df)

                # Save model
                self.recommender.save_model(self.model_path)
                self.last_trained = datetime.now()

                logger.info("Model training completed successfully")
                return True

            except Exception as e:
                logger.error(f"Model training failed: {e}")
                return False

    def should_retrain(self):
        """Check if model should be retrained based on data changes."""
        if self.last_trained is None:
            return True

        # Retrain if model is older than 24 hours
        if datetime.now() - self.last_trained > timedelta(hours=24):
            return True

        # Add more sophisticated logic here, e.g.:
        # - Check if new users/movies have been added
        # - Check if significant number of new ratings

        return False

    def get_fallback_recommendations(self, num_recommendations=10):
        """Get fallback recommendations when no model is available."""
        try:
            from apis.models import Movie

            # Get popular movies (you can customize this logic)
            popular_movies = Movie.objects.all().order_by('-vote_average', '-vote_count')[:num_recommendations]
            
            recommendations = []
            for movie in popular_movies:
                recommendations.append({
                    'movie_id': movie.id,
                    'score': 0.5,  # Default score
                    'title': movie.title,
                    'genres': movie.genres or '',
                    'year': movie.year
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get fallback recommendations: {e}")
            return []

    def get_recommendations(self, user_id, num_recommendations=10):
        """Get recommendations for a user."""
        cache_key = f"recommendations_{user_id}_{num_recommendations}"

        # Try to get from cache first
        cached_recs = cache.get(cache_key)
        if cached_recs:
            return cached_recs

        # Check if we need to retrain
        if self.should_retrain():
            self.train_model()

        # If no trained model, return fallback recommendations
        if self.recommender is None or not self.recommender.is_trained:
            logger.info(f"No trained model available, using fallback recommendations for user {user_id}")
            fallback_recs = self.get_fallback_recommendations(num_recommendations)
            # Cache fallback recommendations for shorter time (30 minutes)
            cache.set(cache_key, fallback_recs, 1800)
            return fallback_recs

        try:
            # Check if user exists in the collaborative filtering system
            if (hasattr(self.recommender.collaborative_recommender, 'user_id_map') and 
                user_id not in self.recommender.collaborative_recommender.user_id_map):
                logger.info(f"New user {user_id}, using fallback recommendations")
                fallback_recs = self.get_fallback_recommendations(num_recommendations)
                # Cache for shorter time for new users
                cache.set(cache_key, fallback_recs, 1800)
                return fallback_recs

            recommendations = self.recommender.get_user_recommendations(
                user_id, num_recommendations
            )

            # If no recommendations returned, use fallback
            if not recommendations:
                logger.info(f"No recommendations found for user {user_id}, using fallback")
                recommendations = self.get_fallback_recommendations(num_recommendations)

            # Cache recommendations for 1 hour
            cache.set(cache_key, recommendations, 3600)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get recommendations for user {user_id}: {e}")
            # Return fallback on any error
            fallback_recs = self.get_fallback_recommendations(num_recommendations)
            cache.set(cache_key, fallback_recs, 1800)
            return fallback_recs

    def update_with_rating(self, user_id, movie_id, rating):
        """Update the system with a new rating."""
        try:
            # Clear user's recommendation cache
            cache.delete_pattern(f"recommendations_{user_id}_*")

            # Log the update
            if self.recommender:
                self.recommender.update_with_new_rating(user_id, movie_id, rating)

            # In a production system, you might want to:
            # 1. Update the model incrementally
            # 2. Schedule a retrain job
            # 3. Use online learning techniques

        except Exception as e:
            logger.error(f"Failed to update with new rating: {e}")


# Singleton instance
recommendation_service = RecommendationService()
