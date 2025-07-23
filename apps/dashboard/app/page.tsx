"use client";

import { useEffect, useState } from "react";
import ResumeUploadForm from "../components/ResumeUploadForm";

interface UserResume {
  name: string;
  contact: {
    email: string;
    phone: string;
    linkedin: string;
    github: string;
  };
  skills: string[];
  experience: {
    title: string;
    company: string;
    duration: string;
    description: string[];
  }[];
  education: {
    degree: string;
    university: string;
    year: string;
  }[];
  summary: string;
}

interface UserProfile {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  years_of_experience: number;
  education: string[];
  job_preferences: {
    remote: boolean;
    company_size: string;
    industry: string;
  };
}

interface AtsData {
  score: number;
  feedback: string[];
  job_id: string;
}

export default function Home() {
  const [resume, setResume] = useState<UserResume | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [atsData, setAtsData] = useState<AtsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [resumeRes, profileRes, atsRes] = await Promise.all([
          fetch("/api/resume"),
          fetch("/api/profile"),
          fetch("/api/ats"),
        ]);

        if (!resumeRes.ok) {
          throw new Error(`Failed to fetch resume: ${resumeRes.statusText}`);
        }
        const resumeData: UserResume = await resumeRes.json();
        setResume(resumeData);

        if (!profileRes.ok) {
          throw new Error(`Failed to fetch profile: ${profileRes.statusText}`);
        }
        const profileData: UserProfile = await profileRes.json();
        setProfile(profileData);

        if (!atsRes.ok) {
          throw new Error(`Failed to fetch ATS data: ${atsRes.statusText}`);
        }
        const atsJson: AtsData = await atsRes.json();
        setAtsData(atsJson);
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

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading data...</p>
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
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
      <ResumeUploadForm />


      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Resume Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Your Resume</h2>
          {resume ? (
            <div>
              <p className="text-lg mb-2">
                <strong>Name:</strong> {resume.name}
              </p>
              <p className="text-lg mb-2">
                <strong>Email:</strong> {resume.contact.email}
              </p>
              <p className="text-lg mb-2">
                <strong>LinkedIn:</strong>{" "}
                <a
                  href={resume.contact.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  {resume.contact.linkedin}
                </a>
              </p>
              <p className="text-lg mb-2">
                <strong>GitHub:</strong>{" "}
                <a
                  href={resume.contact.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  {resume.contact.github}
                </a>
              </p>
              <p className="text-lg mb-2">
                <strong>Summary:</strong> {resume.summary}
              </p>
              <div className="mb-2">
                <strong className="text-lg">Skills:</strong>
                <ul className="list-disc list-inside ml-4">
                  {resume.skills.map((skill, index) => (
                    <li key={index}>{skill}</li>
                  ))}
                </ul>
              </div>
              <div className="mb-2">
                <strong className="text-lg">Experience:</strong>
                {resume.experience.map((exp, index) => (
                  <div key={index} className="mb-2 ml-4">
                    <p className="font-medium">
                      {exp.title} at {exp.company} ({exp.duration})
                    </p>
                    <ul className="list-disc list-inside ml-4">
                      {exp.description.map((desc, i) => (
                        <li key={i}>{desc}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
              <div className="mb-2">
                <strong className="text-lg">Education:</strong>
                <ul className="list-disc list-inside ml-4">
                  {resume.education.map((edu, index) => (
                    <li key={index}>
                      {edu.degree} from {edu.university} ({edu.year})
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p>No resume data available.</p>
          )}
        </div>

        {/* ATS Score & Feedback Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">ATS Score & Feedback</h2>
          {atsData ? (
            <div>
              <p className="text-lg mb-2">
                <strong>Score:</strong>{" "}
                <span className="text-blue-600 font-bold text-xl">
                  {atsData.score}%
                </span>
              </p>
              <h3 className="text-xl font-semibold mb-2">Feedback:</h3>
              <ul className="list-disc list-inside ml-4">
                {atsData.feedback.map((item, index) => (
                  <li key={index} className="mb-1">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p>
              No ATS data available. Please upload a resume and select a job to
              get feedback.
            </p>
          )}
        </div>

        {/* User Profile Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Your Profile</h2>
          {profile ? (
            <div>
              <p className="text-lg mb-2">
                <strong>Name:</strong> {profile.name}
              </p>
              <p className="text-lg mb-2">
                <strong>Email:</strong> {profile.email}
              </p>
              <p className="text-lg mb-2">
                <strong>Phone:</strong> {profile.phone}
              </p>
              <p className="text-lg mb-2">
                <strong>Years of Experience:</strong>{" "}
                {profile.years_of_experience}
              </p>
              <div className="mb-2">
                <strong className="text-lg">Skills:</strong>
                <ul className="list-disc list-inside ml-4">
                  {profile.skills.map((skill, index) => (
                    <li key={index}>{skill}</li>
                  ))}
                </ul>
              </div>
              <div className="mb-2">
                <strong className="text-lg">Education:</strong>
                <ul className="list-disc list-inside ml-4">
                  {profile.education.map((edu, index) => (
                    <li key={index}>{edu}</li>
                  ))}
                </ul>
              </div>
              <h3 className="text-xl font-semibold mb-2">Job Preferences:</h3>
              <p className="mb-1">
                <strong>Remote:</strong>{" "}
                {profile.job_preferences.remote ? "Yes" : "No"}
              </p>
              <p className="mb-1">
                <strong>Company Size:</strong>{" "}
                {profile.job_preferences.company_size}
              </p>
              <p className="mb-1">
                <strong>Industry:</strong> {profile.job_preferences.industry}
              </p>
            </div>
          ) : (
            <p>No profile data available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
