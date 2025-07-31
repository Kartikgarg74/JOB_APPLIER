"use client";
import React, { createContext, useContext, ReactNode } from 'react';
import { fetchApplications, createApplication, matchJobs, updateApplication, deleteApplication, submitJobApplication } from './applications';
import { uploadResume } from './resume';
import { searchJobs, fetchAtsScore } from './ats';
import { getUserProfile, updateUserProfile, getEducation, createEducation, getExperience, createExperience, getSkills, createSkill } from './user';
import axios, { AxiosInstance } from 'axios';

// Types for API services
export interface ApiServices {
  // Application management
  fetchApplications: typeof fetchApplications;
  createApplication: typeof createApplication;
  matchJobs: typeof matchJobs;
  updateApplication: typeof updateApplication;
  deleteApplication: typeof deleteApplication;
  submitJobApplication: typeof submitJobApplication;

  // File upload
  uploadResume: typeof uploadResume;

  // Job search and ATS
  searchJobs: typeof searchJobs;
  fetchAtsScore: typeof fetchAtsScore;

  // User profile management
  getUserProfile: typeof getUserProfile;
  updateUserProfile: typeof updateUserProfile;
  getEducation: typeof getEducation;
  createEducation: typeof createEducation;
  getExperience: typeof getExperience;
  createExperience: typeof createExperience;
  getSkills: typeof getSkills;
  createSkill: typeof createSkill;
  AGENT_ORCHESTRATION_SERVICE: AxiosInstance;
}

// Create the context
const ApiContext = createContext<ApiServices | undefined>(undefined);

// Provider component
export function ApiProvider({ children }: { children: ReactNode }) {
  const services: ApiServices = {
    // Application management
    fetchApplications,
    createApplication,
    matchJobs,
    updateApplication,
    deleteApplication,
    submitJobApplication,

    // File upload
    uploadResume,

    // Job search and ATS
    searchJobs,
    fetchAtsScore,

    // User profile management
    getUserProfile,
    updateUserProfile,
    getEducation,
    createEducation,
    getExperience,
    createExperience,
    getSkills,
    createSkill,
    AGENT_ORCHESTRATION_SERVICE: axios.create({
      baseURL: process.env.NEXT_PUBLIC_AGENT_ORCHESTRATION_SERVICE_URL || 'http://localhost:8000/api',
    }),
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
