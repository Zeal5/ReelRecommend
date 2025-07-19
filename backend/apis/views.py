from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import logging

from .recommendation_engine.services import recommendation_service
from .recommendation_engine.data_fetcher import RealtimeUpdateProcessor
from .models import Movie, Rating, UserInteraction
from .serializers import MovieSerializer, RatingSerializer, RecommendationSerializer

logger = logging.getLogger(__name__)
realtime_processor = RealtimeUpdateProcessor(recommendation_service)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """Get personalized movie recommendations for the authenticated user."""
    try:
        user_id = request.user.id
        count = int(request.GET.get('count', 10))
        
        # Get recommendations from the service
        recommendations = recommendation_service.get_recommendations(user_id, count)
        
        # Add additional movie details
        enriched_recommendations = []
        for rec in recommendations:
            try:
                movie = Movie.objects.get(id=rec['movie_id'])
                rec.update({
                    'poster_url': movie.poster_url,
                    'overview': movie.overview[:200] + '...' if len(movie.overview) > 200 else movie.overview,
                    'vote_average': movie.vote_average,
                })
                enriched_recommendations.append(rec)
            except Movie.DoesNotExist:
                continue
        
        serializer = RecommendationSerializer(enriched_recommendations, many=True)
        
        return Response({
            'success': True,
            'recommendations': serializer.data,
            'count': len(serializer.data)
        })

    except Exception as e:
        logger.error(f"Error getting recommendations for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to get recommendations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_rating(request):
    """Add or update a movie rating."""
    try:
        movie_id = request.data.get('movie_id')
        rating_value = float(request.data.get('rating'))
        
        # Validate rating value
        if not (0.5 <= rating_value <= 5.0):
            return Response({
                'success': False,
                'error': 'Rating must be between 0.5 and 5.0'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get movie
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Create or update rating
        rating_obj, created = Rating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': rating_value}
        )
        
        # Process with recommendation system
        success = realtime_processor.process_rating(
            request.user.id, movie_id, rating_value
        )
        
        if not success:
            logger.warning(f"Failed to update recommendation system for rating: {request.user.id}, {movie_id}")
        
        action = 'created' if created else 'updated'
        
        return Response({
            'success': True,
            'message': f'Rating {action} successfully',
            'rating': {
                'movie_id': movie_id,
                'movie_title': movie.title,
                'rating': rating_value,
                'action': action
            }
        })
        
    except ValueError:
        return Response({
            'success': False,
            'error': 'Invalid rating value'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error adding rating: {e}")
        return Response({
            'success': False,
            'error': 'Failed to add rating'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_interaction(request):
    """Record a user interaction with a movie."""
    try:
        movie_id = request.data.get('movie_id')
        interaction_type = request.data.get('type')
        
        # Validate interaction type
        valid_types = ['view', 'like', 'dislike', 'share', 'watchlist_add', 'watchlist_remove']
        if interaction_type not in valid_types:
            return Response({
                'success': False,
                'error': f'Invalid interaction type. Must be one of: {valid_types}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get movie
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Process interaction
        if interaction_type == 'view':
            success = realtime_processor.process_view(request.user.id, movie_id)
        elif interaction_type == 'like':
            success = realtime_processor.process_like(request.user.id, movie_id)
        elif interaction_type == 'dislike':
            success = realtime_processor.process_dislike(request.user.id, movie_id)
        else:
            success = realtime_processor._process_interaction(
                request.user.id, movie_id, interaction_type, 3.0  # Default implicit rating
            )
        
        if success:
            return Response({
                'success': True,
                'message': f'{interaction_type.title()} recorded successfully',
                'interaction': {
                    'movie_id': movie_id,
                    'movie_title': movie.title,
                    'type': interaction_type
                }
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to record interaction'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        return Response({
            'success': False,
            'error': 'Failed to get recommendations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
