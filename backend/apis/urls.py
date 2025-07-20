from django.urls import path
from . import views

urlpatterns = [
    path("recommendations/", views.get_recommendations, name="get_recommendations"),
    path("ratings/", views.add_rating, name="add_rating"),
    path("interactions/", views.add_interaction, name="add_interaction"),


    path("movies/trending/", views.get_trending_movies, name="get_trending_movies"),
    path("movies/new-releases/", views.get_new_releases, name="get_new_releases"),
    path("movies/top-rated/", views.get_top_rated_movies, name="get_top_rated_movies"),
    path("movies/<int:movie_id>/", views.get_movie_by_id, name="get_movie_by_id"),
]
