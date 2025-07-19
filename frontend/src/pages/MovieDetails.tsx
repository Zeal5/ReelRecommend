import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Star, Calendar, Clock, Users } from "lucide-react";
import { getMovieById } from "@/data/movies";
import { Navigation } from "@/components/Navigation";
import { VideoPlayer } from "@/components/VideoPlayer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const MovieDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const movie = id ? getMovieById(id) : null;

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
          style={{ backgroundImage: `url(${movie.backdrop})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-background/20" />

          {/* Back Button */}
          <div className="absolute top-6 left-6 z-10">
            <Button
              variant="ghost"
              className="bg-black/50 hover:bg-black/70 text-white"
              onClick={() => navigate("/")}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </div>
        </div>

        <div className="container mx-auto px-4 -mt-32 relative z-10">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Movie Poster */}
            <div className="lg:col-span-1">
              <Card className="overflow-hidden shadow-card">
                <img
                  src={movie.poster}
                  alt={movie.title}
                  className="w-full h-96 lg:h-[600px] object-cover"
                />
              </Card>
            </div>

            {/* Movie Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* Title and Badges */}
              <div>
                <div className="flex flex-wrap gap-2 mb-4">
                  {movie.isTrending && (
                    <Badge className="bg-gradient-primary text-white">
                      TRENDING
                    </Badge>
                  )}
                  {movie.isNew && (
                    <Badge className="bg-primary text-primary-foreground">
                      NEW RELEASE
                    </Badge>
                  )}
                </div>
                <h1 className="text-4xl lg:text-5xl font-bold text-foreground mb-2">
                  {movie.title}
                </h1>
              </div>

              {/* Movie Info */}
              <div className="flex flex-wrap items-center gap-6 text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  <span className="font-medium">{movie.rating}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  <span>{movie.year}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  <span>{movie.duration}</span>
                </div>
              </div>

              {/* Genres */}
              <div className="flex flex-wrap gap-2">
                {movie.genre.map((genre) => (
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
                <p className="text-muted-foreground leading-relaxed text-lg">
                  {movie.synopsis}
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
                      {movie.director}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-foreground">Cast: </span>
                    <span className="text-muted-foreground">
                      {movie.cast.join(", ")}
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
            <VideoPlayer poster={movie.backdrop} title={movie.title} />
          </div>

          {/* Episodes Section (for series) */}
          {movie.episodes && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold text-foreground mb-6">
                Episodes
              </h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {movie.episodes.map((episode) => (
                  <Card
                    key={episode.id}
                    className="overflow-hidden cursor-pointer hover:shadow-card transition-shadow"
                  >
                    <img
                      src={episode.thumbnail}
                      alt={episode.title}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-4">
                      <h3 className="font-semibold text-foreground mb-2">
                        S{episode.seasonNumber}E{episode.episodeNumber}:{" "}
                        {episode.title}
                      </h3>
                      <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                        {episode.synopsis}
                      </p>
                      <span className="text-xs text-muted-foreground">
                        {episode.duration}
                      </span>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MovieDetails;
