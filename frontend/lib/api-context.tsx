"use client";
import React, { createContext, useContext, ReactNode } from 'react';
import { fetchAtsScore, searchJobs, AtsResults } from './ats';
import { fetchApplications, applyForJob, matchJobs, Application } from './applications';
import { uploadResume, UploadResult } from './resume';
import {
  getUserProfile, updateUserProfile, getEducation, createEducation,
  getExperience, createExperience, getSkills, createSkill,
  UserProfile, Education, Experience, Skill
} from './user';

interface ApiServices {
  // ATS Service
  fetchAtsScore: typeof fetchAtsScore;
  searchJobs: typeof searchJobs;

  // Job Applier Agent
  fetchApplications: typeof fetchApplications;
  applyForJob: typeof applyForJob;
  uploadResume: typeof uploadResume;

  // Agent Orchestration Service
  matchJobs: typeof matchJobs;

  // User Service
  getUserProfile: typeof getUserProfile;
  updateUserProfile: typeof updateUserProfile;
  getEducation: typeof getEducation;
  createEducation: typeof createEducation;
  getExperience: typeof getExperience;
  createExperience: typeof createExperience;
  getSkills: typeof getSkills;
  createSkill: typeof createSkill;
}

const ApiContext = createContext<ApiServices | undefined>(undefined);

export const ApiProvider = ({ children }: { children: ReactNode }) => {
  return (
    <ApiContext.Provider
      value={{
        // ATS Service
        fetchAtsScore,
        searchJobs,

        // Job Applier Agent
        fetchApplications,
        applyForJob,
        uploadResume,

        // Agent Orchestration Service
        matchJobs,

        // User Service
        getUserProfile,
        updateUserProfile,
        getEducation,
        createEducation,
        getExperience,
        createExperience,
        getSkills,
        createSkill,
      }}
    >
      {children}
    </ApiContext.Provider>
  );
};

export function useApiServices(): ApiServices {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApiServices must be used within an ApiProvider');
  }
  return context;
}

// Export types for use in components
export type {
  AtsResults, Application, UploadResult,
  UserProfile, Education, Experience, Skill
};
