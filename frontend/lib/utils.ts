import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { fetchWithRetry } from './fetchWithRetry';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// API utility for backend integration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1";

export const API_CONFIG = {
  ENDPOINTS: {
    USER_PROFILE: '/user/profile',
    USER_EDUCATION: '/user/education',
    USER_EXPERIENCE: '/user/experience',
    USER_SKILLS: '/user/skills',
    USER_JOB_PREFERENCES: '/user/job-preferences',
    USER_PROJECTS: '/user/projects',
  },
};

export function getServiceUrl(service: string, endpoint: string): string {
  // In a more complex setup, 'service' could map to different base URLs.
  // For now, we'll assume a single API_BASE_URL.
  return `${API_BASE_URL}${endpoint}`;
}

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
