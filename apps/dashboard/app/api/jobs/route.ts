import { NextResponse } from "next/server";

export async function GET() {
  // In a real application, this would fetch data from your backend database
  const dummyJobs = [
    {
      id: "1",
      title: "Software Engineer",
      company: "Tech Solutions Inc.",
      location: "San Francisco, CA",
      description: "Develop and maintain web applications.",
      requirements: "3+ years of experience with React and Node.js",
      salary: "$120,000 - $150,000",
      posting_date: "2023-10-26T10:00:00Z",
      url: "https://example.com/job/1",
      source: "LinkedIn",
      date_discovered: "2023-10-26T10:00:00Z",
      is_applied: false,
      application_status: "Pending",
    },
    {
      id: "2",
      title: "Data Scientist",
      company: "Data Insights Corp.",
      location: "New York, NY",
      description: "Analyze large datasets and build predictive models.",
      requirements: "5+ years of experience with Python and machine learning",
      salary: "$130,000 - $160,000",
      posting_date: "2023-10-25T09:00:00Z",
      url: "https://example.com/job/2",
      source: "Indeed",
      date_discovered: "2023-10-25T09:00:00Z",
      is_applied: true,
      application_status: "Applied",
    },
    {
      id: "3",
      title: "UX Designer",
      company: "Creative Agency LLC",
      location: "Remote",
      description: "Design user-friendly interfaces for web and mobile.",
      requirements: "Portfolio demonstrating strong UX design skills",
      salary: "$100,000 - $120,000",
      posting_date: "2023-10-24T11:30:00Z",
      url: "https://example.com/job/3",
      source: "Glassdoor",
      date_discovered: "2023-10-24T11:30:00Z",
      is_applied: false,
      application_status: "Pending",
    },
  ];

  return NextResponse.json(dummyJobs);
}
