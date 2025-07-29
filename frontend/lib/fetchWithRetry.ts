// frontend/lib/fetchWithRetry.ts

interface FetchOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
}

export async function fetchWithRetry(url: string, options?: FetchOptions): Promise<Response> {
  const { retries = 3, retryDelay = 1000, ...fetchOptions } = options || {};

  for (let i = 0; i <= retries; i++) {
    try {
      const response = await fetch(url, fetchOptions);
      if (!response.ok) {
        // If response is not OK, but not a network error, throw to retry
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response;
    } catch (error) {
      console.error(`Attempt ${i + 1} failed for ${url}:`, error);
      if (i < retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      } else {
        // Last retry failed, re-throw the error
        throw error;
      }
    }
  }
  // This part should ideally not be reached
  throw new Error('Fetch with retry failed after all attempts.');
}