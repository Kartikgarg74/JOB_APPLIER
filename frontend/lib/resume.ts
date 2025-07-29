import { fetchWithRetry } from './fetchWithRetry';
import { API_CONFIG, getServiceUrl } from './config';

// Types for Resume Upload
export interface UploadResult {
  message: string;
  url?: string;
}

// API call to upload resume
export async function uploadResume(resumeFile: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", resumeFile);

  const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', API_CONFIG.ENDPOINTS.UPLOAD_RESUME);

  const result = await fetchWithRetry(url, {
    method: "POST",
    body: formData,
  });

  if (!result.ok) {
    let errMsg = "Failed to upload resume";
    try {
      const err = await result.json();
      errMsg = err.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }
  return result.json();
}
