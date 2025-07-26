import { API_CONFIG, getServiceUrl } from './config';

// Types for ATS API
export interface AtsSuggestion {
  type: 'success' | 'warning' | 'info';
  title: string;
  description: string;
  impact: string;
}

export interface AtsSkillAnalysis {
  skill: string;
  required: boolean;
  match: number;
}

export interface AtsResults {
  score: number;
  grade: string;
  skillsMatch: number;
  keywordsMatch: number;
  suggestions: AtsSuggestion[];
  skillsAnalysis: AtsSkillAnalysis[];
}

// API call for ATS scoring
export async function fetchAtsScore(
  resumeFile: File,
  jobDescription: string
): Promise<AtsResults> {
  const formData = new FormData();
  formData.append("resume_file", resumeFile);
  formData.append("job_description", jobDescription);

  const url = getServiceUrl('ATS_SERVICE', API_CONFIG.ENDPOINTS.ATS_SCORE_FILE);

  const result = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!result.ok) {
    let errMsg = "Failed to get ATS score";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

// API call for job search
export async function searchJobs(
  query: string,
  location: string = "",
  numResults: number = 10,
  sources: string[] = ["indeed", "linkedin", "glassdoor", "company"]
): Promise<any> {
  const formData = new FormData();
  formData.append("query", query);
  formData.append("location", location);
  formData.append("num_results", numResults.toString());
  sources.forEach(source => formData.append("sources", source));

  const url = getServiceUrl('ATS_SERVICE', API_CONFIG.ENDPOINTS.SEARCH_JOBS);

  const result = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!result.ok) {
    let errMsg = "Failed to search jobs";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}
