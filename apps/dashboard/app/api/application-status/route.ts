import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get("jobId");

  // In a real application, this would fetch the actual application status from a database
  // For now, we'll return a dummy status that changes based on the jobId for demonstration
  const dummyStatuses = [
    "Applied",
    "In Review",
    "Interview Scheduled",
    "Rejected",
    "Offer Received",
  ];
  const status =
    dummyStatuses[Math.floor(Math.random() * dummyStatuses.length)];

  if (!jobId) {
    return NextResponse.json({ error: "Job ID is required" }, { status: 400 });
  }

  return NextResponse.json({
    jobId,
    status,
    lastUpdated: new Date().toISOString(),
  });
}
