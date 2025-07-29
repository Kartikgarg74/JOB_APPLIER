import { fetchWithRetry } from './fetchWithRetry';
import { API_CONFIG, getServiceUrl } from './utils';

// Types for User Profile
export interface UserProfile {
  phone?: string;
  address?: string;
  portfolio_url?: string;
  personal_website?: string;
  linkedin_profile?: string;
  github_profile?: string;
  years_of_experience?: number;
  skills?: any[];
  onboarding_complete?: boolean;
  onboarding_step?: string;
  job_preferences?: any;
}

export interface Education {
  id?: number;
  degree: string;
  university: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  description?: string;
}

export interface Experience {
  id?: number;
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date?: string;
  description?: string;
}

export interface Project {
  id?: number;
  name: string;
  description?: string;
  technologies?: string;
  url?: string;
}

export interface Skill {
  id?: number;
  name: string;
  proficiency?: string;
  technologies?: string;
  url?: string;
}

export interface JobPreference {
  id?: number;
  company_size?: string;
  industry?: string;
  job_titles?: string;
  locations?: string;
  remote?: boolean;
  job_type?: string;
  location?: string;
  notifications?: boolean;
}

// User Profile API calls
export async function getUserProfile(): Promise<UserProfile> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_PROFILE);

  const result = await fetchWithRetry(url, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!result.ok) {
    let errMsg = "Failed to fetch user profile";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

export async function updateUserProfile(profile: UserProfile): Promise<UserProfile> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_PROFILE);

  const result = await fetchWithRetry(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(profile),
  });

  if (!result.ok) {
    let errMsg = "Failed to update user profile";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

// Education API calls
export async function getEducation(): Promise<Education[]> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_EDUCATION);

  const result = await fetchWithRetry(url, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!result.ok) {
    let errMsg = "Failed to fetch education";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

export async function createEducation(education: Education): Promise<Education> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_EDUCATION);

  const result = await fetchWithRetry(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(education),
  });

  if (!result.ok) {
    let errMsg = "Failed to create education";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

// Experience API calls
export async function getExperience(): Promise<Experience[]> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_EXPERIENCE);

  const result = await fetchWithRetry(url, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!result.ok) {
    let errMsg = "Failed to fetch experience";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

export async function createExperience(experience: Experience): Promise<Experience> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_EXPERIENCE);

  const result = await fetchWithRetry(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(experience),
  });

  if (!result.ok) {
    let errMsg = "Failed to create experience";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

// Skills API calls
export async function getSkills(): Promise<Skill[]> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_SKILLS);

  const result = await fetchWithRetry(url, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!result.ok) {
    let errMsg = "Failed to fetch skills";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

export async function createSkill(skill: Skill): Promise<Skill> {
  const url = getServiceUrl('USER_SERVICE', API_CONFIG.ENDPOINTS.USER_SKILLS);

  const result = await fetchWithRetry(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(skill),
  });

  if (!result.ok) {
    let errMsg = "Failed to create skill";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}
