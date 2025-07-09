import { Star, Play } from "lucide-react";
import { Movie } from "@/data/movies";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

interface MovieCardProps {
  movie: Movie;
  size?: "sm" | "md" | "lg";
}

export const MovieCard = ({ movie, size = "md" }: MovieCardProps) => {
  const navigate = useNavigate();

  const sizeClasses = {
    sm: "w-48 h-72",
    md: "w-56 h-80",
    lg: "w-64 h-96"
  };

  const handleClick = () => {
    navigate(`/movie/${movie.id}`);
  };

  return (
    <Card 
      className={`${sizeClasses[size]} group cursor-pointer bg-card border-border overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-glow hover:border-primary/50 animate-scale-in`}
      onClick={handleClick}
    >
      <div className="relative h-full">
        {/* Movie Poster */}
        <div className="relative h-full overflow-hidden">
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          />
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
            <Play className="w-12 h-12 text-white drop-shadow-lg" />
          </div>

          {/* Badges */}
          <div className="absolute top-2 left-2 flex flex-col gap-1">
            {movie.isNew && (
              <Badge className="bg-primary text-primary-foreground text-xs">NEW</Badge>
            )}
            {movie.isTrending && (
              <Badge className="bg-gradient-primary text-white text-xs">TRENDING</Badge>
            )}
          </div>

          {/* Rating */}
          <div className="absolute top-2 right-2 flex items-center gap-1 bg-black/70 rounded-full px-2 py-1">
            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
            <span className="text-white text-xs font-medium">{movie.rating}</span>
          </div>
        </div>

        {/* Movie Info */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent p-4">
          <h3 className="font-bold text-white text-sm mb-1 line-clamp-2 group-hover:text-primary transition-colors">
            {movie.title}
          </h3>
          <div className="flex items-center justify-between text-xs text-gray-300">
            <span>{movie.year}</span>
            <span>{movie.duration}</span>
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {movie.genre.slice(0, 2).map((genre) => (
              <span
                key={genre}
                className="text-xs text-muted-foreground bg-muted/30 rounded px-2 py-1"
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