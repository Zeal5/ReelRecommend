import { API_BASE_URL } from "./constants";

export interface Movie {
  id: number;
  title: string;
  overview: string; // Renamed from synopsis
  year: number;
  genres: string; // Genres are now a single string, e.g., "Action|Adventure|Sci-Fi"
  vote_average: number; // Renamed from rating
  runtime?: number; // Renamed from duration and is now a number (in minutes)
  poster_url: string; // Renamed from poster
  backdrop_url: string; // Renamed from backdrop
  trailer?: string; // This field may not be in your backend model yet
  actors?: string; // Actors are a single string "Actor One|Actor Two"
  director?: string;
  popularity?: number;
  vote_count?: number;
	imdb_id?: string;
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

// Enhanced API response interface to handle backend response structure
interface APIResponse<T> {
  success?: boolean;
  data?: T;
  error?: string;
  // Handle direct array responses or nested data responses
}

// Helper function to handle API requests with better error handling
async function fetchFromAPI<T>(endpoint: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    console.log(`Fetching from: ${API_BASE_URL}${endpoint}`, response);

    if (!response.ok) {
      // Handle different HTTP status codes
      if (response.status === 404) {
        throw new Error(`Resource not found: ${endpoint}`);
      } else if (response.status === 500) {
        throw new Error(`Server error: ${response.statusText}`);
      } else if (response.status >= 400) {
        throw new Error(
          `Client error: ${response.status} ${response.statusText}`,
        );
      }
      throw new Error(`Network response was not ok: ${response.statusText}`);
    }

    const data = await response.json();

    // Handle different response formats from backend
    // If response has a 'success' field and it's false, throw an error
    if (
      typeof data === "object" &&
      data !== null &&
      "success" in data &&
      !data.success
    ) {
      throw new Error(data.error || "API request failed");
    }

    // Return the data directly if it's an array or the expected structure
    return data;
  } catch (error) {
    console.error(`Failed to fetch from endpoint ${endpoint}:`, error);
    throw error; // Re-throw the error to be handled by the caller
  }
}

// Enhanced function to validate movie data structure
function validateMovieData(movie: any): Movie | null {
  try {
    // Check required fields
    if (!movie || typeof movie !== "object") return null;
    if (!movie.id || !movie.title) return null;

    // Return movie with default values for missing fields
    return {
      id: Number(movie.id),
      title: String(movie.title || "Untitled"),
      overview: String(movie.overview || "No description available"),
      year: Number(movie.year || new Date().getFullYear()),
      genres: String(movie.genres || "Unknown"),
      vote_average: Number(movie.vote_average || 0),
      runtime: movie.runtime ? Number(movie.runtime) : undefined,
      poster_url: String(movie.poster_url || "/api/placeholder/300/450"),
      backdrop_url: String(movie.backdrop_url || "/api/placeholder/1200/675"),
      trailer: movie.trailer ? String(movie.trailer) : undefined,
      actors: movie.actors ? String(movie.actors) : undefined,
      director: movie.director ? String(movie.director) : undefined,
      popularity: movie.popularity ? Number(movie.popularity) : undefined,
      vote_count: movie.vote_count ? Number(movie.vote_count) : undefined,
			imdb_id: movie.imdb_id ? movie.imdb_id : undefined
    };
  } catch (error) {
    console.error("Error validating movie data:", error, movie);
    return null;
  }
}

// Enhanced function to validate and clean movie arrays
function validateMovieArray(data: any): Movie[] {
  if (!Array.isArray(data)) {
    console.warn("Expected array but received:", typeof data, data);
    return [];
  }

  const validMovies = data
    .map(validateMovieData)
    .filter((movie): movie is Movie => movie !== null);

  console.log(
    `Validated ${validMovies.length} movies out of ${data.length} received`,
  );
  return validMovies;
}

// Rewritten functions to fetch data from the Django backend with better error handling
export const getMovieById = async (id: number): Promise<Movie | undefined> => {
	console.log(`Fetching movie with id ${id}`);
  try {
    const data = await fetchFromAPI<Movie>(`/movies/${id}/`);
    const validatedMovie = validateMovieData(data);
    return validatedMovie || undefined;
  } catch (error) {
    console.error(`Failed to get movie with id ${id}:`, error);
    return undefined; // Return undefined if the movie is not found or an error occurs
  }
};

export const getTrendingMovies = async (): Promise<Movie[]> => {
  try {
    const data = await fetchFromAPI<Movie[] | APIResponse<Movie[]>>(
      `/movies/trending/`,
    );

    // Handle different response structures
    const movieArray = Array.isArray(data)
      ? data
      : (data as APIResponse<Movie[]>).data || [];

    const validatedMovies = validateMovieArray(movieArray);
    return validatedMovies;
  } catch (error) {
    console.error("Failed to get trending movies:", error);
    // Return empty array instead of throwing error
    return [];
  }
};

export const getNewReleases = async (): Promise<Movie[]> => {
  try {
    const data = await fetchFromAPI<Movie[] | APIResponse<Movie[]>>(
      `/movies/new-releases/`,
    );

    // Handle different response structures
    const movieArray = Array.isArray(data)
      ? data
      : (data as APIResponse<Movie[]>).data || [];

    const validatedMovies = validateMovieArray(movieArray);
    return validatedMovies;
  } catch (error) {
    console.error("Failed to get new releases:", error);
    // Return empty array instead of throwing error
    return [];
  }
};

export const getTopRated = async (): Promise<Movie[]> => {
  try {
    const data = await fetchFromAPI<Movie[] | APIResponse<Movie[]>>(
      `/movies/top-rated/`,
    );

    // Handle different response structures
    const movieArray = Array.isArray(data)
      ? data
      : (data as APIResponse<Movie[]>).data || [];

    const validatedMovies = validateMovieArray(movieArray);
    return validatedMovies;
  } catch (error) {
    console.error("Failed to get top-rated movies:", error);
    // Return empty array instead of throwing error
    return [];
  }
};




















