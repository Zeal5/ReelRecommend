import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import pickle
import os
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """Content-based recommendation using movie features like genres, directors, actors."""

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000, stop_words="english", ngram_range=(1, 2)
        )
        self.content_matrix = None
        self.movies_df = None
        self.similarity_matrix = None

    def prepare_content_features(self, movies_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare content features by combining genres, directors, actors, etc."""
        movies_df = movies_df.copy()

        # Combine features into a single text field
        def create_content_soup(row):
            features = []

            # Add genres (give more weight by repeating)
            if pd.notna(row.get("genres")):
                genres = str(row["genres"]).lower().replace("|", " ")
                features.extend([genres] * 3)  # Give genres more weight

            # Add director
            if pd.notna(row.get("director")):
                director = str(row["director"]).lower().replace(" ", "_")
                features.extend([director] * 2)  # Give director good weight

            # Add top actors
            if pd.notna(row.get("actors")):
                actors = str(row["actors"]).lower().replace("|", " ").replace(" ", "_")
                features.append(actors)

            # Add keywords/plot keywords
            if pd.notna(row.get("plot_keywords")):
                keywords = str(row["plot_keywords"]).lower().replace("|", " ")
                features.append(keywords)

            # Add year decade for time-based similarity
            if pd.notna(row.get("year")):
                decade = f"decade_{int(row['year']) // 10 * 10}s"
                features.append(decade)

            return " ".join(features)

        movies_df["content_soup"] = movies_df.apply(create_content_soup, axis=1)
        return movies_df

    def fit(self, movies_df: pd.DataFrame):
        """Train the content-based recommender."""
        logger.info("Training content-based recommender...")

        self.movies_df = self.prepare_content_features(movies_df)

        # Create TF-IDF matrix
        self.content_matrix = self.tfidf_vectorizer.fit_transform(
            self.movies_df["content_soup"]
        )

        # Compute similarity matrix (only for small datasets, otherwise compute on-demand)
        if len(self.movies_df) < 10000:
            self.similarity_matrix = cosine_similarity(self.content_matrix)

        logger.info(f"Content-based model trained on {len(self.movies_df)} movies")

    def get_recommendations(
        self, movie_id: int, n_recommendations: int = 10
    ) -> List[Tuple[int, float]]:
        """Get content-based recommendations for a movie."""
        try:
            movie_idx = self.movies_df[self.movies_df["movie_id"] == movie_id].index[0]

            if self.similarity_matrix is not None:
                # Use precomputed similarity matrix
                sim_scores = self.similarity_matrix[movie_idx]
            else:
                # Compute similarity on-demand
                movie_vector = self.content_matrix[movie_idx]
                sim_scores = cosine_similarity(
                    movie_vector, self.content_matrix
                ).flatten()

            # Get most similar movies
            similar_indices = np.argsort(sim_scores)[::-1][1 : n_recommendations + 1]

            recommendations = []
            for idx in similar_indices:
                movie_id_rec = self.movies_df.iloc[idx]["movie_id"]
                score = sim_scores[idx]
                recommendations.append((movie_id_rec, score))

            return recommendations

        except (IndexError, KeyError) as e:
            logger.warning(
                f"Movie {movie_id} not found for content-based recommendations"
            )
            return []


class CollaborativeFilteringRecommender:
    """Collaborative filtering using matrix factorization (SVD)."""

    def __init__(self, n_components=100, random_state=42):  # @DEV change to 100
        self.svd = TruncatedSVD(n_components=n_components, random_state=random_state)
        self.user_item_matrix = None
        self.user_factors = None
        self.item_factors = None
        self.user_id_map = {}
        self.movie_id_map = {}
        self.reverse_user_map = {}
        self.reverse_movie_map = {}
        self.global_mean = 0

    def create_user_item_matrix(self, ratings_df: pd.DataFrame) -> csr_matrix:
        """Create user-item interaction matrix."""
        # Create mappings
        unique_users = ratings_df["user_id"].unique()
        unique_movies = ratings_df["movie_id"].unique()

        self.user_id_map = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.movie_id_map = {
            movie_id: idx for idx, movie_id in enumerate(unique_movies)
        }
        self.reverse_user_map = {
            idx: user_id for user_id, idx in self.user_id_map.items()
        }
        self.reverse_movie_map = {
            idx: movie_id for movie_id, idx in self.movie_id_map.items()
        }

        # Create matrix
        n_users = len(unique_users)
        n_movies = len(unique_movies)

        user_indices = ratings_df["user_id"].map(self.user_id_map)
        movie_indices = ratings_df["movie_id"].map(self.movie_id_map)

        matrix = csr_matrix(
            (ratings_df["rating"], (user_indices, movie_indices)),
            shape=(n_users, n_movies),
        )

        return matrix

    def fit(self, ratings_df: pd.DataFrame):
        """Train the collaborative filtering model."""
        logger.info("Training collaborative filtering recommender...")

        self.user_item_matrix = self.create_user_item_matrix(ratings_df)
        self.global_mean = ratings_df["rating"].mean()

        # Apply SVD
        self.user_factors = self.svd.fit_transform(self.user_item_matrix)
        self.item_factors = self.svd.components_.T

        logger.info(
            f"Collaborative filtering model trained on {len(self.user_id_map)} users and {len(self.movie_id_map)} movies"
        )

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """Predict rating for a user-movie pair."""
        if user_id not in self.user_id_map or movie_id not in self.movie_id_map:
            return self.global_mean

        user_idx = self.user_id_map[user_id]
        movie_idx = self.movie_id_map[movie_id]

        prediction = np.dot(self.user_factors[user_idx], self.item_factors[movie_idx])
        return prediction

    def get_user_recommendations(
        self, user_id: int, n_recommendations: int = 10, exclude_rated: bool = True
    ) -> List[Tuple[int, float]]:
        """Get collaborative filtering recommendations for a user."""
        if user_id not in self.user_id_map:
            return []

        user_idx = self.user_id_map[user_id]

        # Get all predicted ratings for this user
        predicted_ratings = np.dot(self.user_factors[user_idx], self.item_factors.T)

        if exclude_rated:
            # Exclude already rated movies
            rated_movies = self.user_item_matrix[user_idx].nonzero()[1]
            predicted_ratings[rated_movies] = -np.inf

        # Get top recommendations
        top_movie_indices = np.argsort(predicted_ratings)[::-1][:n_recommendations]

        recommendations = []
        for movie_idx in top_movie_indices:
            movie_id = self.reverse_movie_map[movie_idx]
            score = predicted_ratings[movie_idx]
            if score > -np.inf:  # Valid prediction
                recommendations.append((movie_id, score))

        return recommendations


class HybridRecommender:
    """Hybrid recommender combining collaborative and content-based filtering."""

    def __init__(self, content_weight=0.3, collaborative_weight=0.7):
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_recommender = CollaborativeFilteringRecommender()
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        self.is_trained = False
        self.has_collaborative_data = False

    def fit(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        """Train both recommenders."""
        logger.info("Training hybrid recommender...")

        # Always train content-based recommender
        self.content_recommender.fit(movies_df)

        # Train collaborative only if we have ratings data
        if not ratings_df.empty and len(ratings_df) >= 10:  # Minimum threshold
            self.collaborative_recommender.fit(ratings_df)
            self.has_collaborative_data = True
            logger.info("Trained both content-based and collaborative filtering")
        else:
            logger.info("Insufficient ratings data - trained content-based only")
            self.has_collaborative_data = False

        self.is_trained = True
        logger.info("Hybrid recommender training completed")

    def get_user_recommendations(
        self, user_id: int, n_recommendations: int = 10
    ) -> List[Dict]:
        """Get hybrid recommendations for a user."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")

        # If no collaborative data, use content-based with popular movies
        if not self.has_collaborative_data:
            return self._get_content_based_recommendations(n_recommendations)

        # Get collaborative filtering recommendations
        collab_recs = self.collaborative_recommender.get_user_recommendations(
            user_id, n_recommendations * 3  # Get more to have options for hybridization
        )

        if not collab_recs:
            # New user or no collaborative data - use content-based fallback
            return self._get_content_based_recommendations(n_recommendations)

        # Get content-based recommendations for user's top-rated movies
        content_scores = {}

        # Find user's highly rated movies to use as seeds for content-based
        user_idx = self.collaborative_recommender.user_id_map.get(user_id)
        if user_idx is not None:
            user_ratings = self.collaborative_recommender.user_item_matrix[user_idx]
            top_rated_indices = user_ratings.nonzero()[1]

            # Get content recommendations based on top rated movies
            for movie_idx in top_rated_indices[:5]:  # Use top 5 rated movies as seeds
                movie_id = self.collaborative_recommender.reverse_movie_map[movie_idx]
                content_recs = self.content_recommender.get_recommendations(
                    movie_id, 20
                )

                for rec_movie_id, score in content_recs:
                    if rec_movie_id in content_scores:
                        content_scores[rec_movie_id] = max(
                            content_scores[rec_movie_id], score
                        )
                    else:
                        content_scores[rec_movie_id] = score

        # Combine scores
        hybrid_scores = {}

        # Add collaborative scores
        for movie_id, score in collab_recs:
            hybrid_scores[movie_id] = self.collaborative_weight * score

        # Add content scores
        for movie_id, score in content_scores.items():
            if movie_id in hybrid_scores:
                hybrid_scores[movie_id] += self.content_weight * score
            else:
                hybrid_scores[movie_id] = self.content_weight * score

        # Sort and return top recommendations
        sorted_recs = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for movie_id, score in sorted_recs[:n_recommendations]:
            movie_info = self._get_movie_info(movie_id)
            recommendations.append(
                {
                    "movie_id": movie_id,
                    "score": float(score),
                    "title": movie_info.get("title", "Unknown"),
                    "genres": movie_info.get("genres", ""),
                    "year": movie_info.get("year", None),
                }
            )

        return recommendations

    def _get_content_based_recommendations(self, n_recommendations: int) -> List[Dict]:
        """Get content-based recommendations using popular movies as seeds."""
        if (
            not hasattr(self.content_recommender, "movies_df")
            or self.content_recommender.movies_df.empty
        ):
            return []

        recommendations = []

        # Get a few popular movies as seeds for content-based recommendations
        movies_df = self.content_recommender.movies_df.copy()

        # Sort by year (recent first) and take a sample for diversity
        if "year" in movies_df.columns:
            movies_df = movies_df.sort_values("year", ascending=False)

        # Take top movies as seeds and get content-based recommendations
        seed_movies = movies_df.head(5)  # Use top 5 movies as seeds

        content_scores = {}
        for _, movie in seed_movies.iterrows():
            movie_id = movie["movie_id"]
            content_recs = self.content_recommender.get_recommendations(
                movie_id, n_recommendations
            )

            for rec_movie_id, score in content_recs:
                if (
                    rec_movie_id not in content_scores
                    or score > content_scores[rec_movie_id]
                ):
                    content_scores[rec_movie_id] = score

        # If we don't have enough content recommendations, fill with popular movies
        if len(content_scores) < n_recommendations:
            remaining = n_recommendations - len(content_scores)
            popular_movies = movies_df.head(remaining + len(content_scores))

            for _, movie in popular_movies.iterrows():
                movie_id = movie["movie_id"]
                if movie_id not in content_scores:
                    content_scores[movie_id] = 0.5  # Default score

        # Sort and format recommendations
        sorted_recs = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)[
            :n_recommendations
        ]

        for movie_id, score in sorted_recs:
            movie_info = self._get_movie_info(movie_id)
            recommendations.append(
                {
                    "movie_id": movie_id,
                    "score": float(score),
                    "title": movie_info.get("title", "Unknown"),
                    "genres": movie_info.get("genres", ""),
                    "year": movie_info.get("year", None),
                }
            )

        return recommendations

    def _get_movie_info(self, movie_id: int) -> Dict:
        """Get movie information."""
        try:
            movie_row = self.content_recommender.movies_df[
                self.content_recommender.movies_df["movie_id"] == movie_id
            ].iloc[0]
            return {
                "title": movie_row.get("title", "Unknown"),
                "genres": movie_row.get("genres", ""),
                "year": movie_row.get("year", None),
            }
        except (IndexError, KeyError):
            return {"title": "Unknown", "genres": "", "year": None}

    def _get_fallback_recommendations(self, n_recommendations: int) -> List[Dict]:
        """Fallback recommendations for new users - now using content-based approach."""
        return self._get_content_based_recommendations(n_recommendations)

    def update_with_new_rating(self, user_id: int, movie_id: int, rating: float):
        """Update the model with a new rating (simplified version)."""
        # In a production system, you'd want to implement incremental learning
        # For now, this is a placeholder that logs the new rating
        logger.info(
            f"New rating received: User {user_id}, Movie {movie_id}, Rating {rating}"
        )
        # You would need to retrain periodically or implement online learning

    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        model_data = {
            "content_recommender": self.content_recommender,
            "collaborative_recommender": self.collaborative_recommender,
            "content_weight": self.content_weight,
            "collaborative_weight": self.collaborative_weight,
            "is_trained": self.is_trained,
        }

        with open(filepath, "wb") as f:
            pickle.dump(model_data, f)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        with open(filepath, "rb") as f:
            model_data = pickle.load(f)

        self.content_recommender = model_data["content_recommender"]
        self.collaborative_recommender = model_data["collaborative_recommender"]
        self.content_weight = model_data["content_weight"]
        self.collaborative_weight = model_data["collaborative_weight"]
        self.is_trained = model_data["is_trained"]

        logger.info(f"Model loaded from {filepath}")
