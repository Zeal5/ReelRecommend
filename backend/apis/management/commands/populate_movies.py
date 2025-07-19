from django.core.management.base import BaseCommand
from apis.recommendation_engine.data_fetcher import DataProcessor
from apis.recommendation_engine.services import recommendation_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Populate database with movies from TMDB and initialize recommendation service"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=1000,
            help="Number of movies to fetch (default: 1000)",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(f"Starting to populate database with {count} movies...")

        try:
            # Initialize data processor
            processor = DataProcessor()

            # Populate database from TMDB
            created, updated = processor.populate_database_from_tmdb(count)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully populated database: {created} created, {updated} updated"
                )
            )

            # Initialize recommendation service
            self.stdout.write("Initializing recommendation service...")
            recommendation_service.initialize()

            self.stdout.write(
                self.style.SUCCESS("Recommendation service initialized successfully")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error populating database: {e}"))
            logger.error(f"Database population failed: {e}")
