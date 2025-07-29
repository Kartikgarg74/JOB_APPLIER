"use client"

import React, { useState, useMemo, useCallback, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  GripVertical,
  Plus,
  Trash2,
  Download,
  Save,
  Zap,
  Eye,
  Sparkles,
  Target,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  Upload,
  FileText,
  X,
} from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useApiServices } from '@/lib/api-context';
import { UploadResult } from '@/lib/resume';
import { getWorkflowStatus, updateWorkflowStatus, WorkflowStatus } from '@/lib/workflow';
import Image from 'next/image';

// File Upload Component for Resume Editor
function FileUploadResume({ onFileSelect, onUpload }: {
  onFileSelect: (file: File | null) => void;
  onUpload: () => void;
}) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.type.includes('word') || file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
    onFileSelect(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  }, [onFileSelect]);

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? "border-purple-500 bg-purple-50 dark:bg-purple-950/20"
            : "border-muted-foreground/25 hover:border-muted-foreground/50"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-2">
              <FileText className="w-8 h-8 text-green-600" />
              <span className="font-medium">{selectedFile.name}</span>
            </div>
            <p className="text-sm text-muted-foreground">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" size="sm" onClick={handleRemoveFile}>
                <X className="w-4 h-4 mr-2" />
                Remove File
              </Button>
              <Button size="sm" onClick={onUpload}>
                <Upload className="w-4 h-4 mr-2" />
                Upload Resume
              </Button>
            </div>
          </div>
        ) : (
          <>
            <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">Drop your resume here</h3>
            <p className="text-muted-foreground mb-4">or click to browse files</p>
            <Button onClick={() => inputRef.current?.click()}>
              <FileText className="w-4 h-4 mr-2" />
              Choose File
            </Button>
            <p className="text-xs text-muted-foreground mt-4">Supports PDF, DOC, DOCX files up to 10MB</p>
          </>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".pdf,.doc,.docx"
        onChange={handleChange}
        aria-label="Upload resume file for editing"
        title="Upload resume file for editing"
      />
    </div>
  );
}

const resumeSections = [
  { id: "header", title: "Header", required: true },
  { id: "summary", title: "Professional Summary", required: true },
  { id: "experience", title: "Work Experience", required: true },
  { id: "skills", title: "Skills", required: true },
  { id: "education", title: "Education", required: true },
  { id: "projects", title: "Projects", required: false },
  { id: "certifications", title: "Certifications", required: false },
  { id: "awards", title: "Awards", required: false },
]

// ErrorBoundary component
function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [error, setError] = useState<Error | null>(null)
  return error ? (
    <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
      <AlertDescription>
        <div className="flex justify-between items-center">
          <span>{error.message || "An unexpected error occurred. Please try again."}</span>
          <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
        </div>
      </AlertDescription>
    </Alert>
  ) : (
    <ErrorBoundaryInner setError={setError}>{children}</ErrorBoundaryInner>
  )
}
class ErrorBoundaryInner extends React.Component<{ setError: (e: Error) => void; children: React.ReactNode }> {
  componentDidCatch(error: Error) {
    this.props.setError(error)
  }
  render() {
    return this.props.children
  }
}

export function ResumeEditor() {
  const [activeSection, setActiveSection] = useState("header")
  const [atsScore, setAtsScore] = useState(0)
  const [showAISuggestions, setShowAISuggestions] = useState(true)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  // Real user data state
  const [userProfile, setUserProfile] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    location: "",
    linkedin: "",
    website: "",
    summary: "",
    jobTitle: "",
    experience: [] as any[],
    skills: [] as string[],
    education: [] as string[],
    projects: [] as string[],
    certifications: [] as string[],
    awards: [] as string[]
  });

  // Add state for dynamic sections
  const [educationEntries, setEducationEntries] = useState<string[]>([]);
  const [projectsEntries, setProjectsEntries] = useState<string[]>([]);
  const [certificationsEntries, setCertificationsEntries] = useState<string[]>([]);
  const [awardsEntries, setAwardsEntries] = useState<string[]>([]);
  const [newEntry, setNewEntry] = useState("");

  const { uploadResume, getUserProfile, updateUserProfile } = useApiServices();

  // Load user profile data
  useEffect(() => {
    const loadUserProfile = async () => {
      try {
        const profile = await getUserProfile();
        if (profile) {
          // Map the API response to our local state
          setUserProfile(prev => ({
            ...prev,
            phone: profile.phone || "",
            location: profile.address || "",
            linkedin: profile.linkedin_profile || "",
            website: profile.personal_website || "",
            skills: profile.skills?.map((s: any) => s.name || s) || []
          }));
          // For now, we'll use empty arrays for sections not in the API
          setEducationEntries([]);
          setProjectsEntries([]);
          setCertificationsEntries([]);
          setAwardsEntries([]);
        }
      } catch (err) {
        console.error("Failed to load user profile:", err);
      }
    };
    loadUserProfile();
  }, [getUserProfile]);

  // Load workflow status
  useEffect(() => {
    const fetchStatus = async () => {
      const status = await getWorkflowStatus();
      setWorkflowStatus(status);
    };
    fetchStatus();
  }, []);

  // Fetch AI suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      // TODO: Replace with an actual API call to fetch dynamic AI suggestions
      // For now, we'll set it to an empty array.
      setAiSuggestions([]);
    };
    fetchSuggestions();
  }, [isOptimizing]); // Refetch when optimization runs

  const handleOptimize = useCallback(async () => {
    setIsOptimizing(true);
    setError(null);
    try {
      // This would call the backend optimization service
      console.log("Analytics: Optimize resume");
      // Simulate optimization process
      await new Promise(resolve => setTimeout(resolve, 2000));
      setAtsScore(95);
      setShowAISuggestions(true);
    } catch (err) {
      setError("Failed to optimize resume. Please try again.");
    } finally {
      setIsOptimizing(false);
    }
  }, []);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      // Create the profile object that matches the API
      const profileToSave = {
        phone: userProfile.phone,
        address: userProfile.location,
        personal_website: userProfile.website,
        linkedin_profile: userProfile.linkedin,
        skills: userProfile.skills.map(skill => ({ name: skill })),
        // Add other fields as needed
      };
      await updateUserProfile(profileToSave);
      console.log("Resume saved successfully");
    } catch (err) {
      setError("Failed to save resume. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }, [userProfile, updateUserProfile]);

  const handleExport = useCallback(async () => {
    setIsExporting(true);
    setError(null);
    try {
      // This would generate and download PDF
      console.log("Analytics: Export PDF");
      await new Promise(resolve => setTimeout(resolve, 1500));
      // Simulate PDF download
      const link = document.createElement('a');
      link.href = '#';
      link.download = 'resume.pdf';
      link.click();
    } catch (err) {
      setError("Failed to export PDF. Please try again.");
    } finally {
      setIsExporting(false);
    }
  }, []);

  const handlePreview = useCallback(() => {
    // This would open preview modal
    console.log("Analytics: Preview resume");
    // For now, just log the action
  }, []);

  const handleFileSelect = useCallback((file: File | null) => {
    setResumeFile(file);
    setError(null);
  }, []);

  const handleUpload = useCallback(async () => {
    if (!resumeFile) {
      setError("Please select a resume file to upload.");
      return;
    }
    setIsUploading(true);
    setError(null);
    setUploadResult(null);
    console.log("Analytics: Resume upload", resumeFile)
    try {
      const data = await uploadResume(resumeFile);
      setUploadResult(data);
      // Update ATS score based on uploaded resume - handle the response properly
      if (data && typeof data === 'object' && 'ats_score' in data) {
        setAtsScore(data.ats_score as number);
      } else {
        setAtsScore(85); // Default score
      }
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message || "An error occurred");
      } else {
        setError("An unknown error occurred");
      }
    } finally {
      setIsUploading(false);
    }
  }, [resumeFile, uploadResume]);

  const handleWorkflowToggle = useCallback(async (isRunning: boolean) => {
    setWorkflowStatus(prev => prev ? { ...prev, is_running: isRunning } : null); // Optimistic update
    try {
      const newStatus = await updateWorkflowStatus(isRunning);
      setWorkflowStatus(newStatus);
    } catch (err) {
      setError("Failed to update workflow status. Please try again.");
      setWorkflowStatus(prev => prev ? { ...prev, is_running: !isRunning } : null); // Revert on error
    }
  }, []);

  const handleProfileChange = useCallback((field: string, value: string) => {
    setUserProfile(prev => ({ ...prev, [field]: value }));
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600"
    if (score >= 80) return "text-blue-600"
    if (score >= 70) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreGradient = (score: number) => {
    if (score >= 90) return "from-green-500 to-emerald-500"
    if (score >= 80) return "from-blue-500 to-cyan-500"
    if (score >= 70) return "from-yellow-500 to-orange-500"
    return "from-red-500 to-pink-500"
  }

  const wordCount = useMemo(() => {
    const text = userProfile.summary + userProfile.experience.map(exp => exp.description || "").join(' ') + userProfile.skills.join(' ');
    return text.split(' ').filter(word => word.length > 0).length;
  }, [userProfile]);

  const sectionCount = useMemo(() => {
    let count = 0;
    if (userProfile.summary) count++;
    if (userProfile.experience.length > 0) count++;
    if (userProfile.skills.length > 0) count++;
    if (educationEntries.length > 0) count++;
    if (projectsEntries.length > 0) count++;
    if (certificationsEntries.length > 0) count++;
    if (awardsEntries.length > 0) count++;
    return count;
  }, [userProfile, educationEntries, projectsEntries, certificationsEntries, awardsEntries]);

  const keywordCount = useMemo(() => {
    const keywords = userProfile.skills.join(' ').toLowerCase().split(' ');
    return new Set(keywords).size;
  }, [userProfile.skills]);

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Resume Editor" tabIndex={-1} className="flex gap-6 h-full focus:outline-none">
        {/* Main Editor */}
        <div className="flex-1 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Resume Editor</h1>
              <p className="text-muted-foreground">Create and optimize your resume with AI assistance</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handlePreview}>
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </Button>
              <Button variant="outline" onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save
                  </>
                )}
              </Button>
              <Button
                className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700"
                onClick={handleExport}
                disabled={isExporting}
              >
                {isExporting ? (
                  <>
                    <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Export PDF
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Section Navigation */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-wrap gap-2">
                {resumeSections.map((section) => (
                  <Button
                    key={section.id}
                    variant={activeSection === section.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setActiveSection(section.id)}
                    className="relative"
                  >
                    {section.title}
                    {section.required && (
                      <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                    )}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Editor Content */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GripVertical className="w-5 h-5 text-muted-foreground" />
                {resumeSections.find((s) => s.id === activeSection)?.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {activeSection === "header" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Full Name</label>
                    <Input
                      placeholder="John Doe"
                      value={userProfile.firstName}
                      onChange={(e) => handleProfileChange("firstName", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Job Title</label>
                    <Input
                      placeholder="Senior Software Engineer"
                      value={userProfile.jobTitle || ""}
                      onChange={(e) => handleProfileChange("jobTitle", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Email</label>
                    <Input
                      type="email"
                      placeholder="john@example.com"
                      value={userProfile.email}
                      onChange={(e) => handleProfileChange("email", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Phone</label>
                    <Input
                      placeholder="+1 (555) 123-4567"
                      value={userProfile.phone}
                      onChange={(e) => handleProfileChange("phone", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Location</label>
                    <Input
                      placeholder="San Francisco, CA"
                      value={userProfile.location}
                      onChange={(e) => handleProfileChange("location", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">LinkedIn</label>
                    <Input
                      placeholder="linkedin.com/in/johndoe"
                      value={userProfile.linkedin}
                      onChange={(e) => handleProfileChange("linkedin", e.target.value)}
                    />
                  </div>
                </div>
              )}

              {activeSection === "summary" && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Professional Summary</label>
                  <Textarea
                    placeholder="Write a compelling summary that highlights your key achievements and skills..."
                    rows={6}
                    className="resize-none"
                    value={userProfile.summary}
                    onChange={(e) => handleProfileChange("summary", e.target.value)}
                  />
                  <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                    <Sparkles className="w-4 h-4" />
                    <span>AI will help optimize this section for ATS systems</span>
                  </div>
                </div>
              )}

              {activeSection === "experience" && (
                <div className="space-y-6">
                  {userProfile.experience.map((exp, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="text-sm font-medium mb-2 block">Job Title</label>
                          <Input
                            placeholder="Senior Software Engineer"
                            value={exp.title || ""}
                            onChange={(e) => {
                              const newExp = [...userProfile.experience];
                              newExp[index] = { ...newExp[index], title: e.target.value };
                              setUserProfile(prev => ({ ...prev, experience: newExp }));
                            }}
                          />
                        </div>
                        <div>
                          <label className="text-sm font-medium mb-2 block">Company</label>
                          <Input
                            placeholder="Google"
                            value={exp.company || ""}
                            onChange={(e) => {
                              const newExp = [...userProfile.experience];
                              newExp[index] = { ...newExp[index], company: e.target.value };
                              setUserProfile(prev => ({ ...prev, experience: newExp }));
                            }}
                          />
                        </div>
                        <div>
                          <label className="text-sm font-medium mb-2 block">Start Date</label>
                          <Input
                            type="month"
                            value={exp.startDate || ""}
                            onChange={(e) => {
                              const newExp = [...userProfile.experience];
                              newExp[index] = { ...newExp[index], startDate: e.target.value };
                              setUserProfile(prev => ({ ...prev, experience: newExp }));
                            }}
                          />
                        </div>
                        <div>
                          <label className="text-sm font-medium mb-2 block">End Date</label>
                          <Input
                            type="month"
                            placeholder="Present"
                            value={exp.endDate || ""}
                            onChange={(e) => {
                              const newExp = [...userProfile.experience];
                              newExp[index] = { ...newExp[index], endDate: e.target.value };
                              setUserProfile(prev => ({ ...prev, experience: newExp }));
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Description</label>
                        <Textarea
                          placeholder="• Led a team of 5 engineers to develop..."
                          rows={4}
                          className="resize-none"
                          value={exp.description || ""}
                          onChange={(e) => {
                            const newExp = [...userProfile.experience];
                            newExp[index] = { ...newExp[index], description: e.target.value };
                            setUserProfile(prev => ({ ...prev, experience: newExp }));
                          }}
                        />
                      </div>
                      <div className="flex justify-end mt-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const newExp = userProfile.experience.filter((_, i) => i !== index);
                            setUserProfile(prev => ({ ...prev, experience: newExp }));
                          }}
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Remove
                        </Button>
                      </div>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    className="w-full bg-transparent"
                    onClick={() => {
                      const newExp = [...userProfile.experience, { title: "", company: "", startDate: "", endDate: "", description: "" }];
                      setUserProfile(prev => ({ ...prev, experience: newExp }));
                    }}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Experience
                  </Button>
                </div>
              )}

              {activeSection === "skills" && (
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Technical Skills</label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {userProfile.skills.map((skill, index) => (
                        <Badge key={index} variant="secondary" className="cursor-pointer">
                          {skill}
                          <button
                            className="ml-2 hover:text-red-500"
                            onClick={() => {
                              const newSkills = userProfile.skills.filter((_, i) => i !== index);
                              setUserProfile(prev => ({ ...prev, skills: newSkills }));
                            }}
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                    <Input
                      placeholder="Add a skill and press Enter"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                          const newSkills = [...userProfile.skills, e.currentTarget.value.trim()];
                          setUserProfile(prev => ({ ...prev, skills: newSkills }));
                          e.currentTarget.value = '';
                        }
                      }}
                    />
                  </div>
                </div>
              )}

              {activeSection === "education" && (
                <div className="space-y-4">
                  <ul className="mb-2">
                    {educationEntries.map((entry, idx) => (
                      <li key={idx} className="border rounded p-2 flex justify-between items-center mb-2">
                        <span>{entry}</span>
                        <Button variant="outline" size="sm" onClick={() => setEducationEntries(educationEntries.filter((_, i) => i !== idx))}>Remove</Button>
                      </li>
                    ))}
                  </ul>
                  <div className="flex gap-2">
                    <Input value={newEntry} onChange={e => setNewEntry(e.target.value)} placeholder="Add education..." />
                    <Button onClick={() => { if (newEntry) { setEducationEntries([...educationEntries, newEntry]); setNewEntry(""); } }} variant="outline">Add</Button>
                  </div>
                </div>
              )}
              {activeSection === "projects" && (
                <div className="space-y-4">
                  <ul className="mb-2">
                    {projectsEntries.map((entry, idx) => (
                      <li key={idx} className="border rounded p-2 flex justify-between items-center mb-2">
                        <span>{entry}</span>
                        <Button variant="outline" size="sm" onClick={() => setProjectsEntries(projectsEntries.filter((_, i) => i !== idx))}>Remove</Button>
                      </li>
                    ))}
                  </ul>
                  <div className="flex gap-2">
                    <Input value={newEntry} onChange={e => setNewEntry(e.target.value)} placeholder="Add project..." />
                    <Button onClick={() => { if (newEntry) { setProjectsEntries([...projectsEntries, newEntry]); setNewEntry(""); } }} variant="outline">Add</Button>
                  </div>
                </div>
              )}
              {activeSection === "certifications" && (
                <div className="space-y-4">
                  <ul className="mb-2">
                    {certificationsEntries.map((entry, idx) => (
                      <li key={idx} className="border rounded p-2 flex justify-between items-center mb-2">
                        <span>{entry}</span>
                        <Button variant="outline" size="sm" onClick={() => setCertificationsEntries(certificationsEntries.filter((_, i) => i !== idx))}>Remove</Button>
                      </li>
                    ))}
                  </ul>
                  <div className="flex gap-2">
                    <Input value={newEntry} onChange={e => setNewEntry(e.target.value)} placeholder="Add certification..." />
                    <Button onClick={() => { if (newEntry) { setCertificationsEntries([...certificationsEntries, newEntry]); setNewEntry(""); } }} variant="outline">Add</Button>
                  </div>
                </div>
              )}
              {activeSection === "awards" && (
                <div className="space-y-4">
                  <ul className="mb-2">
                    {awardsEntries.map((entry, idx) => (
                      <li key={idx} className="border rounded p-2 flex justify-between items-center mb-2">
                        <span>{entry}</span>
                        <Button variant="outline" size="sm" onClick={() => setAwardsEntries(awardsEntries.filter((_, i) => i !== idx))}>Remove</Button>
                      </li>
                    ))}
                  </ul>
                  <div className="flex gap-2">
                    <Input value={newEntry} onChange={e => setNewEntry(e.target.value)} placeholder="Add award..." />
                    <Button onClick={() => { if (newEntry) { setAwardsEntries([...awardsEntries, newEntry]); setNewEntry(""); } }} variant="outline">Add</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 space-y-6">
          {/* ATS Score */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                ATS Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center mb-4">
                <div
                  className={`text-4xl font-bold mb-2 bg-gradient-to-r ${getScoreGradient(atsScore)} bg-clip-text text-transparent`}
                >
                  {atsScore}
                </div>
                <Progress value={atsScore} className="h-3" />
                <p className="text-sm text-muted-foreground mt-2">
                  {atsScore >= 90 ? "Excellent" : atsScore >= 80 ? "Good" : atsScore >= 70 ? "Fair" : "Needs Improvement"}
                </p>
              </div>
              <Button
                onClick={handleOptimize}
                disabled={isOptimizing || !workflowStatus?.is_running}
                className="w-full bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700"
              >
                {isOptimizing ? (
                  <>
                    <div className="w-4 h-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Auto-Optimize
                  </>
                )}
              </Button>
              {!workflowStatus?.is_running && (
                <p className="text-xs text-center text-red-500 mt-2">
                  Workflow is paused.
                </p>
              )}
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          {showAISuggestions && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5" />
                    AI Suggestions
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setShowAISuggestions(false)}>
                    ×
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {aiSuggestions.map((suggestion, index) => (
                  <Alert key={index} className="p-3">
                    <div className="flex items-start gap-3">
                      {suggestion.type === "improvement" ? (
                        <TrendingUp className="w-4 h-4 text-blue-600 mt-0.5" />
                      ) : suggestion.type === "keyword" ? (
                        <Target className="w-4 h-4 text-green-600 mt-0.5" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-orange-600 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className="font-medium text-sm mb-1">{suggestion.section}</div>
                        <AlertDescription className="text-xs">{suggestion.suggestion}</AlertDescription>
                        {suggestion.example && (
                          <div className="mt-2 p-2 bg-muted rounded text-xs">{suggestion.example}</div>
                        )}
                        {suggestion.impact && (
                          <Badge variant="outline" className="mt-2 text-xs">
                            {suggestion.impact} impact
                          </Badge>
                        )}
                      </div>
                    </div>
                  </Alert>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Resume Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Word Count</span>
                <span className="text-sm font-medium">{wordCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Sections</span>
                <span className="text-sm font-medium">{sectionCount}/8</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Keywords</span>
                <span className="text-sm font-medium">{keywordCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Last Updated</span>
                <span className="text-sm font-medium">Just now</span>
              </div>
            </CardContent>
          </Card>

          {/* Workflow Status */}
          <Card>
            <CardHeader>
              <CardTitle>Agent Workflow</CardTitle>
            </CardHeader>
            <CardContent>
              {workflowStatus ? (
                <div className="flex items-center justify-between">
                  <Label htmlFor="workflow-toggle" className={`font-medium ${workflowStatus.is_running ? 'text-green-600' : 'text-red-600'}`}>
                    {workflowStatus.is_running ? 'Running' : 'Paused'}
                  </Label>
                  <Switch
                    id="workflow-toggle"
                    checked={workflowStatus.is_running}
                    onCheckedChange={handleWorkflowToggle}
                    aria-label={`Toggle agent workflow ${workflowStatus.is_running ? 'off' : 'on'}`}
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  <span>Loading status...</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Resume Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Resume Upload</CardTitle>
            </CardHeader>
            <CardContent>
              <FileUploadResume onFileSelect={handleFileSelect} onUpload={handleUpload} />
              {isUploading && (
                <div className="mt-4 text-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto"></div>
                  <p className="text-sm text-gray-600 mt-2">Uploading...</p>
                </div>
              )}
              {uploadResult && (
                <Alert className="mt-4 border-green-200 bg-green-50">
                  <AlertDescription className="text-green-800">
                    Resume uploaded successfully!
                  </AlertDescription>
                </Alert>
              )}
              {error && (
                <Alert variant="destructive" className="mt-4">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </ErrorBoundary>
  )
}
