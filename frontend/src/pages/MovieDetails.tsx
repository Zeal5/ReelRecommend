import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Star, Calendar, Clock, Users } from "lucide-react";
import { getMovieById, Movie } from "@/data/movies";
import { Navigation } from "@/components/Navigation";
import { VideoPlayer } from "@/components/VideoPlayer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const MovieDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchMovie = async () => {
      if (id) {
        setLoading(true);
        const movieData = await getMovieById(Number(id));
        setMovie(movieData || null);
        setLoading(false);
      }
    };
    fetchMovie();
  }, [id]);
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-4">
            Movie not found
          </h1>
          <Button onClick={() => navigate("/")}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <div className="pt-16">
        {/* Hero Section */}
        <div
          className="relative h-96 bg-cover bg-center"
          // CHANGE: Updated property from `movie.backdrop` to `movie.backdrop_url`
          style={{ backgroundImage: `url(${movie.backdrop_url})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-background/20" />
          <div className="absolute top-6 left-6 z-10">
            {/* ... back button ... */}
          </div>
        </div>

        <div className="container mx-auto px-4 -mt-32 relative z-10">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Movie Poster */}
            <div className="lg:col-span-1">
              <Card className="overflow-hidden shadow-card">
                <img
                  // CHANGE: Updated property from `movie.poster` to `movie.poster_url`
                  src={movie.poster_url}
                  alt={movie.title}
                  className="w-full h-96 lg:h-[600px] object-cover"
                />
              </Card>
            </div>

            {/* Movie Details */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                {/* REMOVED: Badges for isTrending and isNew as they are no longer in the data model */}
                <h1 className="text-4xl lg:text-5xl font-bold text-foreground mb-2">
                  {movie.title}
                </h1>
              </div>

              {/* Movie Info */}
              <div className="flex flex-wrap items-center gap-6 text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  {/* CHANGE: Updated property from `movie.rating` to `movie.vote_average` */}
                  <span className="font-medium">
                    {movie.vote_average.toFixed(1)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  <span>{movie.year}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  {/* CHANGE: Updated property from `movie.duration` to `movie.runtime` and added formatting */}
                  <span>{movie.runtime ? `${movie.runtime} min` : "N/A"}</span>
                </div>
              </div>

              {/* Genres */}
              <div className="flex flex-wrap gap-2">
                {/* CHANGE: Split the genres string into an array for mapping */}
                {movie.genres &&
                  movie.genres.split("|").map((genre) => (
                    <Badge
                      key={genre}
                      variant="outline"
                      className="border-border"
                    >
                      {genre}
                    </Badge>
                  ))}
              </div>

              {/* Synopsis */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-3">
                  Synopsis
                </h2>
                {/* CHANGE: Updated property from `movie.synopsis` to `movie.overview` */}
                <p className="text-muted-foreground leading-relaxed text-lg">
                  {movie.overview}
                </p>
              </div>

              {/* Cast & Crew */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-3">
                  Cast & Crew
                </h2>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-foreground">
                      Director:{" "}
                    </span>
                    <span className="text-muted-foreground">
                      {movie.director || "N/A"}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-foreground">Cast: </span>
                    {/* CHANGE: Split the actors string and join with commas */}
                    <span className="text-muted-foreground">
                      {movie.actors
                        ? movie.actors.split("|").join(", ")
                        : "N/A"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Video Player */}
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-foreground mb-6">
              Watch {movie.title}
            </h2>
            {/* CHANGE: Updated poster property */}
            <VideoPlayer poster={movie.backdrop_url} imdbId={movie.imdb_id} />
          </div>

        </div>
      </div>
    </div>
  );
};

export default MovieDetails;
