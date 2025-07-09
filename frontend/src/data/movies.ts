export interface Movie {
  id: string;
  title: string;
  synopsis: string;
  year: number;
  genre: string[];
  rating: number;
  duration: string;
  poster: string;
  backdrop: string;
  trailer?: string;
  cast: string[];
  director: string;
  isNew?: boolean;
  isTrending?: boolean;
  episodes?: Episode[];
}

export interface Episode {
  id: string;
  title: string;
  synopsis: string;
  duration: string;
  thumbnail: string;
  episodeNumber: number;
  seasonNumber: number;
}

export const mockMovies: Movie[] = [
  {
    id: "1",
    title: "Nebula Rising",
    synopsis: "A stunning space epic about humanity's first contact with an alien civilization that challenges everything we thought we knew about the universe.",
    year: 2024,
    genre: ["Sci-Fi", "Adventure", "Drama"],
    rating: 8.7,
    duration: "2h 28m",
    poster: "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=400&h=600&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=1200&h=675&fit=crop",
    cast: ["Emma Stone", "Oscar Isaac", "Mahershala Ali", "Lupita Nyong'o"],
    director: "Denis Villeneuve",
    isTrending: true,
    isNew: true
  },
  {
    id: "2",
    title: "The Digital Heist",
    synopsis: "A group of hackers attempts the ultimate digital robbery while being hunted by both the FBI and dangerous criminals.",
    year: 2024,
    genre: ["Thriller", "Crime", "Action"],
    rating: 8.2,
    duration: "2h 15m",
    poster: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=600&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1200&h=675&fit=crop",
    cast: ["Michael Shannon", "Anya Taylor-Joy", "John Boyega", "Zendaya"],
    director: "Christopher Nolan",
    isTrending: true
  },
  {
    id: "3",
    title: "Lost Kingdoms",
    synopsis: "An epic fantasy adventure following a young warrior's quest to unite the scattered kingdoms against an ancient evil.",
    year: 2023,
    genre: ["Fantasy", "Adventure", "Action"],
    rating: 9.1,
    duration: "2h 45m",
    poster: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=600&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1200&h=675&fit=crop",
    cast: ["Tom Holland", "Saoirse Ronan", "Dev Patel", "Tilda Swinton"],
    director: "Peter Jackson",
    isTrending: true
  },
  {
    id: "4",
    title: "Midnight in Paris",
    synopsis: "A romantic drama about a writer who mysteriously travels back in time every night at midnight in the City of Light.",
    year: 2023,
    genre: ["Romance", "Drama", "Comedy"],
    rating: 7.8,
    duration: "1h 54m",
    poster: "https://images.unsplash.com/photo-1502602898536-47ad22581b52?w=400&h=600&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1502602898536-47ad22581b52?w=1200&h=675&fit=crop",
    cast: ["Timothée Chalamet", "Florence Pugh", "Oscar Isaac", "Marion Cotillard"],
    director: "Lulu Wang"
  },
  {
    id: "5",
    title: "Quantum Detective",
    synopsis: "A detective uses quantum physics to solve crimes across multiple parallel universes in this mind-bending thriller.",
    year: 2024,
    genre: ["Sci-Fi", "Mystery", "Thriller"],
    rating: 8.5,
    duration: "2h 12m",
    poster: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&h=600&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1200&h=675&fit=crop",
    cast: ["Benedict Cumberbatch", "Viola Davis", "Rami Malek", "Cate Blanchett"],
    director: "Rian Johnson",
    isNew: true
  },
  {
    id: "6",
    title: "Ocean's Legacy",
    synopsis: "The final adventure of the world's greatest thieves as they pull off one last impossible heist.",
    year: 2023,
    genre: ["Action", "Comedy", "Crime"],
    rating: 8.0,
    duration: "2h 8m",
    poster: "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=600&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1200&h=675&fit=crop",
    cast: ["Ryan Gosling", "Margot Robbie", "Idris Elba", "Sandra Bullock"],
    director: "Steven Soderbergh"
  }
];

export const getMovieById = (id: string): Movie | undefined => {
  return mockMovies.find(movie => movie.id === id);
};

export const getTrendingMovies = (): Movie[] => {
  return mockMovies.filter(movie => movie.isTrending);
};

export const getNewReleases = (): Movie[] => {
  return mockMovies.filter(movie => movie.isNew);
};

export const getTopRated = (): Movie[] => {
  return mockMovies.sort((a, b) => b.rating - a.rating);
};