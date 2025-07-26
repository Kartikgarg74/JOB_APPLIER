import { API_CONFIG, getServiceUrl } from './config';

// Types for Application Tracking
export interface Application {
  id: number;
  company: string;
  position: string;
  status: 'Applied' | 'Interview' | 'Rejected' | 'Offer' | 'On Hold';
  appliedDate: string;
  salary: string;
  location: string;
  logo?: string;
  atsScore: number;
  notes?: string;
}

// API call to fetch applications
export async function fetchApplications(): Promise<Application[]> {
  const url = getServiceUrl('JOB_APPLIER_AGENT', API_CONFIG.ENDPOINTS.NOTIFICATIONS);

  const result = await fetch(url);
  if (!result.ok) {
    let errMsg = "Failed to fetch applications";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

// API call to apply for a job
export async function applyForJob(jobUrl: string): Promise<void> {
  const formData = new FormData();
  formData.append("job_posting_url", jobUrl);

  const url = getServiceUrl('JOB_APPLIER_AGENT', API_CONFIG.ENDPOINTS.APPLY_JOB);

  const result = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!result.ok) {
    let errMsg = "Failed to apply for job";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
}

// API call to match jobs using Agent Orchestration Service
export async function matchJobs(userProfile: any): Promise<any> {
  const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', API_CONFIG.ENDPOINTS.MATCH_JOBS);

  const result = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_profile: userProfile }),
  });

  if (!result.ok) {
    let errMsg = "Failed to match jobs";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}
