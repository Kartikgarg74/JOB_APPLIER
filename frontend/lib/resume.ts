// Types for Resume Upload
export interface UploadResult {
  message: string;
  url?: string;
}

// API call to upload resume
export async function uploadResume(resumeFile: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", resumeFile);
  const result = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1"}/upload-resume`, {
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
