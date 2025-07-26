"use client";
import React, { createContext, useContext, ReactNode } from 'react';
import { fetchApplications, applyForJob, matchJobs, createApplicationManually, updateApplicationStatus, deleteApplicationById } from './applications';
import { uploadResume } from './resume';
import { searchJobs } from './ats';
import { getUserProfile, updateUserProfile, getEducation, createEducation, getExperience, createExperience, getSkills, createSkill } from './user';

// Types for API services
export interface ApiServices {
  // Application management
  fetchApplications: typeof fetchApplications;
  applyForJob: typeof applyForJob;
  matchJobs: typeof matchJobs;
  createApplicationManually: typeof createApplicationManually;
  updateApplicationStatus: typeof updateApplicationStatus;
  deleteApplicationById: typeof deleteApplicationById;

  // File upload
  uploadResume: typeof uploadResume;

  // Job search and ATS
  searchJobs: typeof searchJobs;

  // User profile management
  getUserProfile: typeof getUserProfile;
  updateUserProfile: typeof updateUserProfile;
  getEducation: typeof getEducation;
  createEducation: typeof createEducation;
  getExperience: typeof getExperience;
  createExperience: typeof createExperience;
  getSkills: typeof getSkills;
  createSkill: typeof createSkill;
}

// Create the context
const ApiContext = createContext<ApiServices | undefined>(undefined);

// Provider component
export function ApiProvider({ children }: { children: ReactNode }) {
  const services: ApiServices = {
    // Application management
    fetchApplications,
    applyForJob,
    matchJobs,
    createApplicationManually,
    updateApplicationStatus,
    deleteApplicationById,

    // File upload
    uploadResume,

    // Job search and ATS
    searchJobs,

    // User profile management
    getUserProfile,
    updateUserProfile,
    getEducation,
    createEducation,
    getExperience,
    createExperience,
    getSkills,
    createSkill,
  };

  return (
    <ApiContext.Provider value={services}>
      {children}
    </ApiContext.Provider>
  );
}

// Hook to use the API services
export function useApiServices(): ApiServices {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApiServices must be used within an ApiProvider');
  }
  return context;
}
