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

  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <div className="flex justify-between items-center w-full max-w-5xl mb-8">
        <h1 className="text-4xl font-bold">Application Status</h1>
        <div className="flex gap-2">
          <button
            aria-label="Export application statuses as CSV"
            className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 focus:outline-none focus:ring"
            onClick={() => exportToCSV(applicationStatus, "application_statuses.csv")}
            disabled={!applicationStatus.length}
          >
            Export CSV
          </button>
          <button
            aria-label="Export application statuses as JSON"
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 focus:outline-none focus:ring"
            onClick={() => exportToJSON(applicationStatus, "application_statuses.json")}
            disabled={!applicationStatus.length}
          >
            Export JSON
          </button>
        </div>
      </div>

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
