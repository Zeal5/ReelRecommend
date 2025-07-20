# management/commands/manage_recommendations.py
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from apis.recommendation_engine.services import recommendation_service
from apis.models import Movie, Rating
import json
import os
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Manage recommendation models - train, save, and test recommendations'

    def add_arguments(self, parser):
        # Subcommands
        subparsers = parser.add_subparsers(dest='action', help='Available actions')
        
        # Train model command
        train_parser = subparsers.add_parser('train', help='Train and save new recommendation model')
        train_parser.add_argument(
            '--force',
            action='store_true',
            help='Force retrain even if model was recently trained',
        )
        
        # Test recommendations command
        test_parser = subparsers.add_parser('test', help='Test recommendations for specific users')
        test_parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to get recommendations for',
        )
        test_parser.add_argument(
            '--user-email',
            type=str,
            help='User email to get recommendations for',
        )
        test_parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of recommendations to generate (default: 10)',
        )
        test_parser.add_argument(
            '--all-users',
            action='store_true',
            help='Generate recommendations for all users (be careful with large datasets)',
        )
        
        # Model info command
        info_parser = subparsers.add_parser('info', help='Show model information and statistics')
        
        # Clear cache command
        cache_parser = subparsers.add_parser('clear-cache', help='Clear recommendation cache')
        cache_parser.add_argument(
            '--user-id',
            type=int,
            help='Clear cache for specific user (optional)',
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if not action:
            self.stdout.write(
                self.style.ERROR('Please specify an action. Use --help for available options.')
            )
            return
            
        if action == 'train':
            self.handle_train(options)
        elif action == 'test':
            self.handle_test(options)
        elif action == 'info':
            self.handle_info(options)
        elif action == 'clear-cache':
            self.handle_clear_cache(options)

    def handle_train(self, options):
        """Handle model training."""
        self.stdout.write("Starting recommendation model training...")
        
        # Check if we should force retrain
        force_retrain = options.get('force', False)
        
        if not force_retrain and not recommendation_service.should_retrain():
            self.stdout.write(
                self.style.WARNING(
                    "Model was recently trained. Use --force to retrain anyway."
                )
            )
            return
        
        # Show current statistics
        self.show_data_statistics()
        
        start_time = timezone.now()
        self.stdout.write("Training model...")
        
        # Initialize service if not already done
        if not hasattr(recommendation_service, 'recommender') or recommendation_service.recommender is None:
            recommendation_service.initialize()
        
        # Train the model
        success = recommendation_service.train_model()
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Model trained successfully in {duration:.2f} seconds!'
                )
            )
            
            # Show model info
            self.show_model_info()
            
            # Clear all cached recommendations
            self.stdout.write("Clearing recommendation cache...")
            cache.clear()  # Clear all cache or use more specific pattern
            self.stdout.write(self.style.SUCCESS("Cache cleared successfully!"))
            
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Model training failed after {duration:.2f} seconds'
                )
            )

    def handle_test(self, options):
        """Handle recommendation testing."""
        user_id = options.get('user_id')
        user_email = options.get('user_email')
        count = options.get('count', 10)
        all_users = options.get('all_users', False)
        
        # Initialize service if needed
        if not hasattr(recommendation_service, 'recommender') or recommendation_service.recommender is None:
            self.stdout.write("Initializing recommendation service...")
            recommendation_service.initialize()
        
        if all_users:
            self.test_all_users(count)
        elif user_id or user_email:
            user = self.get_user(user_id, user_email)
            if user:
                self.test_user_recommendations(user, count)
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Please specify --user-id, --user-email, or --all-users"
                )
            )

    def handle_info(self, options):
        """Handle showing model information."""
        self.stdout.write(self.style.HTTP_INFO("=== Recommendation System Info ==="))
        
        # Data statistics
        self.show_data_statistics()
        
        # Model information
        self.show_model_info()
        
        # Cache information
        self.show_cache_info()

    def handle_clear_cache(self, options):
        """Handle cache clearing."""
        user_id = options.get('user_id')
        
        if user_id:
            # Clear cache for specific user
            cache_pattern = f"recommendations_{user_id}_*"
            # Django's cache.delete_pattern might not be available in all backends
            # You might need to implement this differently based on your cache backend
            try:
                cache.delete_pattern(cache_pattern)
                self.stdout.write(
                    self.style.SUCCESS(f"Cache cleared for user {user_id}")
                )
            except AttributeError:
                # Fallback: clear specific keys
                for count in [5, 10, 15, 20, 25, 30]:
                    cache.delete(f"recommendations_{user_id}_{count}")
                self.stdout.write(
                    self.style.SUCCESS(f"Cache cleared for user {user_id} (common counts)")
                )
        else:
            # Clear all cache
            cache.clear()
            self.stdout.write(self.style.SUCCESS("All cache cleared"))

    def show_data_statistics(self):
        """Show database statistics."""
        self.stdout.write(self.style.HTTP_INFO("\n=== Data Statistics ==="))
        
        movie_count = Movie.objects.count()
        user_count = User.objects.count()
        rating_count = Rating.objects.count()
        
        self.stdout.write(f"Movies: {movie_count:,}")
        self.stdout.write(f"Users: {user_count:,}")
        self.stdout.write(f"Ratings: {rating_count:,}")
        
        if rating_count > 0 and user_count > 0:
            avg_ratings_per_user = rating_count / user_count
            self.stdout.write(f"Average ratings per user: {avg_ratings_per_user:.2f}")

    def show_model_info(self):
        """Show model information."""
        self.stdout.write(self.style.HTTP_INFO("\n=== Model Information ==="))
        
        if not recommendation_service.recommender:
            self.stdout.write(self.style.WARNING("No model loaded"))
            return
        
        # Check if model file exists
        if os.path.exists(recommendation_service.model_path):
            model_mtime = os.path.getmtime(recommendation_service.model_path)
            model_date = datetime.fromtimestamp(model_mtime)
            self.stdout.write(f"Model file: {recommendation_service.model_path}")
            self.stdout.write(f"Last trained: {model_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Model status
        is_trained = getattr(recommendation_service.recommender, 'is_trained', False)
        has_collaborative = getattr(recommendation_service.recommender, 'has_collaborative_data', False)
        
        self.stdout.write(f"Model trained: {is_trained}")
        self.stdout.write(f"Has collaborative data: {has_collaborative}")
        
        # Collaborative filtering info
        if hasattr(recommendation_service.recommender, 'collaborative_recommender'):
            cf_recommender = recommendation_service.recommender.collaborative_recommender
            if hasattr(cf_recommender, 'user_id_map'):
                self.stdout.write(f"Users in CF model: {len(cf_recommender.user_id_map)}")
                self.stdout.write(f"Movies in CF model: {len(cf_recommender.movie_id_map)}")

    def show_cache_info(self):
        """Show cache information."""
        self.stdout.write(self.style.HTTP_INFO("\n=== Cache Information ==="))
        
        # This is cache-backend dependent and might not work for all backends
        try:
            # For Redis backend
            if hasattr(cache, '_cache'):
                cache_info = cache._cache.get_stats()
                self.stdout.write(f"Cache backend: {type(cache._cache).__name__}")
        except:
            pass
        
        self.stdout.write("Cache keys are automatically managed by the system")

    def get_user(self, user_id=None, user_email=None):
        """Get user by ID or email."""
        try:
            if user_id:
                return User.objects.get(id=user_id)
            elif user_email:
                return User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User not found: {user_id or user_email}")
            )
            return None

    def test_user_recommendations(self, user, count):
        """Test recommendations for a specific user."""
        self.stdout.write(
            self.style.HTTP_INFO(f"\n=== Recommendations for {user.username} (ID: {user.id}) ===")
        )
        
        # Check user's rating history
        user_ratings = Rating.objects.filter(user=user).order_by('-timestamp')[:5]
        if user_ratings.exists():
            self.stdout.write("Recent ratings:")
            for rating in user_ratings:
                self.stdout.write(f"  - {rating.movie.title}: {rating.rating}/5.0")
        else:
            self.stdout.write("No ratings found for this user")
        
        # Get recommendations
        start_time = timezone.now()
        recommendations = recommendation_service.get_recommendations(user.id, count)
        end_time = timezone.now()
        
        duration = (end_time - start_time).total_seconds() * 1000  # in milliseconds
        
        self.stdout.write(f"\nRecommendations generated in {duration:.2f}ms:")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                movie_title = rec.get('title', 'Unknown')
                score = rec.get('score', 0)
                genres = rec.get('genres', 'N/A')
                year = rec.get('year', 'N/A')
                
                self.stdout.write(
                    f"  {i:2d}. {movie_title} ({year}) - Score: {score:.3f}"
                )
                self.stdout.write(f"      Genres: {genres}")
        else:
            self.stdout.write(self.style.WARNING("No recommendations generated"))

    def test_all_users(self, count):
        """Test recommendations for all users."""
        self.stdout.write(self.style.WARNING("Testing recommendations for all users..."))
        
        users_with_ratings = User.objects.filter(rating__isnull=False).distinct()
        total_users = users_with_ratings.count()
        
        if total_users == 0:
            self.stdout.write(self.style.WARNING("No users with ratings found"))
            return
        
        self.stdout.write(f"Testing {total_users} users with ratings...")
        
        successful = 0
        failed = 0
        
        for i, user in enumerate(users_with_ratings, 1):
            try:
                recommendations = recommendation_service.get_recommendations(user.id, count)
                if recommendations:
                    successful += 1
                    self.stdout.write(
                        f"  {i:3d}/{total_users} - User {user.username}: {len(recommendations)} recommendations"
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        f"  {i:3d}/{total_users} - User {user.username}: No recommendations"
                    )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  {i:3d}/{total_users} - User {user.username}: Error - {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted: {successful} successful, {failed} failed"
            )
        )
