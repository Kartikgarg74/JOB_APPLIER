"use client";

import { useEffect, useState } from "react";

interface ApplicationStatus {
  jobId: string;
  status: string;
  lastUpdated: string;
}

export default function ApplicationStatusPage() {
  const [applicationStatus, setApplicationStatus] = useState<
    ApplicationStatus[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchApplicationStatus() {
      try {
        // In a real app, you'd fetch a list of applied job IDs first, then their statuses
        // For this example, we'll just use a dummy job ID
        const dummyJobIds = ["job-123", "job-456", "job-789"];
        const statuses = await Promise.all(
          dummyJobIds.map(async (id) => {
            const response = await fetch(`/api/application-status?jobId=${id}`);
            if (!response.ok) {
              throw new Error(
                `Failed to fetch status for ${id}: ${response.statusText}`,
              );
            }
            return response.json();
          }),
        );
        setApplicationStatus(statuses);
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

    fetchApplicationStatus();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading application statuses...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p className="text-red-500">Error: {error}</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <h1 className="text-4xl font-bold mb-8">Application Status</h1>

      {applicationStatus.length === 0 ? (
        <p>No applications found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-5xl">
          {applicationStatus.map((app) => (
            <div key={app.jobId} className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2">
                Job ID: {app.jobId}
              </h2>
              <p>
                <strong>Status:</strong> {app.status}
              </p>
              <p>
                <strong>Last Updated:</strong>{" "}
                {new Date(app.lastUpdated).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
