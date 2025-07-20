import { Movie } from "@/data/movies";
import React, { useState, useEffect } from "react";
import { Star, Heart, Eye, Share2, Plus, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { APIService } from "@/data/constants";

// Enhanced Movie Card with rating and interaction features
export const EnhancedMovieCard: React.FC<{
  movie: Movie;
  size?: "sm" | "md" | "lg";
  onRate?: (movieId: number, rating: number) => void;
  onInteraction?: (movieId: number, type: string) => void;
  userRating?: number;
  isInWatchlist?: boolean;
}> = ({
  movie,
  size = "md",
  onRate,
  onInteraction,
  userRating,
  isInWatchlist,
}) => {
  const [showRating, setShowRating] = useState(false);
  const [hoverRating, setHoverRating] = useState(0);
  const [currentRating, setCurrentRating] = useState(userRating || 0);
  const [watchlistStatus, setWatchlistStatus] = useState(
    isInWatchlist || false,
  );

  const navigate = useNavigate();
  const sizeClasses = {
    sm: "w-48 h-72",
    md: "w-56 h-80",
    lg: "w-64 h-96",
  };

  const handleRateMovie = async (rating: number) => {
    setCurrentRating(rating);
    if (onRate) {
      onRate(movie.id, rating);
    }
    // Record the rating interaction
    await APIService.addInteraction(movie.id, "view");
  };

  const handleInteraction = async (type: string) => {
    if (type === "watchlist_add" || type === "watchlist_remove") {
      setWatchlistStatus(!watchlistStatus);
    }

    if (onInteraction) {
      onInteraction(movie.id, type);
    }

    await APIService.addInteraction(movie.id, type);
  };

  const handleCardClick = () => {
    // Record view interaction when card is clicked
    handleInteraction("view");
    navigate(`/movie/${movie.id}`);
  };

  return (
    <Card
      className={`${sizeClasses[size]} group cursor-pointer bg-card border-border overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-glow hover:border-primary/50`}
      onClick={handleCardClick}
    >
      <div className="relative h-full">
        {/* Movie Poster */}
        <div className="relative h-4/5 overflow-hidden">
          <img
            src={movie.poster_url}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          />

          {/* Interactive Overlay */}
          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <div className="absolute top-2 right-2 flex flex-col gap-2">
              <Button
                size="sm"
                variant="ghost"
                className="w-8 h-8 p-0 bg-black/50 hover:bg-black/70 text-white"
                onClick={(e) => {
                  e.stopPropagation();
                  handleInteraction(
                    watchlistStatus ? "watchlist_remove" : "watchlist_add",
                  );
                }}
              >
                {watchlistStatus ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="w-8 h-8 p-0 bg-black/50 hover:bg-black/70 text-white"
                onClick={(e) => {
                  e.stopPropagation();
                  handleInteraction("like");
                }}
              >
                <Heart className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="w-8 h-8 p-0 bg-black/50 hover:bg-black/70 text-white"
                onClick={(e) => {
                  e.stopPropagation();
                  handleInteraction("share");
                }}
              >
                <Share2 className="w-4 h-4" />
              </Button>
            </div>

            {/* Rating Stars */}
            <div className="absolute bottom-2 left-2 right-2">
              <div
                className="flex justify-center gap-1 mb-2"
                onMouseEnter={() => setShowRating(true)}
                onMouseLeave={() => {
                  setShowRating(false);
                  setHoverRating(0);
                }}
              >
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    className="transition-transform hover:scale-110"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRateMovie(star);
                    }}
                    onMouseEnter={() => setHoverRating(star)}
                  >
                    <Star
                      className={`w-5 h-5 ${
                        star <= (hoverRating || currentRating)
                          ? "text-yellow-400 fill-yellow-400"
                          : "text-white/50"
                      }`}
                    />
                  </button>
                ))}
              </div>
              {currentRating > 0 && (
                <div className="text-center text-white text-sm">
                  Your Rating: {currentRating}/5
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Movie Info */}
        <div className="h-1/5 p-3 bg-card">
          <h3 className="font-bold text-foreground text-sm mb-1 line-clamp-1">
            {movie.title}
          </h3>
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
            <span>{movie.year}</span>
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
              <span>{movie.popularity}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-1">
            {movie.genres
              .split("|")
              .slice(0, 3)
              .map((genre) => (
                <span
                  key={genre}
                  className="text-xs text-muted-foreground bg-muted/30 rounded px-1"
                >
                  {genre}
                </span>
              ))}
          </div>
        </div>
      </div>
    </Card>
  );
};
