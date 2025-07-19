from django.apps import AppConfig
from django.contrib import admin
from .models import Movie, Rating, UserInteraction, UserProfile

# Register your models here.

admin.site.register(Rating)
admin.site.register(UserProfile)
admin.site.register(UserInteraction)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Columns shown on the main changelist page
    list_display = ('title','genres', 'popularity', 'vote_count')
    
    # Fields to search by in the admin search bar
    search_fields = ('title',)
    
    
    # Optional: add ordering or default ordering (your model Meta already has ordering)
    ordering = ('title','-popularity', '-vote_average')

class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    
    def ready(self):
        from apis.recommendation_engine.services import recommendation_service
        recommendation_service.initialize()
