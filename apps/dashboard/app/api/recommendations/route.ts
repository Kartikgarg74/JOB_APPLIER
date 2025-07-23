import { NextResponse } from "next/server";

export async function GET() {
  // In a real application, this would fetch job recommendations from a backend service
  // based on user profile, resume, and application history.
  const dummyRecommendations = [
    {
      id: "rec1",
      title: "Senior Software Engineer",
      company: "Tech Solutions Inc.",
      location: "Remote",
      description:
        "Seeking a senior software engineer with 5+ years of experience in full-stack development.",
      match_score: 92,
      reason:
        "High match with Python, React, and AWS skills from your resume and preferences.",
    },
    {
      id: "rec2",
      title: "Machine Learning Engineer",
      company: "AI Innovations",
      location: "San Francisco, CA",
      description:
        "Develop and deploy machine learning models for cutting-edge AI products.",
      match_score: 88,
      reason:
        "Strong alignment with your Data Science and ML education and experience.",
    },
    {
      id: "rec3",
      title: "Cloud Architect",
      company: "Global Cloud Services",
      location: "New York, NY (Hybrid)",
      description:
        "Design and implement scalable cloud infrastructure solutions on AWS.",
      match_score: 75,
      reason:
        "Good match with your AWS skills, but experience in architecture is a plus.",
    },
  ];

  return NextResponse.json(dummyRecommendations);
}
