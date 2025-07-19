from django.urls import path
from . import views

urlpatterns = [
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
    path('ratings/', views.add_rating, name='add_rating'),
    path('interactions/', views.add_interaction, name='add_interaction'),
]
