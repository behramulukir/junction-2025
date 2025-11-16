import type { Regulation, Overlap, Contradiction } from '../data/mockData';

// Get API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Request types
interface RegulationRequest {
  subcategory_id: string;
  subcategory_description: string;
  top_k?: number;
}

interface AnalysisRequest {
  subcategory_id: string;
  subcategory_description: string;
  top_k?: number;
}

// Response types
interface RegulationsResponse {
  regulations: Regulation[];
}

interface AnalysisResponse {
  overlaps: Overlap[];
  contradictions: Contradiction[];
}

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Fetch regulations for a given subcategory
 * @param subcategoryId - The ID of the subcategory (e.g., "1.1")
 * @param description - The description of the subcategory to search for
 * @param topK - Number of top results to return (default: 10)
 * @returns Array of regulations with similarity scores
 * @throws ApiError if the request fails
 */
export async function fetchRegulations(
  subcategoryId: string,
  description: string,
  topK: number = 10
): Promise<Regulation[]> {
  try {
    const requestBody: RegulationRequest = {
      subcategory_id: subcategoryId,
      subcategory_description: description,
      top_k: topK,
    };

    const response = await fetch(`${API_BASE_URL}/api/regulations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `Failed to fetch regulations: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    const data: RegulationsResponse = await response.json();
    return data.regulations;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network or other errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError('Unable to connect to server. Please ensure the backend is running.');
    }
    
    throw new ApiError(
      error instanceof Error ? error.message : 'An unexpected error occurred',
      undefined,
      error
    );
  }
}

/**
 * Fetch overlap and contradiction analysis for a given subcategory
 * @param subcategoryId - The ID of the subcategory (e.g., "1.1")
 * @param description - The description of the subcategory to analyze
 * @param topK - Number of top results to analyze (default: 30)
 * @returns Object containing arrays of overlaps and contradictions
 * @throws ApiError if the request fails
 */
export async function fetchAnalysis(
  subcategoryId: string,
  description: string,
  topK: number = 30
): Promise<{ overlaps: Overlap[]; contradictions: Contradiction[] }> {
  try {
    const requestBody: AnalysisRequest = {
      subcategory_id: subcategoryId,
      subcategory_description: description,
      top_k: topK,
    };

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `Failed to fetch analysis: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    const data: AnalysisResponse = await response.json();
    return {
      overlaps: data.overlaps,
      contradictions: data.contradictions,
    };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network or other errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError('Unable to connect to server. Please ensure the backend is running.');
    }
    
    throw new ApiError(
      error instanceof Error ? error.message : 'An unexpected error occurred',
      undefined,
      error
    );
  }
}
