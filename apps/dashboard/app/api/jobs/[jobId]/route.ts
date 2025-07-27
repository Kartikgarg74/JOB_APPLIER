import { NextResponse } from "next/server";

// TODO: Replace with real DB integration
let jobs = [];

export async function PATCH(request, { params }) {
  const { jobId } = params;
  const { status } = await request.json();
  const job = jobs.find(j => j.id === jobId);
  if (!job) {
    return NextResponse.json({ error: "Job not found" }, { status: 404 });
  }
  job.application_status = status;
  // In production, persist to DB here
  return NextResponse.json({ message: "Job status updated", job });
}
