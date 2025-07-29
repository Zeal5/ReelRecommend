from rest_framework import serializers
from .models import Movie, Rating


class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "overview",
            "genres",
            "director",
            "actors",
            "year",
            "poster_url",
            "backdrop_url",
            "popularity",
            "vote_average",
            "vote_count",
            "runtime",
            "average_rating",
            "imdb_id",
        ]


class RatingSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Rating
        fields = ["id", "movie", "movie_title", "rating", "timestamp"]
        read_only_fields = ["timestamp"]


class RecommendationSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    score = serializers.FloatField()
    title = serializers.CharField()
    genres = serializers.CharField()
    year = serializers.IntegerField(allow_null=True)
    poster_url = serializers.URLField(allow_blank=True)
