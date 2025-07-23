"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
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
} from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { apiRequest } from "@/lib/utils";

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

const aiSuggestions = [
  {
    type: "improvement",
    section: "Professional Summary",
    suggestion: "Add quantifiable achievements to make your summary more impactful",
    example:
      "Instead of 'Experienced developer', try 'Senior developer with 5+ years building scalable applications for 10M+ users'",
  },
  {
    type: "keyword",
    section: "Skills",
    suggestion: "Add 'React Hooks' and 'TypeScript' to match job requirements",
    impact: "high",
  },
  {
    type: "format",
    section: "Work Experience",
    suggestion: "Use bullet points starting with action verbs for better ATS parsing",
    impact: "medium",
  },
]

export function ResumeEditor() {
  const [activeSection, setActiveSection] = useState("header")
  const [atsScore, setAtsScore] = useState(87)
  const [showAISuggestions, setShowAISuggestions] = useState(true)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Add state for dynamic sections
  const [educationEntries, setEducationEntries] = useState<any[]>([]);
  const [projectsEntries, setProjectsEntries] = useState<any[]>([]);
  const [certificationsEntries, setCertificationsEntries] = useState<any[]>([]);
  const [awardsEntries, setAwardsEntries] = useState<any[]>([]);
  const [newEntry, setNewEntry] = useState("");

  const handleOptimize = () => {
    setIsOptimizing(true)
    setTimeout(() => {
      setAtsScore(95)
      setIsOptimizing(false)
      // Confetti animation would trigger here
    }, 2000)
  }

  const handleUpload = async () => {
    if (!resumeFile) {
      setError("Please select a resume file to upload.");
      return;
    }
    setIsUploading(true);
    setError(null);
    setUploadResult(null);
    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      const result = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1"}/upload-resume`, {
        method: "POST",
        body: formData,
      });
      if (!result.ok) {
        const err = await result.json();
        throw new Error(err.message || "Failed to upload resume");
      }
      const data = await result.json();
      setUploadResult(data);
    } catch (e: any) {
      setError(e.message || "An error occurred");
    } finally {
      setIsUploading(false);
    }
  };

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

  return (
    <div className="flex gap-6 h-full">
      {/* Main Editor */}
      <div className="flex-1 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Resume Editor</h1>
            <p className="text-muted-foreground">Create and optimize your resume with AI assistance</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </Button>
            <Button variant="outline">
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
            <Button className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700">
              <Download className="w-4 h-4 mr-2" />
              Export PDF
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
                  <Input placeholder="John Doe" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Job Title</label>
                  <Input placeholder="Senior Software Engineer" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Email</label>
                  <Input type="email" placeholder="john@example.com" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Phone</label>
                  <Input placeholder="+1 (555) 123-4567" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Location</label>
                  <Input placeholder="San Francisco, CA" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">LinkedIn</label>
                  <Input placeholder="linkedin.com/in/johndoe" />
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
                />
                <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                  <Sparkles className="w-4 h-4" />
                  <span>AI will help optimize this section for ATS systems</span>
                </div>
              </div>
            )}

            {activeSection === "experience" && (
              <div className="space-y-6">
                <div className="border rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">Job Title</label>
                      <Input placeholder="Senior Software Engineer" />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Company</label>
                      <Input placeholder="Google" />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Start Date</label>
                      <Input type="month" />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">End Date</label>
                      <Input type="month" placeholder="Present" />
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Description</label>
                    <Textarea
                      placeholder="• Led a team of 5 engineers to develop..."
                      rows={4}
                      className="resize-none"
                    />
                  </div>
                  <div className="flex justify-end mt-4">
                    <Button variant="outline" size="sm">
                      <Trash2 className="w-4 h-4 mr-2" />
                      Remove
                    </Button>
                  </div>
                </div>
                <Button variant="outline" className="w-full bg-transparent">
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
                    {["React", "TypeScript", "Node.js", "Python", "AWS"].map((skill) => (
                      <Badge key={skill} variant="secondary" className="cursor-pointer">
                        {skill}
                        <button className="ml-2 hover:text-red-500">×</button>
                      </Badge>
                    ))}
                  </div>
                  <Input placeholder="Add a skill and press Enter" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Soft Skills</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {["Leadership", "Communication", "Problem Solving"].map((skill) => (
                      <Badge key={skill} variant="outline" className="cursor-pointer">
                        {skill}
                        <button className="ml-2 hover:text-red-500">×</button>
                      </Badge>
                    ))}
                  </div>
                  <Input placeholder="Add a soft skill and press Enter" />
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
              disabled={isOptimizing}
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
              <span className="text-sm font-medium">247</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Sections</span>
              <span className="text-sm font-medium">6/8</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Keywords</span>
              <span className="text-sm font-medium">23</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Last Updated</span>
              <span className="text-sm font-medium">2 min ago</span>
            </div>
          </CardContent>
        </Card>

        {/* Resume Upload */}
        <Card>
          <CardHeader>
            <CardTitle>Resume Upload</CardTitle>
          </CardHeader>
          <CardContent>
            <label htmlFor="resume-upload" className="text-sm font-medium mb-1 block">Upload Resume File</label>
            <input
              id="resume-upload"
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={e => {
                const file = e.target.files?.[0] || null;
                setResumeFile(file);
                if (file) handleUpload();
              }}
              className="mb-2"
              placeholder="Choose a file..."
            />
            {resumeFile && <div className="text-xs text-muted-foreground">Selected: {resumeFile.name}</div>}
            <Button onClick={handleUpload} disabled={isUploading || !resumeFile} className="w-full mb-2">
              {isUploading ? "Uploading..." : "Upload Resume"}
            </Button>
            {uploadResult && <div className="text-green-600 text-xs">Upload successful!</div>}
            {error && <div className="text-red-600 text-xs">{error}</div>}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
