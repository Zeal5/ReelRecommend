import { ChevronLeft, ChevronRight } from "lucide-react";
import { Movie } from "@/data/movies";
import { MovieCard } from "./MovieCard";
import { Button } from "@/components/ui/button";
import { useRef, useState } from "react";

interface MovieCarouselProps {
  title: string;
  movies: Movie[];
  size?: "sm" | "md" | "lg";
}

export const MovieCarousel = ({
  title,
  movies,
  size = "md",
}: MovieCarouselProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkScrollButtons = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth);
    }
  };

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = 320; // Adjust based on card width
      const newScrollLeft =
        direction === "left"
          ? scrollRef.current.scrollLeft - scrollAmount
          : scrollRef.current.scrollLeft + scrollAmount;

      scrollRef.current.scrollTo({
        left: newScrollLeft,
        behavior: "smooth",
      });

      // Check buttons after animation
      setTimeout(checkScrollButtons, 300);
    }
  };

  return (
    <div className="relative">
      <h2 className="text-2xl font-bold text-foreground mb-6 px-4">{title}</h2>

      <div className="relative">
        {/* Left scroll button */}
        {canScrollLeft && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute left-2 top-1/2 -translate-y-1/2 z-10 bg-black/70 hover:bg-black/90 text-white border-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            onClick={() => scroll("left")}
          >
            <ChevronLeft className="h-6 w-6" />
          </Button>
        )}

        {/* Right scroll button */}
        {canScrollRight && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-2 top-1/2 -translate-y-1/2 z-10 bg-black/70 hover:bg-black/90 text-white border-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            onClick={() => scroll("right")}
          >
            <ChevronRight className="h-6 w-6" />
          </Button>
        )}

        {/* Carousel container */}
        <div
          ref={scrollRef}
          className="flex gap-4 overflow-x-auto scrollbar-hide px-4 py-2"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          onScroll={checkScrollButtons}
        >
          {movies.map((movie, index) => (
            <div
              key={movie.id}
              className="flex-shrink-0 animate-slide-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <MovieCard movie={movie} size={size} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
