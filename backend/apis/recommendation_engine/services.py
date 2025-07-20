# Enhanced services.py with better logging and monitoring

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
    """Enhanced service class to handle recommendations in Django."""

    def __init__(self):
        self.recommender = None
        self.model_path = os.path.join(
            settings.BASE_DIR, "models", "hybrid_recommender.pkl"
        )
        self.last_trained = None
        self.training_lock = threading.Lock()
        self.model_version = None  # Track model version
        self.initialization_time = None
        self.stats = {
            'total_recommendations_served': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'fallback_recommendations': 0,
            'personalized_recommendations': 0,
        }

    def initialize(self):
        """Initialize the recommendation service with detailed logging."""
        logger.info("Initializing recommendation service...")
        self.initialization_time = datetime.now()
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        # Try to load existing model
        if os.path.exists(self.model_path):
            try:
                logger.info(f"Loading existing model from: {self.model_path}")
                self.recommender = HybridRecommender()
                self.recommender.load_model(self.model_path)
                
                self.last_trained = datetime.fromtimestamp(
                    os.path.getmtime(self.model_path)
                )
                self.model_version = self._generate_model_version()
                
                logger.info(f"✅ Successfully loaded recommendation model (Version: {self.model_version})")
                logger.info(f"📅 Model last trained: {self.last_trained.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Log model capabilities
                self._log_model_capabilities()
                
            except Exception as e:
                logger.error(f"❌ Failed to load existing model: {e}")
                self.recommender = None

        # If no model exists or loading failed, try to train a new one
        if self.recommender is None:
            logger.warning("No valid model found, attempting to train new model...")
            self.train_model()

    def _generate_model_version(self):
        """Generate a model version identifier."""
        if self.last_trained:
            return f"v{self.last_trained.strftime('%Y%m%d_%H%M%S')}"
        return f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _log_model_capabilities(self):
        """Log what the current model can do."""
        if not self.recommender:
            return
            
        capabilities = []
        
        if hasattr(self.recommender, 'is_trained') and self.recommender.is_trained:
            capabilities.append("✅ Content-based filtering")
            
        if hasattr(self.recommender, 'has_collaborative_data') and self.recommender.has_collaborative_data:
            capabilities.append("✅ Collaborative filtering")
            
            # Log collaborative filtering stats
            if hasattr(self.recommender.collaborative_recommender, 'user_id_map'):
                cf = self.recommender.collaborative_recommender
                logger.info(f"📊 Collaborative filtering trained on {len(cf.user_id_map)} users and {len(cf.movie_id_map)} movies")
        else:
            capabilities.append("❌ Collaborative filtering (insufficient data)")
            
        logger.info(f"🎯 Model capabilities: {', '.join(capabilities)}")

    def get_movies_dataframe(self):
        """Convert Django Movie model to pandas DataFrame with logging."""
        from apis.models import Movie  # Adjust import path
        
        logger.debug("Fetching movies from database...")
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
            
            logger.info(f"📚 Loaded {len(df)} movies from database")
        else:
            logger.warning("⚠️ No movies found in database")

        return df

    def get_ratings_dataframe(self):
        """Convert Django Rating model to pandas DataFrame with logging."""
        from apis.models import Rating  # Adjust import path
        
        logger.debug("Fetching ratings from database...")
        ratings = Rating.objects.all().values("user_id", "movie_id", "rating")
        df = pd.DataFrame(ratings)
        
        if not df.empty:
            logger.info(f"⭐ Loaded {len(df)} ratings from database")
            
            # Log some statistics
            unique_users = df['user_id'].nunique()
            unique_movies = df['movie_id'].nunique()
            avg_rating = df['rating'].mean()
            
            logger.info(f"📊 Ratings stats: {unique_users} users, {unique_movies} movies, avg rating: {avg_rating:.2f}")
        else:
            logger.warning("⚠️ No ratings found in database")

        return df

    def train_model(self):
        """Train the recommendation model with detailed logging."""
        with self.training_lock:
            try:
                logger.info("🚀 Starting recommendation model training...")
                training_start = datetime.now()

                # Get data
                movies_df = self.get_movies_dataframe()
                ratings_df = self.get_ratings_dataframe()

                if movies_df.empty:
                    logger.error("❌ No movies in database - cannot train model")
                    return False

                if ratings_df.empty:
                    logger.warning("⚠️ No ratings in database - training content-based only")
                    # Initialize recommender and train only content-based
                    self.recommender = HybridRecommender()
                    self.recommender.content_recommender.fit(movies_df)
                    self.recommender.is_trained = True  # Mark as partially trained
                    self.recommender.has_collaborative_data = False
                else:
                    # Initialize and train full hybrid model
                    logger.info("🔄 Training hybrid model (content + collaborative)...")
                    self.recommender = HybridRecommender()
                    self.recommender.fit(movies_df, ratings_df)

                # Save model
                logger.info(f"💾 Saving model to: {self.model_path}")
                self.recommender.save_model(self.model_path)
                self.last_trained = datetime.now()
                self.model_version = self._generate_model_version()

                training_duration = (datetime.now() - training_start).total_seconds()
                
                logger.info(f"✅ Model training completed successfully in {training_duration:.2f} seconds")
                logger.info(f"🏷️ New model version: {self.model_version}")
                
                # Log model capabilities
                self._log_model_capabilities()
                
                # Clear all cached recommendations since we have a new model
                logger.info("🧹 Clearing recommendation cache...")
                try:
                    cache.clear()
                    logger.info("✅ Cache cleared successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clear cache: {e}")
                
                return True

            except Exception as e:
                logger.error(f"❌ Model training failed: {e}")
                return False

    def should_retrain(self):
        """Check if model should be retrained based on data changes."""
        if self.last_trained is None:
            logger.info("🔄 Model needs training (never trained)")
            return True

        # Retrain if model is older than 24 hours
        if datetime.now() - self.last_trained > timedelta(hours=24):
            logger.info("🔄 Model needs retraining (older than 24 hours)")
            return True

        # Add more sophisticated logic here, e.g.:
        # - Check if new users/movies have been added
        # - Check if significant number of new ratings

        return False

    def get_fallback_recommendations(self, num_recommendations=10):
        """Get fallback recommendations with logging."""
        try:
            logger.debug(f"🎲 Generating {num_recommendations} fallback recommendations...")
            
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
            
            self.stats['fallback_recommendations'] += 1
            logger.debug(f"✅ Generated {len(recommendations)} fallback recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get fallback recommendations: {e}")
            return []

    def get_recommendations(self, user_id, num_recommendations=10):
        """Get recommendations for a user with detailed logging."""
        start_time = datetime.now()
        cache_key = f"recommendations_{user_id}_{num_recommendations}"
        
        logger.debug(f"🎯 Getting {num_recommendations} recommendations for user {user_id}")

        # Try to get from cache first
        cached_recs = cache.get(cache_key)
        if cached_recs:
            self.stats['cache_hits'] += 1
            self.stats['total_recommendations_served'] += 1
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.debug(f"⚡ Cache hit for user {user_id} ({duration:.2f}ms)")
            return cached_recs

        self.stats['cache_misses'] += 1

        # Check if we need to retrain
        if self.should_retrain():
            logger.info("🔄 Retraining model before generating recommendations...")
            self.train_model()

        # If no trained model, return fallback recommendations
        if self.recommender is None or not self.recommender.is_trained:
            logger.info(f"🎲 No trained model available, using fallback for user {user_id}")
            fallback_recs = self.get_fallback_recommendations(num_recommendations)
            # Cache fallback recommendations for shorter time (30 minutes)
            cache.set(cache_key, fallback_recs, 1800)
            self.stats['total_recommendations_served'] += 1
            return fallback_recs

        try:
            # Check if user exists in the collaborative filtering system
            is_new_user = False
            if (hasattr(self.recommender.collaborative_recommender, 'user_id_map') and 
                user_id not in self.recommender.collaborative_recommender.user_id_map):
                is_new_user = True
                logger.debug(f"👤 New user {user_id}, using fallback recommendations")
                
            if is_new_user:
                fallback_recs = self.get_fallback_recommendations(num_recommendations)
                # Cache for shorter time for new users
                cache.set(cache_key, fallback_recs, 1800)
                self.stats['total_recommendations_served'] += 1
                return fallback_recs

            # Generate personalized recommendations
            logger.debug(f"🎯 Generating personalized recommendations for user {user_id}")
            recommendations = self.recommender.get_user_recommendations(
                user_id, num_recommendations
            )

            # If no recommendations returned, use fallback
            if not recommendations:
                logger.info(f"🎲 No personalized recommendations found for user {user_id}, using fallback")
                recommendations = self.get_fallback_recommendations(num_recommendations)
            else:
                self.stats['personalized_recommendations'] += 1
                logger.debug(f"✅ Generated {len(recommendations)} personalized recommendations for user {user_id}")

            # Cache recommendations for 1 hour
            cache.set(cache_key, recommendations, 3600)
            self.stats['total_recommendations_served'] += 1

            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.debug(f"⏱️ Recommendation generation completed in {duration:.2f}ms")

            return recommendations

        except Exception as e:
            logger.error(f"❌ Failed to get recommendations for user {user_id}: {e}")
            # Return fallback on any error
            fallback_recs = self.get_fallback_recommendations(num_recommendations)
            cache.set(cache_key, fallback_recs, 1800)
            self.stats['total_recommendations_served'] += 1
            return fallback_recs

    def update_with_rating(self, user_id, movie_id, rating):
        """Update the system with a new rating."""
        try:
            logger.debug(f"📝 Processing new rating: User {user_id}, Movie {movie_id}, Rating {rating}")
            
            # Clear user's recommendation cache
            cache.delete_pattern(f"recommendations_{user_id}_*")
            logger.debug(f"🧹 Cleared cache for user {user_id}")

            # Log the update
            if self.recommender:
                self.recommender.update_with_new_rating(user_id, movie_id, rating)

            # In a production system, you might want to:
            # 1. Update the model incrementally
            # 2. Schedule a retrain job
            # 3. Use online learning techniques

        except Exception as e:
            logger.error(f"❌ Failed to update with new rating: {e}")

    def get_service_stats(self):
        """Get service statistics."""
        stats = self.stats.copy()
        stats.update({
            'model_version': self.model_version,
            'last_trained': self.last_trained.isoformat() if self.last_trained else None,
            'initialization_time': self.initialization_time.isoformat() if self.initialization_time else None,
            'model_file_exists': os.path.exists(self.model_path),
            'is_trained': self.recommender.is_trained if self.recommender else False,
        })
        return stats

    def log_service_stats(self):
        """Log current service statistics."""
        stats = self.get_service_stats()
        logger.info("📊 Recommendation Service Statistics:")
        logger.info(f"  Total recommendations served: {stats['total_recommendations_served']}")
        logger.info(f"  Cache hits: {stats['cache_hits']}")
        logger.info(f"  Cache misses: {stats['cache_misses']}")
        logger.info(f"  Personalized recommendations: {stats['personalized_recommendations']}")
        logger.info(f"  Fallback recommendations: {stats['fallback_recommendations']}")
        logger.info(f"  Current model version: {stats['model_version']}")


# Singleton instance
recommendation_service = RecommendationService()


