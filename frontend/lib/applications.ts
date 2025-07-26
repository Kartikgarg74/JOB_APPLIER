import { API_CONFIG, getServiceUrl } from './config';
import { getApplications, createApplication, updateApplication, deleteApplication } from './supabase';

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
  created_at?: string;
  updated_at?: string;
}

// API call to fetch applications - now uses Supabase
export async function fetchApplications(): Promise<Application[]> {
  try {
    // First try to get from Supabase (real data)
    const supabaseData = await getApplications();
    if (supabaseData && supabaseData.length > 0) {
      return supabaseData.map((app: any) => ({
        id: app.id,
        company: app.company || 'Unknown Company',
        position: app.position || 'Unknown Position',
        status: app.status || 'Applied',
        appliedDate: app.applied_date || app.created_at || new Date().toISOString(),
        salary: app.salary || 'Not specified',
        location: app.location || 'Remote',
        logo: app.logo,
        atsScore: app.ats_score || 0,
        notes: app.notes,
        created_at: app.created_at,
        updated_at: app.updated_at
      }));
    }

    // Fallback to backend API if no Supabase data
    const url = getServiceUrl('JOB_APPLIER_AGENT', API_CONFIG.ENDPOINTS.NOTIFICATIONS);
    const result = await fetch(url);
    if (!result.ok) {
      throw new Error("Failed to fetch applications");
    }
    return result.json();
  } catch (error) {
    console.error('Error fetching applications:', error);
    throw new Error("Failed to fetch applications");
  }
}

// API call to apply for a job - now stores in Supabase
export async function applyForJob(jobUrl: string): Promise<void> {
  try {
    // First try backend API
    const formData = new FormData();
    formData.append("job_posting_url", jobUrl);

    const url = getServiceUrl('JOB_APPLIER_AGENT', API_CONFIG.ENDPOINTS.APPLY_JOB);

    const result = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!result.ok) {
      throw new Error("Failed to apply for job via backend");
    }

    const backendResponse = await result.json();

    // Store in Supabase
    await createApplication({
      company: backendResponse.company || 'Unknown Company',
      position: backendResponse.position || 'Unknown Position',
      status: 'Applied',
      applied_date: new Date().toISOString(),
      salary: backendResponse.salary || 'Not specified',
      location: backendResponse.location || 'Remote',
      ats_score: backendResponse.ats_score || 0,
      notes: `Applied via: ${jobUrl}`,
      job_url: jobUrl
    });

  } catch (error) {
    console.error('Error applying for job:', error);
    throw new Error("Failed to apply for job");
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

// New function to create application manually
export async function createApplicationManually(application: Omit<Application, 'id'>): Promise<Application> {
  try {
    const newApp = await createApplication({
      company: application.company,
      position: application.position,
      status: application.status,
      applied_date: application.appliedDate,
      salary: application.salary,
      location: application.location,
      logo: application.logo,
      ats_score: application.atsScore,
      notes: application.notes
    });

    return {
      id: newApp.id,
      company: newApp.company,
      position: newApp.position,
      status: newApp.status,
      appliedDate: newApp.applied_date,
      salary: newApp.salary,
      location: newApp.location,
      logo: newApp.logo,
      atsScore: newApp.ats_score,
      notes: newApp.notes
    };
  } catch (error) {
    console.error('Error creating application:', error);
    throw new Error("Failed to create application");
  }
}

// New function to update application
export async function updateApplicationStatus(id: number, status: Application['status'], notes?: string): Promise<void> {
  try {
    await updateApplication(id, { status, notes });
  } catch (error) {
    console.error('Error updating application:', error);
    throw new Error("Failed to update application");
  }
}

// New function to delete application
export async function deleteApplicationById(id: number): Promise<void> {
  try {
    await deleteApplication(id);
  } catch (error) {
    console.error('Error deleting application:', error);
    throw new Error("Failed to delete application");
  }
}
