"use client";

import { useEffect, useState } from "react";
import { useRef } from "react";

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

function exportToCSV(data: any[], filename: string) {
  if (!data.length) return;
  const keys = Object.keys(data[0]);
  const csv = [keys.join(",")].concat(
    data.map(row => keys.map(k => JSON.stringify(row[k] ?? "")).join(","))
  ).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function exportToJSON(data: any[], filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
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
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">Job Listings</h1>
        <div className="flex gap-2">
          <button
            aria-label="Export jobs as CSV"
            className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 focus:outline-none focus:ring"
            onClick={() => exportToCSV(jobListings, "job_listings.csv")}
            disabled={!jobListings.length}
          >
            Export CSV
          </button>
          <button
            aria-label="Export jobs as JSON"
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 focus:outline-none focus:ring"
            onClick={() => exportToJSON(jobListings, "job_listings.json")}
            disabled={!jobListings.length}
          >
            Export JSON
          </button>
        </div>
      </div>
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
