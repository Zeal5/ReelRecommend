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
from django import db
import logging
from datetime import datetime

from .recommendation_engine.services import recommendation_service
from .recommendation_engine.data_fetcher import RealtimeUpdateProcessor
from .models import Movie, Rating, UserInteraction
from .serializers import MovieSerializer, RatingSerializer, RecommendationSerializer

logger = logging.getLogger(__name__)
realtime_processor = RealtimeUpdateProcessor(recommendation_service)



@api_view(['GET'])
@permission_classes([])
def get_recommendations(request):
    """Get movie recommendations for both authenticated and unauthenticated users."""
    try:
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Authenticated user - get personalized recommendations
            user_id = request.user.id
            count = int(request.GET.get('count', 10))
            
            # Get recommendations from the service
            recommendations = recommendation_service.get_recommendations(user_id, count)
            
        else:
            # Unauthenticated user - get popular/fallback recommendations
            count = int(request.GET.get('count', 10))
            
            # Get fallback recommendations (popular movies)
            recommendations = recommendation_service.get_fallback_recommendations(count)
        
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
        
        res = Response({
            'success': True,
            'recommendations': serializer.data,
            'count': len(serializer.data),
            'is_personalized': request.user.is_authenticated  # Indicate if recommendations are personalized
        })
        return res

    except Exception as e:
        # Log different messages for authenticated vs unauthenticated users
        user_info = f"user {request.user.id}" if request.user.is_authenticated else "anonymous user"
        logger.error(f"Error getting recommendations for {user_info}: {e}")
        
        return Response({
            'success': False,
            'error': 'Failed to get recommendations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_rating(request):
    """Add or update a movie rating."""
    db.close_old_connections()
    try:
        print()
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
        logger.info(f"Recording interaction: {request.user.id}, {movie_id}, {interaction_type}")
        
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





# get movies
@api_view(['GET'])
@permission_classes([]) # No authentication needed to view movie lists
def get_movie_by_id(request, movie_id):
    """
    Get detailed information for a single movie by its ID.
    """
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting movie with id {movie_id}: {e}")
        return Response(
            {'success': False, 'error': 'Movie not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([])
def get_trending_movies(request):
    """
    Get a list of trending movies.
    Trending is determined by recent releases with high popularity.
    """
    try:
        # Define "recent" as the last 3 years
        last_three_years = datetime.now().year - 3
        
        # Filter for recent movies and order by popularity
        trending_movies = Movie.objects.filter(
            year__gte=last_three_years,
            popularity__gt=100  # Filter out very low popularity movies
        ).order_by('-popularity')[:15] # Get top 15

        serializer = MovieSerializer(trending_movies, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting trending movies: {e}")
        return Response(
            {'success': False, 'error': 'Failed to retrieve trending movies'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([])
def get_new_releases(request):
    """
    Get a list of new release movies.
    New releases are defined as movies from the current and previous year.
    """
    try:
        current_year = datetime.now().year
        
        # Filter for movies from this year and last year, order by most recent
        new_releases = Movie.objects.filter(
            year__in=[current_year, current_year - 1]
        ).order_by('-year', '-popularity')[:15] # Get top 15

        serializer = MovieSerializer(new_releases, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error getting new releases: {e}")
        return Response(
            {'success': False, 'error': 'Failed to retrieve new releases'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([])
def get_top_rated_movies(request):
    """
    Get a list of top-rated movies.
    Top-rated is determined by vote average, with a minimum number of votes.
    """
    try:
        # Filter for movies with a significant number of votes to ensure reliability
        top_rated = Movie.objects.filter(
            vote_count__gt=500 # Minimum 500 votes
        ).order_by('-vote_average', '-vote_count')[:15] # Get top 15

        serializer = MovieSerializer(top_rated, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error getting top-rated movies: {e}")
        return Response(
            {'success': False, 'error': 'Failed to retrieve top-rated movies'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

