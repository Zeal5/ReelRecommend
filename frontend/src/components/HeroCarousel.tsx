import { useState, useEffect } from "react";
import { Play, Info, ChevronLeft, ChevronRight } from "lucide-react";
import { Movie } from "@/data/movies";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

interface HeroCarouselProps {
  movies: Movie[];
}

export const HeroCarousel = ({ movies }: HeroCarouselProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % movies.length);
    }, 5000);

    return () => clearInterval(timer);
  }, [movies.length]);

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % movies.length);
  };

  const prevSlide = () => {
    setCurrentIndex(
      (prevIndex) => (prevIndex - 1 + movies.length) % movies.length,
    );
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  const currentMovie = movies[currentIndex];

  if (!currentMovie) return null;

  return (
    <div className="relative h-screen overflow-hidden bg-background">
      {/* Background Image */}
      <div className="absolute inset-0">
        <img
          src={currentMovie.backdrop_url.replace("w500", "w1280")}
          alt={currentMovie.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
      </div>

      {/* Content */}
      <div className="relative z-10 h-full flex items-center">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl animate-fade-in">
            {/* Badges */}

            {/* Title */}
            <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-2xl">
              {currentMovie.title}
            </h1>

            {/* Synopsis */}
            <p className="text-xl text-gray-200 mb-6 max-w-xl leading-relaxed">
              {currentMovie.overview}
            </p>

            {/* Movie Info */}
            <div className="flex items-center gap-4 text-gray-300 mb-8">
              <span className="font-medium">{currentMovie.year}</span>
              <span>•</span>
              <span>{currentMovie.runtime}</span>
              <span>•</span>
              <div className="flex gap-2">
                {currentMovie.genres
                  .split("|")
                  .slice(0, 3)
                  .map((genre) => (
                    <span key={genre} className="text-sm">
                      {genre}
                    </span>
                  ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <Button
                size="lg"
                className="bg-white text-black hover:bg-gray-200 font-semibold px-8 py-3 text-lg"
                onClick={() => navigate(`/movie/${currentMovie.id}`)}
              >
                <Play className="w-6 h-6 mr-2" />
                Play Now
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-gray-400 text-white hover:bg-white/10 font-semibold px-8 py-3 text-lg"
                onClick={() => navigate(`/movie/${currentMovie.id}`)}
              >
                <Info className="w-6 h-6 mr-2" />
                More Info
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Arrows */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-black/30 hover:bg-black/60 text-white border-none"
        onClick={prevSlide}
      >
        <ChevronLeft className="h-8 w-8" />
      </Button>

      <Button
        variant="ghost"
        size="icon"
        className="absolute right-4 top-1/2 -translate-y-1/2 z-10 bg-black/30 hover:bg-black/60 text-white border-none"
        onClick={nextSlide}
      >
        <ChevronRight className="h-8 w-8" />
      </Button>

      {/* Indicators */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2 z-10">
        {movies.map((_, index) => (
          <button
            key={index}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentIndex
                ? "bg-white scale-125"
                : "bg-white/50 hover:bg-white/75"
            }`}
            onClick={() => goToSlide(index)}
          />
        ))}
      </div>
    </div>
  );
};
