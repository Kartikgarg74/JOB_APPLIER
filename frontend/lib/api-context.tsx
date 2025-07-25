"use client";
import React, { createContext, useContext, ReactNode } from 'react';
import { fetchAtsScore, AtsResults } from './ats';
import { fetchApplications, applyForJob, Application } from './applications';
import { uploadResume, UploadResult } from './resume';

interface ApiServices {
  fetchAtsScore: typeof fetchAtsScore;
  fetchApplications: typeof fetchApplications;
  applyForJob: typeof applyForJob;
  uploadResume: typeof uploadResume;
}

const ApiContext = createContext<ApiServices | undefined>(undefined);

export const ApiProvider = ({ children }: { children: ReactNode }) => {
  return (
    <ApiContext.Provider
      value={{
        fetchAtsScore,
        fetchApplications,
        applyForJob,
        uploadResume,
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
