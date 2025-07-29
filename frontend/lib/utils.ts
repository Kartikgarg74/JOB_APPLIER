import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { fetchWithRetry } from './fetchWithRetry';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// API utility for backend integration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1";

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetchWithRetry(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      'Accept': 'application/json',
    },
    credentials: 'include',
  });
  if (!res.ok) {
    let errorMsg = `API error: ${res.status}`;
    try {
      const err = await res.json();
      errorMsg = err.message || errorMsg;
    } catch {}
    throw new Error(errorMsg);
  }
  return res.json();
}
