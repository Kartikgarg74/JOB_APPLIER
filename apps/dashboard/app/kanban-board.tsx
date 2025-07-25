"use client";

import React, { useEffect, useState } from "react";

const columns = ["To Apply", "Applied", "Interview", "Offer", "Rejected"];

interface Job {
  id: string;
  title: string;
  application_status: string;
  // Add other properties as needed
}

export default function KanbanBoard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [draggedJob, setDraggedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  async function fetchJobs() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/jobs");
      if (!res.ok) throw new Error("Failed to fetch jobs");
      const data = await res.json();
      setJobs(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const onDragStart = (job: Job) => setDraggedJob(job);
  const onDrop = async (status: string) => {
    if (draggedJob) {
      try {
        const res = await fetch(`/api/jobs/${draggedJob.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        });
        if (!res.ok) throw new Error("Failed to update job status");
        const updated = await res.json();
        setJobs(jobs.map(j => j.id === draggedJob.id ? updated.job : j));
      } catch (e) {
        setError(e.message);
      } finally {
        setDraggedJob(null);
      }
    }
  };

  if (loading) return <div className="p-4">Loading jobs...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  return (
    <div className="flex flex-col md:flex-row gap-4 w-full overflow-x-auto">
      {columns.map(col => (
        <div
          key={col}
          className="flex-1 min-w-[220px] bg-gray-100 rounded-lg p-4 shadow-md"
          onDragOver={e => e.preventDefault()}
          onDrop={() => onDrop(col)}
          aria-label={`${col} column`}
        >
          <h2 className="text-lg font-bold mb-2">{col}</h2>
          <div className="flex flex-col gap-2 min-h-[60px]">
            {jobs.filter(j => j.application_status === col).map(job => (
              <div
                key={job.id}
                className="bg-white rounded p-2 shadow cursor-move"
                draggable
                onDragStart={() => onDragStart(job)}
                tabIndex={0}
                aria-label={`Job: ${job.title}`}
              >
                {job.title}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
