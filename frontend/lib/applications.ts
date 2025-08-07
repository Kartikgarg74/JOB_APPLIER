import { fetchWithRetry } from './fetchWithRetry';
import { API_CONFIG, getServiceUrl } from './config';

// This is the primary data type used by the UI components.
export interface Application {
  id: number;
  company: string;
  position: string;
  status: 'applied' | 'reviewed' | 'interview' | 'offer' | 'rejected';
  appliedDate: string; // ISO string
  salary: string;
  location: string;
  notes?: string;
  jobUrl?: string | null;
  logo?: string;
  atsScore?: number;
  jobMatchScore?: number;
  responseTime?: string; // e.g., "5 days"
  interviewDate?: string; // ISO string
  offerDetails?: string;
  rejectionReason?: string;
}

export interface ApplicationSubmissionRequest {
  job_id: string;
  user_id: string;
  resume_id: string;
  cover_letter_content?: string;
  application_url: string;
  additional_data?: Record<string, any>;
}

export interface ApplicationSubmissionResponse {
  status: string;
  message: string;
  application_id?: string;
  details?: Record<string, any>;
}

// This interface matches the raw data from the backend API
export interface ApiApplication {
  id: number;
  user_id: number;
  job_id: string;
  status: string;
  applied_at: string;
  updated_at: string;
  resume_id: number | null;
  cover_letter: string | null;
  job: {
    title: string;
    company: string;
    location: string;
    salary: string | null;
    url: string | null;
  };
  response_time?: string;
  interview_date?: string;
  offer_details?: string;
  rejection_reason?: string;
}

// Data required for creating a new application
export interface CreateApplicationData {
  userId: number;
  jobId: string;
  status: Application['status'];
  resumeId?: number;
  notes?: string; // Mapped to cover_letter
}

// Data required for updating an application
export interface UpdateApplicationData {
  status: 'Applied' | 'Interview' | 'Rejected' | 'Offer' | 'On Hold';
  notes?: string;
  resumeId?: number;
}

// Helper to map API response to the UI's Application type
function mapApiToUiApplication(apiApp: ApiApplication): Application {
  return {
    id: apiApp.id,
    company: apiApp.job.company,
    position: apiApp.job.title,
    status: apiApp.status as Application['status'],
    appliedDate: apiApp.applied_at,
    salary: apiApp.job.salary || 'N/A',
    location: apiApp.job.location,
    notes: apiApp.cover_letter || undefined,
    jobUrl: apiApp.job.url,
    atsScore: 0, // Placeholder
    jobMatchScore: 0, // Placeholder
    responseTime: apiApp.response_time,
    interviewDate: apiApp.interview_date,
    offerDetails: apiApp.offer_details,
    rejectionReason: apiApp.rejection_reason,
  };
}

// --- CRUD Functions --- 

/**
 * Fetches all job applications for a given user.
 * @param userId The ID of the user.
 * @returns A promise that resolves to an array of applications.
 */
export async function fetchApplications(userId: number): Promise<Application[]> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', `/v1/applications/${userId}`);
    const response = await fetchWithRetry(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch applications: ${response.statusText}`);
    }
    const apiApplications: ApiApplication[] = await response.json();
    return apiApplications.map(mapApiToUiApplication);
  } catch (error) {
    console.error('Error fetching applications:', error);
    // Return empty array on error to prevent UI crashes
    return [];
  }
}

export async function matchJobs(userProfile: { jobTitle?: string, location?: string }): Promise<any> {
  // This function is being refactored to use the existing /v1/job-search endpoint
  // on the JOB_APPLIER_AGENT service, as the originally intended endpoint does not exist.
  const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', '/v1/job-search');

  const result = await fetchWithRetry(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: userProfile.jobTitle || "Software Engineer", // Default query if not provided
      location: userProfile.location || "",
      num_results: 20,
    }),
  });

  if (!result.ok) {
    let errMsg = "Failed to match jobs";
    try {
      const err = await result.json();
      errMsg = err.detail || err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}

/**
 * Creates a new job application record.
 * @param appData The data for the new application.
 * @returns A promise that resolves to the newly created application.
 */
export async function createApplication(appData: CreateApplicationData): Promise<Application> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', '/v1/applications/');
    const response = await fetchWithRetry(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: appData.userId,
        job_id: appData.jobId,
        status: appData.status,
        resume_id: appData.resumeId,
        cover_letter: appData.notes,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Failed to create application: ${errorData.detail}`);
    }
    const newApiApp: ApiApplication = await response.json();
    return mapApiToUiApplication(newApiApp);
  } catch (error) {
    console.error('Error creating application:', error);
    throw error;
  }
}

/**
 * Submits a job application through the Agent Orchestration Service.
 * @param submissionData The data required for submitting the application.
 * @returns A promise that resolves to the submission response.
 */
export async function submitJobApplication(submissionData: ApplicationSubmissionRequest): Promise<ApplicationSubmissionResponse> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', '/applications/submit');
    const response = await fetchWithRetry(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(submissionData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Failed to submit application: ${errorData.detail}`);
    }
    return response.json();
  } catch (error) {
    console.error('Error submitting job application:', error);
    throw error;
  }
}

/**
 * Updates an existing job application.
 * @param applicationId The ID of the application to update.
 * @param updateData The data to update.
 * @returns A promise that resolves to the updated application.
 */
export async function updateApplication(
  applicationId: number,
  updateData: UpdateApplicationData
): Promise<Application> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', `/v1/applications/${applicationId}`);
    const response = await fetchWithRetry(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: updateData.status,
        resume_id: updateData.resumeId,
        cover_letter: updateData.notes,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Failed to update application: ${errorData.detail}`);
    }
    const updatedApiApp: ApiApplication = await response.json();
    return mapApiToUiApplication(updatedApiApp);
  } catch (error) {
    console.error('Error updating application:', error);
    throw error;
  }
}

/**
 * Deletes a job application.
 * @param applicationId The ID of the application to delete.
 * @returns A promise that resolves when the application is deleted.
 */
export async function deleteApplication(applicationId: number): Promise<void> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', `/v1/applications/${applicationId}`);
    const response = await fetchWithRetry(url, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Failed to delete application: ${errorData.detail}`);
    }
  } catch (error) {
    console.error('Error deleting application:', error);
    throw error;
  }
}

/**
 * Sends a request to the job applier agent to apply for a job.
 * @param userId The ID of the user applying.
 * @param jobId The ID of the job to apply for.
 * @returns A promise that resolves with the application status.
 */
export async function applyForJob(userId: number, jobId: string): Promise<any> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', '/v1/apply');
    const response = await fetchWithRetry(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        job_id: jobId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Failed to apply for job: ${errorData.detail}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error applying for job:', error);
    throw error;
  }
}
