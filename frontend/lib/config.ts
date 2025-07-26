// API Configuration for deployed services
export const API_CONFIG = {
  // Backend service URLs
  JOB_APPLIER_AGENT: process.env.NEXT_PUBLIC_JOB_APPLIER_AGENT_URL || 'https://job-applier-job-applier.onrender.com',
  ATS_SERVICE: process.env.NEXT_PUBLIC_ATS_SERVICE_URL || 'https://job-applier-ats-service.onrender.com',
  USER_SERVICE: process.env.NEXT_PUBLIC_USER_SERVICE_URL || 'https://job-applier-user-services.onrender.com',
  AGENT_ORCHESTRATION_SERVICE: process.env.NEXT_PUBLIC_AGENT_ORCHESTRATION_SERVICE_URL || 'https://job-applier-agent-orchestration-service.onrender.com',

  // API endpoints
  ENDPOINTS: {
    // Job Applier Agent endpoints
    APPLY_JOB: '/v1/apply-job',
    UPLOAD_RESUME: '/v1/upload-resume',
    NOTIFICATIONS: '/v1/notifications',

    // ATS Service endpoints
    ATS_SCORE: '/score_ats',
    ATS_SCORE_FILE: '/score_ats_file',
    SEARCH_JOBS: '/search_jobs',

    // User Service endpoints
    USER_PROFILE: '/v1/profile',
    USER_EDUCATION: '/v1/education',
    USER_EXPERIENCE: '/v1/experience',
    USER_PROJECTS: '/v1/projects',
    USER_SKILLS: '/v1/skills',
    USER_JOB_PREFERENCES: '/v1/job_preferences',

    // Agent Orchestration endpoints
    MATCH_JOBS: '/v1/match_jobs',
    AGENT_APPLY: '/v1/apply',
    UNICORN_MAGIC: '/v1/unicorn/perform_magic',

    // Auth endpoints (from Job Applier Agent)
    LOGIN: '/v1/auth/login',
    SIGNUP: '/v1/auth/signup',
    REFRESH_TOKEN: '/v1/auth/refresh',
  }
};

// Helper function to get full URL for a service endpoint
export function getServiceUrl(service: keyof typeof API_CONFIG, endpoint: string): string {
  const baseUrl = API_CONFIG[service];
  return `${baseUrl}${endpoint}`;
}

// Default API base URL (for backward compatibility)
export const DEFAULT_API_BASE_URL = API_CONFIG.JOB_APPLIER_AGENT;
