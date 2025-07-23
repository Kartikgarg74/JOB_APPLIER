"use client";

import { useEffect, useState } from "react";

interface JobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string;
  salary: string;
  posting_date: string;
  url: string;
  source: string;
  date_discovered: string;
  is_applied: boolean;
  application_status: string;
}

export default function JobsPage() {
  const [jobListings, setJobListings] = useState<JobListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await fetch("/api/jobs");
        if (!res.ok) {
          throw new Error(`Failed to fetch job listings: ${res.statusText}`);
        }
        const data: JobListing[] = await res.json();
        setJobListings(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unknown error occurred");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchJobs();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading job listings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-4xl font-bold mb-8">Job Listings</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {jobListings.map((job) => (
          <div key={job.id} className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-2">{job.title}</h2>
            <p className="text-gray-600 mb-1">
              <strong>Company:</strong> {job.company}
            </p>
            <p className="text-gray-600 mb-1">
              <strong>Location:</strong> {job.location}
            </p>
            <p className="text-gray-600 mb-1">
              <strong>Salary:</strong> {job.salary}
            </p>
            <p className="text-gray-600 mb-1">
              <strong>Status:</strong> {job.application_status}
            </p>
            <p className="text-gray-600 mb-4">
              <strong>Posted:</strong>{" "}
              {new Date(job.posting_date).toLocaleDateString()}
            </p>
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              View Job
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
