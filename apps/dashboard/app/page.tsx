"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "../../../frontend/components/ui/dialog";
import { Progress } from "../../../frontend/components/ui/progress";
import type { Step } from "react-joyride";

const ResumeUploadForm = dynamic(() => import("../components/ResumeUploadForm"), { ssr: false, loading: () => <div>Loading Resume Upload...</div> });
const Joyride = dynamic(() => import("react-joyride"), { ssr: false });

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

interface JobPreferences {
  job_type?: string;
  location?: string;
  notifications?: boolean;
  remote?: boolean;
  company_size?: string;
  industry?: string;
  job_titles?: string;
  locations?: string;
}

interface UserProfile {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  years_of_experience: number;
  education: string[];
  job_preferences: JobPreferences;
  onboarding_complete?: boolean;
  onboarding_step?: string;
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
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [tourRun, setTourRun] = useState(false);
  const tourSteps: Step[] = [
    {
      target: "#kanban-board-link",
      content: "Track your job applications visually with the Kanban Board.",
    },
    {
      target: "#file-manager-link",
      content: "Manage your resumes and documents in the File Manager.",
    },
    {
      target: "#resume-upload-form",
      content: "Upload your resume here to get started.",
    },
    {
      target: "#profile-section",
      content: "View and edit your profile and job preferences here.",
    },
  ];

  const [setupName, setSetupName] = useState("");
  const [setupPhone, setSetupPhone] = useState("");
  const [setupError, setSetupError] = useState("");
  const [resumeUploaded, setResumeUploaded] = useState(false);
  const [setupJobType, setSetupJobType] = useState("");
  const [setupLocation, setSetupLocation] = useState("");
  const [setupNotifications, setSetupNotifications] = useState(true);
  const [scanResults, setScanResults] = useState<null | { atsScore: number; jobMatches: any[] }>(null);
  const [showScanModal, setShowScanModal] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackValue, setFeedbackValue] = useState<null | 'up' | 'down'>(null);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showInitialScanResult, setShowInitialScanResult] = useState(false);
  const [initialScanResult, setInitialScanResult] = useState(null);

  // Progress calculation for onboarding
  const totalSteps = 3;
  let completedSteps = 0;
  if (setupName && setupPhone) completedSteps++;
  if (resumeUploaded) completedSteps++;
  if (setupJobType && setupLocation) completedSteps++;
  const progressPercent = Math.round((completedSteps / totalSteps) * 100);

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
        if (profileData && profileData.onboarding_complete === false) {
          setShowOnboarding(true);
        }

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
    // Show tour if onboarding is complete and tour not seen
    if (typeof window !== "undefined" && localStorage.getItem("joyride_tour_seen") !== "true") {
      setShowTour(true);
      setTourRun(true);
    }
  }, []);

  useEffect(() => {
    if (profile && profile.onboarding_complete && localStorage.getItem("joyride_tour_seen") !== "true") {
      setShowTour(true);
      setTourRun(true);
    }
  }, [profile]);

  useEffect(() => {
    if (!showFeedback && feedbackSubmitted) {
      setTimeout(() => setShowSuccess(true), 1000);
    }
  }, [showFeedback, feedbackSubmitted]);

  function handleTourCallback(data: any) {
    if (data.status === "finished" || data.status === "skipped") {
      setTourRun(false);
      setShowTour(false);
      if (typeof window !== "undefined") {
        localStorage.setItem("joyride_tour_seen", "true");
      }
    }
  }

  async function completeOnboarding() {
    if (!profile) return;
    if (!setupName || !setupPhone || !resumeUploaded || !setupJobType || !setupLocation) {
      setSetupError("Please fill in all fields, upload your resume, and set preferences.");
      return;
    }
    await fetch("/api/profile", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        onboarding_complete: true,
        name: setupName,
        phone: setupPhone,
        job_preferences: {
          job_type: setupJobType,
          location: setupLocation,
          notifications: setupNotifications,
          remote: profile?.job_preferences?.remote ?? false,
          company_size: profile?.job_preferences?.company_size ?? "",
          industry: profile?.job_preferences?.industry ?? "",
          job_titles: profile?.job_preferences?.job_titles ?? "",
          locations: profile?.job_preferences?.locations ?? ""
        },
      }),
    });
    setShowOnboarding(false);
    // Trigger initial scan after onboarding
    const scanRes = await fetch("/api/initial-scan", { method: "POST" });
    if (scanRes.ok) {
      const data = await scanRes.json();
      setInitialScanResult(data);
      setShowInitialScanResult(true);
    }
    setProfile({
      ...profile,
      onboarding_complete: true,
      name: setupName,
      phone: setupPhone,
      job_preferences: {
        ...profile.job_preferences,
        job_type: setupJobType,
        location: setupLocation,
        notifications: setupNotifications,
      },
    });
    setTimeout(() => setShowFeedback(true), 1000);
  }

  async function submitFeedback() {
    await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: feedbackValue, comment: feedbackComment }),
    });
    setFeedbackSubmitted(true);
    setTimeout(() => setShowFeedback(false), 2000);
  }

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
    <>
      {showTour && (
        <Joyride
          steps={tourSteps}
          run={tourRun}
          continuous
          showSkipButton
          showProgress
          callback={handleTourCallback}
          styles={{ options: { zIndex: 10000 } }}
        />
      )}
      <Dialog open={showOnboarding} onOpenChange={setShowOnboarding}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Welcome to Job Applier!</DialogTitle>
            <DialogDescription>
              Let's get you set up. Complete the steps below to finish onboarding.
            </DialogDescription>
          </DialogHeader>
          <div className="mb-4">
            <Progress value={progressPercent} />
            <div className="text-sm text-gray-500 mt-1">{progressPercent}% complete</div>
          </div>
          {/* Help resources section */}
          <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
            <div className="font-semibold mb-1">Need help?</div>
            <ul className="list-disc ml-5 text-sm">
              <li><a href="/docs/architecture.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">System Architecture</a></li>
              <li><a href="/docs/README.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Documentation Home</a></li>
              <li>FAQ: Coming soon</li>
              <li>Contact support: <a href="mailto:support@jobapplier.com" className="text-blue-600 underline">support@jobapplier.com</a></li>
            </ul>
          </div>
          <div className="my-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                type="text"
                value={setupName}
                onChange={e => setSetupName(e.target.value)}
                className="w-full border rounded px-2 py-1"
                placeholder="Your name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Phone</label>
              <input
                type="text"
                value={setupPhone}
                onChange={e => setSetupPhone(e.target.value)}
                className="w-full border rounded px-2 py-1"
                placeholder="Your phone number"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Upload Resume</label>
              <ResumeUploadForm onUploadSuccess={() => setResumeUploaded(true)} />
              {!resumeUploaded && <p className="text-xs text-gray-500 mt-1">Please upload your resume to continue.</p>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Preferred Job Type</label>
              <input
                type="text"
                value={setupJobType}
                onChange={e => setSetupJobType(e.target.value)}
                className="w-full border rounded px-2 py-1"
                placeholder="e.g. Software Engineer, Data Analyst"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Preferred Location</label>
              <input
                type="text"
                value={setupLocation}
                onChange={e => setSetupLocation(e.target.value)}
                className="w-full border rounded px-2 py-1"
                placeholder="e.g. Remote, New York, London"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={setupNotifications}
                onChange={e => setSetupNotifications(e.target.checked)}
                id="notifications"
                className="mr-2"
              />
              <label htmlFor="notifications" className="text-sm">Receive job alerts and notifications</label>
            </div>
            {setupError && <div className="text-red-600 text-sm">{setupError}</div>}
            <DialogFooter>
              <button
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                onClick={completeOnboarding}
              >
                Complete Onboarding
              </button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
      {showInitialScanResult && initialScanResult && (
        <Dialog open={showInitialScanResult} onOpenChange={setShowInitialScanResult}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Initial Scan Results</DialogTitle>
            </DialogHeader>
            <DialogDescription>
              {initialScanResult.ats_score && (
                <div>ATS Score: {initialScanResult.ats_score}</div>
              )}
              {initialScanResult.job_matches && initialScanResult.job_matches.length > 0 && (
                <div>
                  <div>Job Matches:</div>
                  <ul>
                    {initialScanResult.job_matches.map((job: any) => (
                      <li key={job.id}>{job.title} at {job.company}</li>
                    ))}
                  </ul>
                </div>
              )}
            </DialogDescription>
            <DialogFooter>
              <DialogClose asChild>
                <button onClick={() => setShowInitialScanResult(false)}>Close</button>
              </DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      {showScanModal && scanResults && (
        <Dialog open={showScanModal} onOpenChange={setShowScanModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Initial Scan Results</DialogTitle>
              <DialogDescription>
                Your resume ATS score: <b>{scanResults.atsScore}</b>
                <br />
                Top job matches:
                <ul>
                  {scanResults.jobMatches.map((job, idx) => (
                    <li key={idx}>{job.title} at {job.company}</li>
                  ))}
                </ul>
              </DialogDescription>
              <DialogFooter>
                <DialogClose asChild>
                  <button className="btn btn-primary">Close</button>
                </DialogClose>
              </DialogFooter>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      )}
      {showFeedback && (
        <Dialog open={showFeedback} onOpenChange={setShowFeedback}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>How was your onboarding experience?</DialogTitle>
            </DialogHeader>
            <div className="flex items-center gap-4 my-4">
              <button
                className={`text-3xl ${feedbackValue === 'up' ? 'text-green-600' : 'text-gray-400'}`}
                onClick={() => setFeedbackValue('up')}
                aria-label="Thumbs up"
              >👍</button>
              <button
                className={`text-3xl ${feedbackValue === 'down' ? 'text-red-600' : 'text-gray-400'}`}
                onClick={() => setFeedbackValue('down')}
                aria-label="Thumbs down"
              >👎</button>
            </div>
            <textarea
              className="w-full border rounded p-2 mb-2"
              placeholder="Any comments? (optional)"
              value={feedbackComment}
              onChange={e => setFeedbackComment(e.target.value)}
              rows={3}
            />
            <DialogFooter>
              <button
                className="btn btn-primary"
                onClick={submitFeedback}
                disabled={!feedbackValue || feedbackSubmitted}
              >{feedbackSubmitted ? "Thank you!" : "Submit Feedback"}</button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      {showSuccess && (
        <Dialog open={showSuccess} onOpenChange={setShowSuccess}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>🎉 Onboarding Complete!</DialogTitle>
              <DialogDescription>
                Congratulations! You’ve completed onboarding. Start exploring jobs, update your profile, or check your dashboard for new opportunities.
              </DialogDescription>
            </DialogHeader>
            <div className="flex justify-center my-4">
              <span className="text-5xl">🥳</span>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <button className="btn btn-primary">Go to Dashboard</button>
              </DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      <div className="p-4">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
        <div className="flex flex-wrap gap-4 mb-8">
          <Link href="/kanban-board" id="kanban-board-link">
            <a className="bg-yellow-400 text-black px-4 py-2 rounded shadow hover:bg-yellow-500 focus:outline-none focus:ring font-semibold">Kanban Board</a>
          </Link>
          <Link href="/file-manager" id="file-manager-link">
            <a className="bg-blue-400 text-white px-4 py-2 rounded shadow hover:bg-blue-500 focus:outline-none focus:ring font-semibold">File Manager</a>
          </Link>
        </div>
        <div id="resume-upload-form">
          <ResumeUploadForm />
        </div>
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
          <div className="bg-white p-6 rounded-lg shadow-md" id="profile-section">
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
    </>
  );
}
