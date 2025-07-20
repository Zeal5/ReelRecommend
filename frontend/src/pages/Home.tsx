import React, { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { HeroCarousel } from "@/components/HeroCarousel";
import { EnhancedMovieCarousel } from "@/components/MovieCarousel";
import { APIService, Recommendation } from "@/data/constants";
import {
  getTrendingMovies,
  getNewReleases,
  getTopRated,
  Movie,
} from "@/data/movies";

// Error state interface for better error tracking
interface ErrorState {
  trending: string | null;
  newReleases: string | null;
  topRated: string | null;
  recommendations: string | null;
}

const Home: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([]);
  const [newReleases, setNewReleases] = useState<Movie[]>([]);
  const [topRated, setTopRated] = useState<Movie[]>([]);

  // Individual loading states for better UX
  const [loadingStates, setLoadingStates] = useState({
    trending: true,
    newReleases: true,
    topRated: true,
    recommendations: true,
  });

  // Error states for each section
  const [errors, setErrors] = useState<ErrorState>({
    trending: null,
    newReleases: null,
    topRated: null,
    recommendations: null,
  });

  const [userRatings, setUserRatings] = useState<{ [key: number]: number }>({});

  // Helper function to update loading state for specific section
  const updateLoadingState = (
    section: keyof typeof loadingStates,
    isLoading: boolean,
  ) => {
    setLoadingStates((prev) => ({ ...prev, [section]: isLoading }));
  };

  // Helper function to update error state for specific section
  const updateError = (section: keyof ErrorState, error: string | null) => {
    setErrors((prev) => ({ ...prev, [section]: error }));
  };

  // Enhanced function to fetch movies with individual error handling

  const fetchMoviesData = async () => {
    // Fetch trending movies
    updateLoadingState("trending", true);
    try {
      const trending = await getTrendingMovies();
      setTrendingMovies(trending);
      updateError("trending", null);
      console.log("✅ Trending movies loaded successfully:", trending.length);
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Failed to load trending movies";
      console.error("❌ Error loading trending movies:", error);
      updateError("trending", errorMessage);
      setTrendingMovies([]); // Ensure empty array on error
    } finally {
      updateLoadingState("trending", false);
    }

    // Fetch new releases
    updateLoadingState("newReleases", true);
    try {
      const newReleasesData = await getNewReleases();
      setNewReleases(newReleasesData);
      updateError("newReleases", null);
      console.log(
        "✅ New releases loaded successfully:",
        newReleasesData.length,
      );
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to load new releases";
      console.error("❌ Error loading new releases:", error);
      updateError("newReleases", errorMessage);
      setNewReleases([]); // Ensure empty array on error
    } finally {
      updateLoadingState("newReleases", false);
    }

    // Fetch top rated
    updateLoadingState("topRated", true);
    try {
      const topRatedData = await getTopRated();
      setTopRated(topRatedData);
      updateError("topRated", null);
      console.log(
        "✅ Top rated movies loaded successfully:",
        topRatedData.length,
      );
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Failed to load top rated movies";
      console.error("❌ Error loading top rated movies:", error);
      updateError("topRated", errorMessage);
      setTopRated([]); // Ensure empty array on error
    } finally {
      updateLoadingState("topRated", false);
    }
  };

  useEffect(() => {
    fetchMoviesData();
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    updateLoadingState("recommendations", true);
    try {
      const recs = await APIService.getRecommendations(8);

      // Enhanced validation for recommendations
      if (!recs || !Array.isArray(recs)) {
        throw new Error("Invalid recommendations data received");
      }

      // More robust movie object construction with validation
      const recommendedMovies = recs
        .filter((rec: Recommendation) => rec && rec.movie_id && rec.title) // Filter out invalid entries
        .map(
          (rec: Recommendation): Movie => ({
            id: rec.movie_id,
            title: rec.title || "Untitled",
            overview: rec.overview || "No description available.",
            poster_url: rec.poster_url || "/api/placeholder/300/450",
            backdrop_url: rec.poster_url
              ? rec.poster_url.replace("w500", "w1280")
              : "/api/placeholder/1200/675",
            vote_average: rec.vote_average || 0,
            year: new Date().getFullYear(),
            runtime: 120,
            genres: "Drama",
            actors: "N/A",
            director: "N/A",
          }),
        );

      setRecommendations(recommendedMovies);
      // setRecommendations([]);
      updateError("recommendations", null);
      console.log(
        "✅ Recommendations loaded successfully:",
        recommendedMovies.length,
      );
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Failed to load recommendations";
      console.error("❌ Error loading recommendations:", error);
      updateError("recommendations", errorMessage);
      setRecommendations([]); // Ensure empty array on error
    } finally {
      updateLoadingState("recommendations", false);
    }
  };

  const handleRating = async (movieId: number, rating: number) => {
    try {
      const success = await APIService.addRating(movieId, rating);
      if (success) {
        setUserRatings((prev) => ({
          ...prev,
          [movieId]: rating,
        }));
        // Reload recommendations with delay
        setTimeout(() => {
          loadRecommendations();
        }, 1000);
      } else {
        console.warn("Rating submission returned false, but no error thrown");
      }
    } catch (error) {
      console.error("Error submitting rating:", error);
      // Could add toast notification here for user feedback
    }
  };

  const handleInteraction = async (movieId: number, type: string) => {
    try {
      await APIService.addInteraction(movieId, type);

      // If it's a significant interaction, reload recommendations
      if (["like", "dislike", "watchlist_add"].includes(type)) {
        setTimeout(() => {
          loadRecommendations();
        }, 1000);
      }
    } catch (error) {
      console.error("Error submitting interaction:", error);
      // Could add toast notification here for user feedback
    }
  };

  // Check if any critical data is available for hero carousel
  const heroMovies =
    trendingMovies.length > 0
      ? trendingMovies
      : topRated.length > 0
        ? topRated
        : newReleases.length > 0
          ? newReleases
          : [];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      {/* Hero Carousel with fallback handling */}
      {heroMovies.length > 0 ? (
        <HeroCarousel movies={heroMovies} />
      ) : (
        <div className="relative h-96 bg-gradient-to-r from-primary/20 to-secondary/20 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-foreground mb-4">
              Welcome to MovieApp
            </h1>
            <p className="text-muted-foreground">
              Discover amazing movies tailored just for you
            </p>
          </div>
        </div>
      )}

      <div className="py-16 space-y-16">
        {/* Personalized Recommendations Section - NOW USING CAROUSEL */}
        <EnhancedMovieCarousel
          title="Recommended for You"
          movies={recommendations}
          size="md"
          onRate={handleRating}
          onInteraction={handleInteraction}
          loading={loadingStates.recommendations}
          showEmptyState={true}
          emptyStateMessage={
            errors.recommendations
              ? `Unable to load recommendations: ${errors.recommendations}`
              : "No personalized recommendations available yet. Rate some movies to get better suggestions!"
          }
        />

        {/* New Releases Carousel with enhanced error handling */}
        <EnhancedMovieCarousel
          title="New Releases"
          movies={newReleases}
          size="lg"
          onRate={handleRating}
          onInteraction={handleInteraction}
          loading={loadingStates.newReleases}
          showEmptyState={true}
          emptyStateMessage={
            errors.newReleases
              ? `Error loading new releases: ${errors.newReleases}`
              : undefined
          }
        />

        {/* Top Rated Carousel with enhanced error handling */}
        <EnhancedMovieCarousel
          title="Top Rated Movies"
          movies={topRated}
          size="md"
          onRate={handleRating}
          onInteraction={handleInteraction}
          loading={loadingStates.topRated}
          showEmptyState={true}
          emptyStateMessage={
            errors.topRated
              ? `Error loading top rated movies: ${errors.topRated}`
              : undefined
          }
        />

        {/* Show retry section if there are any errors */}
        {(errors.trending || errors.newReleases || errors.topRated) && (
          <div className="px-4">
            <div className="bg-muted/30 border border-border rounded-lg p-6 text-center">
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Some Content Failed to Load
              </h3>
              <p className="text-muted-foreground text-sm mb-4">
                Don't worry! You can still browse available movies and try
                reloading the failed sections.
              </p>
              <button
                onClick={fetchMoviesData}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                Reload All Movies
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-secondary/30 border-t border-border py-12 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p className="text-muted-foreground">
            © 2025 MovieApp. Discover your next favorite movie.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
