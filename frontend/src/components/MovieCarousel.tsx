import { Movie } from "@/data/movies";
import { EnhancedMovieCard } from "./MovieCard";
import MovieCardSkeleton from "./MovieCardSkeleton";
import DragScrollWrapper from "./DragScrollWrapper";
import React from "react";

// Enhanced Movie Carousel with API integration, loading state, and empty state handling
export const EnhancedMovieCarousel: React.FC<{
  title: string;
  movies: Movie[];
  size?: "sm" | "md" | "lg";
  onRate?: (movieId: number, rating: number) => void;
  onInteraction?: (movieId: number, type: string) => void;
  loading?: boolean;
  showEmptyState?: boolean; // New prop to control empty state display
  emptyStateMessage?: string; // Custom empty state message
}> = ({
  title,
  movies,
  size = "md",
  onRate,
  onInteraction,
  loading = false,
  showEmptyState = true,
  emptyStateMessage,
}) => {
  // Don't render anything if loading is false, movies is empty, and showEmptyState is false
  if (!loading && (!movies || movies.length === 0) && !showEmptyState) {
    return null;
  }

  const getEmptyStateMessage = () => {
    if (emptyStateMessage) return emptyStateMessage;

    // Generate contextual messages based on title
    const titleLower = title.toLowerCase();
    if (titleLower.includes("trending")) {
      return "No trending movies available right now. Check back later!";
    } else if (titleLower.includes("new") || titleLower.includes("release")) {
      return "No new releases available at the moment.";
    } else if (titleLower.includes("top") || titleLower.includes("rated")) {
      return "No top-rated movies to display right now.";
    } else if (titleLower.includes("recommend")) {
      return "No recommendations available. Rate some movies to get personalized suggestions!";
    }
    return "No movies available in this category right now.";
  };

  return (
    <div className="relative">
      <h2 className="text-2xl font-bold text-foreground mb-6 px-4">{title}</h2>

      {loading ? (
        // Loading state - show skeleton cards
        <div className="flex gap-4 overflow-x-auto scrollbar-hide px-4 py-2">
          {Array.from({ length: 5 }).map((_, index) => (
            <MovieCardSkeleton key={`skeleton-${index}`} size={size} />
          ))}
        </div>
      ) : movies && movies.length > 0 ? (
        // Content state - show actual movie cards
        <DragScrollWrapper>
          {movies.map((movie) => (
            <div key={movie.id} className="flex-shrink-0">
              <EnhancedMovieCard
                movie={movie}
                size={size}
                onRate={onRate}
                onInteraction={onInteraction}
              />
            </div>
          ))}
        </DragScrollWrapper>
      ) : showEmptyState ? (
        // Empty state - show when no movies are available
        <div className="px-4">
          <div className="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-border rounded-lg bg-secondary/20">
            <div className="w-16 h-16 mb-4 rounded-full bg-secondary/50 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-muted-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4H20C20.55 4 21 4.45 21 5S20.55 6 20 6H19V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V6H4C3.45 6 3 5.55 3 5S3.45 4 4 4H7ZM9 8V17H11V8H9ZM13 8V17H15V8H13Z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No Movies Found
            </h3>
            <p className="text-muted-foreground text-sm max-w-md">
              {getEmptyStateMessage()}
            </p>
            {title.toLowerCase().includes("recommend") && (
              <div className="mt-4 text-xs text-muted-foreground">
                <p>
                  💡 Tip: Try rating movies in other sections to improve your
                  recommendations
                </p>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
