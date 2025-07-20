export const BASE_URL = "http://localhost:8000";

export const BACKEND_ENDPOINTS = {
  REGISTER: BASE_URL + "/register/",
  GET_AUTH_TOKEN: BASE_URL + "/get_auth_token/",
};

// API service functions
export const API_BASE_URL = "http://localhost:8000/api";

export interface Recommendation {
  movie_id: number;
  title: string;
  score: number;
  poster_url?: string;
  overview?: string;
  vote_average?: number;
}

export interface RatingData {
  movie_id: number;
  rating: number;
}

export interface InteractionData {
  movie_id: number;
  type:
    | "view"
    | "like"
    | "dislike"
    | "share"
    | "watchlist_add"
    | "watchlist_remove";
}

export class APIService {
  private static async getAuthHeaders() {
    // In a real app, you'd get the token from localStorage, context, or cookies
    const token = localStorage.getItem("token");
    return {
      "Content-Type": "application/json",
      Authorization: token ? `Token ${token}` : "",
    };
  }

  static async getRecommendations(
    count: number = 10,
  ): Promise<Recommendation[]> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(
        `${API_BASE_URL}/recommendations/?count=${count}`,
        {
          headers,
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.success ? data.recommendations : [];
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      return [];
    }
  }

  static async addRating(movieId: number, rating: number): Promise<boolean> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}/ratings/`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          movie_id: movieId,
          rating: rating,
        }),
      });

      const data = await response.json();
      console.log("add rating", data);
      return data.success || false;
    } catch (error) {
      console.error("Error adding rating:", error);
      return false;
    }
  }

  static async addInteraction(movieId: number, type: string): Promise<boolean> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}/interactions/`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          movie_id: movieId,
          type: type,
        }),
      });

      const data = await response.json();
      return data.success || false;
    } catch (error) {
      console.error("Error adding interaction:", error);
      return false;
    }
  }
}
