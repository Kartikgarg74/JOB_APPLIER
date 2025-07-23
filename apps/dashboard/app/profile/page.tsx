"use client";

import { useEffect, useState } from "react";

interface EducationEntry {
  degree: string;
  university: string;
  field_of_study: string;
  start_date: string;
  end_date: string;
  description?: string;
}

interface ExperienceEntry {
  title: string;
  company: string;
  location: string;
  start_date: string;
  end_date: string;
  description: string[];
}

interface ProjectEntry {
  name: string;
  description: string;
  technologies: string[];
  url?: string;
}

interface UserProfile {
  name: string;
  email: string;
  phone: string;
  address?: string;
  portfolio_url?: string;
  personal_website?: string;
  linkedin?: string;
  github?: string;
  skills: string[];
  years_of_experience: number;
  education: EducationEntry[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  job_preferences: {
    remote: boolean;
    company_size: string;
    industry: string;
    job_titles: string[];
    locations: string[];
  };
}

interface UserResume {
  name: string;
  contact: {
    email: string;
    phone: string;
    linkedin?: string;
    github?: string;
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

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [resume, setResume] = useState<UserResume | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // State for form inputs
  const [editMode, setEditMode] = useState(false);
  const [editedProfile, setEditedProfile] = useState<UserProfile | null>(null);
  const [editedResume, setEditedResume] = useState<UserResume | null>(null);
  const [resumeUploadProgress, setResumeUploadProgress] = useState(0);
  const [resumeUploadStatus, setResumeUploadStatus] = useState<string | null>(null);

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setResumeUploadStatus('Uploading...');
    setResumeUploadProgress(0);

    const formData = new FormData();
    formData.append('resume', file);

    try {
      // Simulate upload progress
      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setResumeUploadProgress(progress);
        if (progress >= 100) {
          clearInterval(interval);
        }
      }, 100);

      const response = await fetch('/api/resume/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      setResumeUploadStatus('Upload successful!');
      setMessage('Resume uploaded successfully!');
      // Optionally, update profile/resume state with new resume info
    } catch (err) {
      if (err instanceof Error) {
        setResumeUploadStatus(`Upload failed: ${err.message}`);
        setError(err.message);
      } else {
        setResumeUploadStatus('Upload failed: An unknown error occurred');
        setError('An unknown error occurred');
      }
    } finally {
      setResumeUploadProgress(100);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      const [profileRes, resumeRes] = await Promise.all([
        fetch("/api/profile"),
        fetch("/api/resume"),
      ]);

      if (!profileRes.ok) {
        throw new Error(
          `Failed to fetch profile data: ${profileRes.statusText}`,
        );
      }
      const profileData: UserProfile = await profileRes.json();
      setProfile(profileData);
      setEditedProfile(profileData); // Initialize edited data

      if (!resumeRes.ok) {
        throw new Error(`Failed to fetch resume data: ${resumeRes.statusText}`);
      }
      const resumeData: UserResume = await resumeRes.json();
      setResume(resumeData);
      setEditedResume(resumeData); // Initialize edited data
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

  const handleProfileChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      if (name.startsWith("job_preferences.")) {
        const [_, prefKey] = name.split(".");
        setEditedProfile({
          ...editedProfile,
          job_preferences: {
            ...editedProfile.job_preferences,
            [prefKey]: value,
          },
        });
      } else if (name === "skills" || name === "job_preferences.job_titles" || name === "job_preferences.locations") {
        setEditedProfile({
          ...editedProfile,
          [name]: value.split(",").map((s) => s.trim()),
        });
      } else {
        setEditedProfile({
          ...editedProfile,
          [name]: value,
        });
      }
    }
  };

  const handleEducationChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      const updatedEducation = [...editedProfile.education];
      updatedEducation[index] = { ...updatedEducation[index], [name]: value };
      setEditedProfile({ ...editedProfile, education: updatedEducation });
    }
  };

  const handleExperienceChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      const updatedExperience = [...editedProfile.experience];
      updatedExperience[index] = { ...updatedExperience[index], [name]: value };
      setEditedProfile({ ...editedProfile, experience: updatedExperience });
    }
  };

  const handleProjectChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      const updatedProjects = [...editedProfile.projects];
      updatedProjects[index] = { ...updatedProjects[index], [name]: value };
      setEditedProfile({ ...editedProfile, projects: updatedProjects });
    }
  };

  const handleAddEducation = () => {
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        education: [
          ...editedProfile.education,
          {
            degree: "",
            university: "",
            field_of_study: "",
            start_date: "",
            end_date: "",
            description: "",
          },
        ],
      });
    }
  };

  const handleDeleteEducation = (index: number) => {
    if (editedProfile) {
      const updatedEducation = editedProfile.education.filter(
        (_, i) => i !== index,
      );
      setEditedProfile({ ...editedProfile, education: updatedEducation });
    }
  };

  const handleAddProject = () => {
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        projects: [
          ...editedProfile.projects,
          {
            name: "",
            description: "",
            technologies: [],
            url: "",
          },
        ],
      });
    }
  };

  const handleDeleteProject = (index: number) => {
    if (editedProfile) {
      const updatedProjects = editedProfile.projects.filter(
        (_, i) => i !== index,
      );
      setEditedProfile({ ...editedProfile, projects: updatedProjects });
    }
  };

  const handleAddExperience = () => {
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        experience: [
          ...editedProfile.experience,
          {
            title: "",
            company: "",
            location: "",
            start_date: "",
            end_date: "",
            description: [],
          },
        ],
      });
    }
  };

  const handleDeleteExperience = (index: number) => {
    if (editedProfile) {
      const updatedExperience = editedProfile.experience.filter(
        (_, i) => i !== index,
      );
      setEditedProfile({ ...editedProfile, experience: updatedExperience });
    }
  };

  const handleSkillChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        skills: e.target.value.split(",").map((s) => s.trim()),
      });
    }
  };

  const handleJobPreferenceChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        job_preferences: {
          ...editedProfile.job_preferences,
          [name]:
            e.target instanceof HTMLInputElement && e.target.type === "checkbox"
              ? e.target.checked
              : value,
        },
      });
    }
  };

  const handleJobPreferenceArrayChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        job_preferences: {
          ...editedProfile.job_preferences,
          [name]: value.split(",").map((s) => s.trim()),
        },
      });
    }
  };

  const handleResumeChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    if (editedResume) {
      if (name.startsWith("contact.")) {
        const contactKey = name.split(".")[1];
        setEditedResume({
          ...editedResume,
          contact: {
            ...editedResume.contact,
            [contactKey]: value,
          },
        });
      } else if (name === "skills") {
        setEditedResume({
          ...editedResume,
          [name]: value.split(",").map((s) => s.trim()),
        });
      } else if (name === "summary") {
        setEditedResume({
          ...editedResume,
          [name]: value,
        });
      }
      // Handle experience and education arrays more complexly if needed
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!editedProfile) return true;

    if (!editedProfile.name.trim()) {
      errors.name = "Name is required.";
    }
    if (!editedProfile.email.trim()) {
      errors.email = "Email is required.";
    } else if (!/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(editedProfile.email)) {
      errors.email = "Invalid email format.";
    }
    if (!editedProfile.phone.trim()) {
      errors.phone = "Phone number is required.";
    }

    if (editedProfile.portfolio_url && !/^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$/.test(editedProfile.portfolio_url)) {
      errors.portfolio_url = "Invalid portfolio URL format.";
    }
    if (editedProfile.personal_website && !/^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$/.test(editedProfile.personal_website)) {
      errors.personal_website = "Invalid personal website URL format.";
    }
    if (editedProfile.linkedin && !/^https?:\/\/(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+\/?$/.test(editedProfile.linkedin)) {
      errors.linkedin = "Invalid LinkedIn URL format.";
    }
    if (editedProfile.github && !/^https?:\/\/(?:www\.)?github\.com\/[a-zA-Z0-9_-]+\/?$/.test(editedProfile.github)) {
      errors.github = "Invalid GitHub URL format.";
    }

    editedProfile.experience.forEach((exp, index) => {
      if (!exp.title.trim()) {
        errors[`experience[${index}].title`] = "Job Title is required.";
      }
      if (!exp.company.trim()) {
        errors[`experience[${index}].company`] = "Company is required.";
      }
      if (!exp.location.trim()) {
        errors[`experience[${index}].location`] = "Location is required.";
      }
      if (!exp.start_date.trim()) {
        errors[`experience[${index}].start_date`] = "Start Date is required.";
      }
      if (!exp.end_date.trim()) {
        errors[`experience[${index}].end_date`] = "End Date is required.";
      } else if (exp.start_date && exp.end_date && new Date(exp.start_date) > new Date(exp.end_date)) {
        errors[`experience[${index}].end_date`] = "End Date cannot be before Start Date.";
      }
      if (exp.description.length === 0 || exp.description[0].trim() === '') {
        errors[`experience[${index}].description`] = "Responsibilities are required.";
      }
    });

    editedProfile.education.forEach((edu, index) => {
      if (!edu.degree.trim()) {
        errors[`education[${index}].degree`] = "Degree is required.";
      }
      if (!edu.university.trim()) {
        errors[`education[${index}].university`] = "University is required.";
      }
      if (!edu.field_of_study.trim()) {
        errors[`education[${index}].field_of_study`] = "Field of Study is required.";
      }
      if (!edu.start_date.trim()) {
        errors[`education[${index}].start_date`] = "Start Date is required.";
      }
      if (!edu.end_date.trim()) {
        errors[`education[${index}].end_date`] = "End Date is required.";
      } else if (edu.start_date && edu.end_date && new Date(edu.start_date) > new Date(edu.end_date)) {
        errors[`education[${index}].end_date`] = "End Date cannot be before Start Date.";
      }
      if (edu.description.length === 0 || edu.description[0].trim() === '') {
        errors[`education[${index}].description`] = "Description is required.";
      }
    });

    editedProfile.projects.forEach((proj, index) => {
      if (!proj.name.trim()) {
        errors[`projects[${index}].name`] = "Project Name is required.";
      }
      if (!proj.description.trim()) {
        errors[`projects[${index}].description`] = "Project Description is required.";
      }
      if (proj.technologies.length === 0) {
        errors[`projects[${index}].technologies`] = "Technologies used are required.";
      }
      if (proj.url && !/^https?:\/\/(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z0-9.]+(?:\/[^\s]*)?$/.test(proj.url)) {
      errors[`projects[${index}].url`] = "Invalid Project URL format.";
    }
  });

  if (editedProfile.skills.length === 0) {
    errors.skills = "At least one skill is required.";
  }

  if (
    !editedProfile.job_preferences.company_size &&
    !editedProfile.job_preferences.industry &&
    editedProfile.job_preferences.job_titles.length === 0 &&
    editedProfile.job_preferences.locations.length === 0 &&
    !editedProfile.job_preferences.remote
  ) {
    errors.job_preferences = "At least one job preference field is required.";
  }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      setMessage("Please correct the errors in the form.");
      return;
    }
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      if (editedProfile) {
        const profileRes = await fetch("/api/profile/update", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(editedProfile),
        });
        if (!profileRes.ok) {
          throw new Error(`Failed to update profile: ${profileRes.statusText}`);
        }
      }

      if (editedResume) {
        const resumeRes = await fetch("/api/resume/update", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(editedResume),
        });
        if (!resumeRes.ok) {
          throw new Error(`Failed to update resume: ${resumeRes.statusText}`);
        }
      }

      setMessage("Profile and Resume updated successfully!");
      setEditMode(false);
      fetchData(); // Re-fetch data to ensure UI is in sync
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred during update");
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading profile and resume data...</p>
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
      <h1 className="text-4xl font-bold mb-8">Your Profile & Resume</h1>

      {message && (
        <div
          className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4"
          role="alert"
        >
          {message}
        </div>
      )}

      <button
        onClick={() => setEditMode(!editMode)}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
        {editMode ? "Cancel Edit" : "Edit Profile & Resume"}
      </button>

      {editMode && (
        <button
          onClick={handleSave}
          className="mb-4 ml-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
        >
          Save Changes
        </button>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Profile Display/Edit */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">
            Personal Information & Preferences
          </h2>
          {profile && editedProfile ? (
            <form>
              <div className="mb-4">
                <label
                  htmlFor="name"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Name:
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={editedProfile.name}
                  onChange={handleProfileChange}
                />
                {validationErrors.email && (
                  <p className="text-red-500 text-xs italic">{validationErrors.email}</p>
                )}
                {validationErrors.name && (
                  <p className="text-red-500 text-xs italic">{validationErrors.name}</p>
                )}
              </div>
              <div className="mb-4">
                <label
                  htmlFor="email"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Email:
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={editedProfile.email}
                  onChange={handleProfileChange}
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="phone"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Phone:
                </label>
                <input
                  type="text"
                  id="phone"
                  name="phone"
                  value={editedProfile.phone}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
                {validationErrors.github && (
                  <p className="text-red-500 text-xs italic">{validationErrors.github}</p>
                )}
                {validationErrors.linkedin && (
                  <p className="text-red-500 text-xs italic">{validationErrors.linkedin}</p>
                )}
                {validationErrors.personal_website && (
                  <p className="text-red-500 text-xs italic">{validationErrors.personal_website}</p>
                )}
                {validationErrors.portfolio_url && (
                  <p className="text-red-500 text-xs italic">{validationErrors.portfolio_url}</p>
                )}
                {validationErrors.phone && (
                  <p className="text-red-500 text-xs italic">{validationErrors.phone}</p>
                )}
              </div>
              <div className="mb-4">
                <label
                  htmlFor="address"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Address:
                </label>
                <input
                  type="text"
                  id="address"
                  name="address"
                  value={editedProfile.address || ''}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="portfolio_url"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Portfolio URL:
                </label>
                <input
                  type="url"
                  id="portfolio_url"
                  name="portfolio_url"
                  value={editedProfile.portfolio_url || ''}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="personal_website"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Personal Website:
                </label>
                <input
                  type="url"
                  id="personal_website"
                  name="personal_website"
                  value={editedProfile.personal_website || ''}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="linkedin"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  LinkedIn Profile:
                </label>
                <input
                  type="text"
                  id="linkedin"
                  name="linkedin"
                  value={editedProfile.linkedin || ''}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="github"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  GitHub:
                </label>
                <input
                  type="text"
                  id="github"
                  name="github"
                  value={editedProfile.github || ""}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>

            <h3 className="text-lg font-semibold mb-2">Experience</h3>
            {editedProfile.experience.map((exp, index) => (
              <div key={index} className="border p-4 rounded-md mb-4">
                <div className="mb-4">
                  <label
                    htmlFor={`job-title-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Job Title:
                  </label>
                  <input
                    type="text"
                    id={`job-title-${index}`}
                    name="title"
                    value={exp.title}
                    onChange={(e) => handleExperienceChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                  {validationErrors[`projects[${index}].url`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`projects[${index}].url`]}</p>
                  )}
                  {validationErrors[`projects[${index}].technologies`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`projects[${index}].technologies`]}</p>
                  )}
                  {validationErrors[`projects[${index}].description`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`projects[${index}].description`]}</p>
                  )}
                  {validationErrors[`projects[${index}].name`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`projects[${index}].name`]}</p>
                  )}
                  {validationErrors[`education[${index}].description`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`education[${index}].description`]}</p>
                  )}
                  {validationErrors[`education[${index}].end_date`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`education[${index}].end_date`]}</p>
                  )}
                  {validationErrors[`education[${index}].start_date`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`education[${index}].start_date`]}</p>
                  )}
                  {validationErrors[`education[${index}].field_of_study`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`education[${index}].field_of_study`]}</p>
                  )}
                  {validationErrors[`education[${index}].university`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`education[${index}].university`]}</p>
                  )}
                  {validationErrors[`education[${index}].degree`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`education[${index}].degree`]}</p>
                  )}
                  {validationErrors[`experience[${index}].description`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`experience[${index}].description`]}</p>
                  )}
                  {validationErrors[`experience[${index}].end_date`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`experience[${index}].end_date`]}</p>
                  )}
                  {validationErrors[`experience[${index}].start_date`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`experience[${index}].start_date`]}</p>
                  )}
                  {validationErrors[`experience[${index}].location`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`experience[${index}].location`]}</p>
                  )}
                  {validationErrors[`experience[${index}].company`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`experience[${index}].company`]}</p>
                  )}
                  {validationErrors[`experience[${index}].title`] && (
                    <p className="text-red-500 text-xs italic">{validationErrors[`experience[${index}].title`]}</p>
                  )}
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`company-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Company:
                  </label>
                  <input
                    type="text"
                    id={`company-${index}`}
                    name="company"
                    value={exp.company}
                    onChange={(e) => handleExperienceChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`location-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Location:
                  </label>
                  <input
                    type="text"
                    id={`location-${index}`}
                    name="location"
                    value={exp.location}
                    onChange={(e) => handleExperienceChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`experience-start-date-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Start Date:
                  </label>
                  <input
                    type="date"
                    id={`experience-start-date-${index}`}
                    name="start_date"
                    value={exp.start_date}
                    onChange={(e) => handleExperienceChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`experience-end-date-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    End Date:
                  </label>
                  <input
                    type="date"
                    id={`experience-end-date-${index}`}
                    name="end_date"
                    value={exp.end_date}
                    onChange={(e) => handleExperienceChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`responsibilities-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Responsibilities (comma-separated):
                  </label>
                  <textarea
                    id={`responsibilities-${index}`}
                    name="description"
                    value={exp.description}
                    onChange={(e) =>
                      handleExperienceChange(index, {
                        ...e,
                        target: {
                          ...e.target,
                          value: e.target.value
                            .split(",")
                            .map((s) => s.trim()),
                          name: "description",
                        },
                      })
                    }
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                {editMode && (
                  <button
                    type="button"
                    onClick={() => handleDeleteExperience(index)}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    Delete Experience
                  </button>
                )}
              </div>
            ))}
            {editMode && (
              <button
                type="button"
                onClick={handleAddProject}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mb-4"
              >
                Add Project
              </button>
            )}

            <h3 className="text-lg font-semibold mb-2">Skills</h3>
            <div className="mb-4">
              <label
                htmlFor="skills"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Skills (comma-separated):
              </label>
              {validationErrors.skills && (
                <p className="text-red-500 text-xs italic">{validationErrors.skills}</p>
              )}
              <input
                type="text"
                id="skills"
                name="skills"
                value={editedProfile.skills.join(", ")}
                onChange={handleSkillChange}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
              <p className="text-gray-600 text-xs italic mt-1">
                Enter skills separated by commas (e.g., React, Node.js, Python)
              </p>
            </div>

            <h3 className="text-lg font-semibold mb-2">Job Preferences</h3>
            {validationErrors.job_preferences && (
              <p className="text-red-500 text-xs italic">{validationErrors.job_preferences}</p>
            )}
            <div className="mb-4">
              <label
                htmlFor="job_preferences.company_size"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Preferred Company Size:
              </label>
              <select
                id="job_preferences.company_size"
                name="company_size"
                value={editedProfile.job_preferences.company_size}
                onChange={handleJobPreferenceChange}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              >
                <option value="">Select...</option>
                <option value="small">Small (1-50 employees)</option>
                <option value="medium">Medium (51-500 employees)</option>
                <option value="large">Large (501+ employees)</option>
              </select>
            </div>
            <div className="mb-4">
              <label
                htmlFor="job_preferences.industry"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Preferred Industry:
              </label>
              <input
                type="text"
                id="job_preferences.industry"
                name="industry"
                value={editedProfile.job_preferences.industry}
                onChange={handleJobPreferenceChange}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="mb-4">
              <label
                htmlFor="job_preferences.job_titles"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Desired Job Titles (comma-separated):
              </label>
              <input
                type="text"
                id="job_preferences.job_titles"
                name="job_titles"
                value={editedProfile.job_preferences.job_titles.join(", ")}
                onChange={handleJobPreferenceArrayChange}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="mb-4">
              <label
                htmlFor="job_preferences.locations"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Preferred Locations (comma-separated):
              </label>
              <input
                type="text"
                id="job_preferences.locations"
                name="locations"
                value={editedProfile.job_preferences.locations.join(", ")}
                onChange={handleJobPreferenceArrayChange}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="mb-4">
              <label
                htmlFor="job_preferences.remote"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Remote Work Preferred:
              </label>
              <input
                type="checkbox"
                id="job_preferences.remote"
                name="remote"
                checked={editedProfile.job_preferences.remote}
                onChange={handleJobPreferenceChange}
                disabled={!editMode}
                className="mr-2 leading-tight"
              />
            </div>

            <h3 className="text-lg font-semibold mb-2">Resume Upload</h3>
            <div className="mb-4">
              <label htmlFor="resume-upload" className="block text-gray-700 text-sm font-bold mb-2">
                Upload Resume (PDF, DOCX):
              </label>
              <input
                type="file"
                id="resume-upload"
                name="resume"
                accept=".pdf,.docx"
                onChange={handleResumeUpload}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
              {resumeUploadProgress > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mt-2">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{ width: `${resumeUploadProgress}%` }}
                  ></div>
                </div>
              )}
              {resumeUploadStatus && (
                <p className="text-sm text-gray-500 mt-1">{resumeUploadStatus}</p>
              )}
            </div>

            <h3 className="text-lg font-semibold mb-2 mt-6">ATS Score</h3>
            <div className="mb-4 p-4 border rounded-md">
              <p className="text-gray-700">Your resume's ATS compatibility score: <span className="font-bold text-blue-600">85%</span></p>
              <p className="text-sm text-gray-500 mt-1">Areas for improvement: Keywords, Formatting (placeholder)</p>
            </div>

            <h3 className="text-lg font-semibold mb-2 mt-6">Job Suitability</h3>
            <div className="mb-4 p-4 border rounded-md">
              <p className="text-gray-700">Suitability for 'Software Engineer' role: <span className="font-bold text-green-600">92%</span></p>
              <p className="text-sm text-gray-500 mt-1">Matching keywords/skills: React, Node.js, JavaScript, AWS (placeholder)</p>
            </div>

            <h3 className="text-lg font-semibold mb-2">Projects</h3>
            {editedProfile.projects.map((project, index) => (
              <div key={index} className="border p-4 rounded-md mb-4">
                <div className="mb-4">
                  <label
                    htmlFor={`project-name-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Project Name:
                  </label>
                  <input
                    type="text"
                    id={`project-name-${index}`}
                    name="name"
                    value={project.name}
                    onChange={(e) => handleProjectChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`project-description-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Description:
                  </label>
                  <textarea
                    id={`project-description-${index}`}
                    name="description"
                    value={project.description}
                    onChange={(e) => handleProjectChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`project-technologies-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Technologies (comma-separated):
                  </label>
                  <input
                    type="text"
                    id={`project-technologies-${index}`}
                    name="technologies"
                    value={project.technologies}
                    onChange={(e) =>
                      handleProjectChange(index, {
                        ...e,
                        target: {
                          ...e.target,
                          value: e.target.value
                            .split(",")
                            .map((s) => s.trim()),
                          name: "technologies"
                        }
                      })
                    }
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`project-url-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    URL:
                  </label>
                  <input
                    type="url"
                    id={`project-url-${index}`}
                    name="url"
                    value={project.url || ""}
                    onChange={(e) => handleProjectChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                {editMode && (
                  <button
                    type="button"
                    onClick={() => handleDeleteProject(index)}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    Delete Project
                  </button>
                )}
              </div>
            ))}
            {editMode && (
              <button
                type="button"
                onClick={handleAddProject}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mb-4"
              >
                Add Project
              </button>
            )}
            <div className="mb-4">
                <label
                  htmlFor="github"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  GitHub Profile:
                </label>
                <input
                  type="text"
                  id="github"
                  name="github"
                  value={editedProfile.github || ''}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
              <label
                htmlFor="years_of_experience"
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Years of Experience:
              </label>
              <input
                type="number"
                id="years_of_experience"
                name="years_of_experience"
                value={editedProfile.years_of_experience}
                onChange={handleProfileChange}
                disabled={!editMode}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>

              <h3 className="text-xl font-semibold mt-6 mb-4">
                ATS Improvement Suggestions
              </h3>
              <div className="bg-gray-100 p-4 rounded-md mb-4">
                <p className="text-gray-700">
                  <strong>Resume Scan Result:</strong> Your resume is 70% optimized for ATS.
                </p>
                <p className="text-gray-700">
                  <strong>Actionable Suggestions:</strong>
                </p>
                <ul className="list-disc list-inside text-gray-700">
                  <li>Use more keywords from job descriptions in your experience section.</li>
                  <li>Quantify achievements with numbers and metrics.</li>
                  <li>Ensure consistent formatting throughout the document.</li>
                  <li>Avoid using tables or complex graphics as they can be hard for ATS to parse.</li>
                </ul>
              </div>

            <h3 className="text-lg font-semibold mb-2">Education</h3>
            {editedProfile.education.map((edu, index) => (
              <div key={index} className="border p-4 rounded-md mb-4">
                <div className="mb-4">
                  <label
                    htmlFor={`degree-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Degree:
                  </label>
                  <input
                    type="text"
                    id={`degree-${index}`}
                    name="degree"
                    value={edu.degree}
                    onChange={(e) => handleEducationChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`university-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    University:
                  </label>
                  <input
                    type="text"
                    id={`university-${index}`}
                    name="university"
                    value={edu.university}
                    onChange={(e) => handleEducationChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`field_of_study-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Field of Study:
                  </label>
                  <input
                    type="text"
                    id={`field_of_study-${index}`}
                    name="field_of_study"
                    value={edu.field_of_study}
                    onChange={(e) => handleEducationChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`start_date-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Start Date:
                  </label>
                  <input
                    type="date"
                    id={`start_date-${index}`}
                    name="start_date"
                    value={edu.start_date}
                    onChange={(e) => handleEducationChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`end_date-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    End Date:
                  </label>
                  <input
                    type="date"
                    id={`end_date-${index}`}
                    name="end_date"
                    value={edu.end_date}
                    onChange={(e) => handleEducationChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <div className="mb-4">
                  <label
                    htmlFor={`description-${index}`}
                    className="block text-gray-700 text-sm font-bold mb-2"
                  >
                    Description:
                  </label>
                  <textarea
                    id={`description-${index}`}
                    name="description"
                    value={edu.description || ""}
                    onChange={(e) => handleEducationChange(index, e)}
                    disabled={!editMode}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                {editMode && (
                  <button
                    type="button"
                    onClick={() => handleDeleteEducation(index)}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    Delete Education
                  </button>
                )}
              </div>
            ))}
            {editMode && (
              <button
                type="button"
                onClick={handleAddEducation}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mb-4"
              >
                Add Education
              </button>
            )}
              <div className="mb-4">
                <label
                  htmlFor="skills"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Skills (comma-separated):
                </label>
                <textarea
                  id="skills"
                  name="skills"
                  value={editedProfile.skills.join(", ")}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                ></textarea>
              </div>
              <div className="mb-4">
                <label
                  htmlFor="education"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Education (comma-separated):
                </label>
                <textarea
                  id="education"
                  name="education"
                  value={editedProfile.education.join(", ")}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                ></textarea>
              </div>

              <h3 className="text-xl font-semibold mt-6 mb-4">
                Job Preferences
              </h3>
              <div className="mb-4">
                <label
                  htmlFor="job_preferences.remote"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Remote:
                </label>
                <input
                  type="checkbox"
                  id="job_preferences.remote"
                  name="job_preferences.remote"
                  checked={editedProfile.job_preferences.remote}
                  onChange={(e) =>
                    handleProfileChange({
                      ...e,
                      target: {
                        ...e.target,
                        value: e.target.checked.toString(),
                      },
                    })
                  }
                  disabled={!editMode}
                  className="mr-2 leading-tight"
                />
                <span>
                  {editedProfile.job_preferences.remote ? "Yes" : "No"}
                </span>
              </div>
              <div className="mb-4">
                <label
                  htmlFor="job_preferences.company_size"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Company Size:
                </label>
                <input
                  type="text"
                  id="job_preferences.company_size"
                  name="job_preferences.company_size"
                  value={editedProfile.job_preferences.company_size}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="job_preferences.industry"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Industry:
                </label>
                <input
                  type="text"
                  id="job_preferences.industry"
                  name="job_preferences.industry"
                  value={editedProfile.job_preferences.industry}
                  onChange={handleProfileChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
            </form>
          ) : (
            <p>No profile data available.</p>
          )}
        </div>

        {/* Resume Display/Edit */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Your Resume</h2>
          {resume && editedResume ? (
            <form>
              <div className="mb-4">
                <label
                  htmlFor="resumeName"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Name:
                </label>
                <input
                  type="text"
                  id="resumeName"
                  name="name"
                  value={editedResume.name}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="contactEmail"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Email:
                </label>
                <input
                  type="email"
                  id="contactEmail"
                  name="contact.email"
                  value={editedResume.contact.email}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="contactPhone"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Phone:
                </label>
                <input
                  type="text"
                  id="contactPhone"
                  name="contact.phone"
                  value={editedResume.contact.phone}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="contactLinkedin"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  LinkedIn:
                </label>
                <input
                  type="text"
                  id="contactLinkedin"
                  name="contact.linkedin"
                  value={editedResume.contact.linkedin}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="contactGithub"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  GitHub:
                </label>
                <input
                  type="text"
                  id="contactGithub"
                  name="contact.github"
                  value={editedResume.contact.github}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="resumeSkills"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Skills (comma-separated):
                </label>
                <textarea
                  id="resumeSkills"
                  name="skills"
                  value={editedResume.skills.join(", ")}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                ></textarea>
              </div>
              <div className="mb-4">
                <label
                  htmlFor="resumeSummary"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Summary:
                </label>
                <textarea
                  id="resumeSummary"
                  name="summary"
                  value={editedResume.summary}
                  onChange={handleResumeChange}
                  disabled={!editMode}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                ></textarea>
              </div>
              {/* Note: Experience and Education editing would require more complex dynamic forms */}
            </form>
          ) : (
            <p>No resume data available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
