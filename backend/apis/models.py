from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class MovieManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(adult=False)

class Movie(models.Model):
    # Basic movie information
    title = models.CharField(max_length=200, db_index=True)
    overview = models.TextField(blank=True)
    genres = models.CharField(max_length=200, blank=True)
    director = models.CharField(max_length=100, blank=True)
    actors = models.CharField(max_length=500, blank=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    plot_keywords = models.CharField(max_length=500, blank=True)
    
    # External IDs
    imdb_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, db_index=True)
    
    # Media
    poster_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    
    # Metadata
    popularity = models.FloatField(default=0.0, db_index=True)
    vote_average = models.FloatField(default=0.0, db_index=True)
    vote_count = models.IntegerField(default=0)
    runtime = models.IntegerField(null=True, blank=True)
    budget = models.BigIntegerField(default=0)
    revenue = models.BigIntegerField(default=0)
    adult = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MovieManager()
    
    class Meta:
        ordering = ['-popularity', '-vote_average']
        indexes = [
            models.Index(fields=['popularity', 'vote_average']),
            models.Index(fields=['year', 'popularity']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.year})"
    
    @property
    def average_rating(self):
        ratings = self.rating_set.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField(
        validators=[MinValueValidator(0.5), MaxValueValidator(5.0)]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['movie', 'rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}"

class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('share', 'Share'),
        ('watchlist_add', 'Added to Watchlist'),
        ('watchlist_remove', 'Removed from Watchlist'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'interaction_type', 'timestamp']),
            models.Index(fields=['movie', 'interaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.interaction_type}d {self.movie.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_genres = models.CharField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Recommendation preferences
    enable_recommendations = models.BooleanField(default=True)
    recommendation_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile" 
