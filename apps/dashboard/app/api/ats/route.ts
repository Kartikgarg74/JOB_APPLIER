import { NextResponse } from "next/server";

export async function GET() {
  try {
    // In a real application, this would call the JobApplierAgent backend
    // to calculate the ATS score and feedback based on the user's resume
    // and a specific job description.
    const dummyAtsData = {
      score: 75,
      feedback: [
        "Your resume is well-structured and easy to read.",
        "Consider adding more quantifiable achievements to your work experience.",
        "Tailor your skills section more closely to the job description for higher relevance.",
        "Ensure keywords from the job description are naturally integrated.",
      ],
      job_id: "dummy-job-123",
    };

    return NextResponse.json(dummyAtsData);
  } catch (error) {
    console.error("Error fetching ATS data:", error);
    return NextResponse.json(
      { error: "Failed to fetch ATS data" },
      { status: 500 },
    );
  }
}
