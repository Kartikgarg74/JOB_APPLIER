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
  const result = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1"}/applications`);
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
  const result = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1"}/apply-for-job`, {
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
