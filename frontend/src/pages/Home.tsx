import { Navigation } from "@/components/Navigation";
import { HeroCarousel } from "@/components/HeroCarousel";
import { MovieCarousel } from "@/components/MovieCarousel";
import { getTrendingMovies, getNewReleases, getTopRated, mockMovies } from "@/data/movies";

const Home = () => {
  const trendingMovies = getTrendingMovies();
  const newReleases = getNewReleases();
  const topRated = getTopRated();

  // Simulated peer watching data (in a real app, this would come from analytics)
  const peerWatching = mockMovies.slice(2, 6);
  const youMightLike = mockMovies.slice(1, 5);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      {/* Hero Carousel */}
      <HeroCarousel movies={trendingMovies} />

      {/* Movie Sections */}
      <div className="py-16 space-y-16">
        {/* What Peers Are Watching */}
        <MovieCarousel
          title="What Peers Are Watching"
          movies={peerWatching}
          size="md"
        />

        {/* What You Might Like */}
        <MovieCarousel
          title="What You Might Like"
          movies={youMightLike}
          size="md"
        />

        {/* New Releases */}
        <MovieCarousel
          title="New Releases"
          movies={newReleases}
          size="lg"
        />

        {/* Top Rated */}
        <MovieCarousel
          title="Top Rated Movies"
          movies={topRated}
          size="md"
        />

        {/* Browse by Genre */}
        <div className="px-4">
          <h2 className="text-2xl font-bold text-foreground mb-6">Browse by Genre</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {["Action", "Comedy", "Drama", "Sci-Fi", "Romance", "Thriller"].map((genre) => (
              <div
                key={genre}
                className="bg-card border border-border rounded-lg p-6 text-center cursor-pointer hover:bg-accent hover:border-primary/50 transition-all duration-300 group"
              >
                <span className="text-lg font-medium text-foreground group-hover:text-primary transition-colors">
                  {genre}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-secondary/30 border-t border-border py-12 mt-16">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">S</span>
            </div>
            <span className="text-2xl font-bold text-foreground">StreamMovies</span>
          </div>
          <p className="text-muted-foreground">
            Your premium destination for the latest movies and shows
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
