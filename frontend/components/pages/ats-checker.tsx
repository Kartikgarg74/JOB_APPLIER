"use client"

import React, { useState, useRef, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, FileText, Link, CheckCircle, AlertTriangle, TrendingUp, Target, Zap, Download, X, RefreshCw, Eye, Info } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { useApiServices } from '@/lib/api-context';
import { AtsResults } from '@/lib/ats';
import { useMemo } from 'react';

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

// File Upload Component for ATS Checker
function FileUploadATS({ onFileSelect }: { onFileSelect: (file: File) => void }) {
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
    onFileSelect(null as any);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  }, [onFileSelect]);

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
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
            <Button variant="outline" size="sm" onClick={handleRemoveFile}>
              <X className="w-4 h-4 mr-2" />
              Remove File
            </Button>
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
        aria-label="Upload resume file for ATS analysis"
        title="Upload resume file for ATS analysis"
      />
    </div>
  );
}

export function ATSChecker() {
  const [activeTab, setActiveTab] = useState("upload");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [atsResults, setAtsResults] = useState<AtsResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { fetchAtsScore } = useApiServices();

  const getScoreColor = useCallback((score: number) => {
    if (score >= 85) return "text-green-600"
    if (score >= 70) return "text-yellow-600"
    return "text-red-600"
  }, []);

  const getScoreGradient = useCallback((score: number) => {
    if (score >= 85) return "from-green-500 to-emerald-500"
    if (score >= 70) return "from-yellow-500 to-orange-500"
    return "from-red-500 to-pink-500"
  }, []);

  const handleFileSelect = useCallback((file: File | null) => {
    setResumeFile(file);
    setError(null);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!resumeFile || !jobDescription.trim()) {
      setError("Please upload a resume and provide a job description.");
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAtsResults(null);

    try {
      const data = await fetchAtsScore(resumeFile, jobDescription);
      setAtsResults(data);
      console.log("ATS Analysis completed:", data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to analyze resume. Please try again.");
      } else {
        setError("An unknown error occurred during analysis.");
      }
      console.error("ATS Analysis error:", err);
    } finally {
      setIsAnalyzing(false);
    }
  }, [resumeFile, jobDescription, fetchAtsScore]);

  const handleStartNewScan = useCallback(() => {
    setResumeFile(null);
    setJobDescription("");
    setAtsResults(null);
    setError(null);
  }, []);

  const handleCheckResults = useCallback(() => {
    if (atsResults) {
      // Scroll to results section
      const resultsElement = document.getElementById('ats-results');
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [atsResults]);

  if (showResults) {
    return (
      <div className="space-y-6 px-2 sm:px-4 md:px-0">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold mb-2">ATS Analysis Results</h1>
            <p className="text-muted-foreground text-base sm:text-lg">Your resume analysis is complete</p>
          </div>
          <Button onClick={() => setShowResults(false)} variant="outline" className="w-full sm:w-auto">
            Analyze Another Resume
          </Button>
        </div>

        {/* Results Section */}
        {atsResults && (
          <Card id="ats-results" className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                ATS Analysis Results
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Score Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {atsResults.score || 0}%
                  </div>
                  <div className="text-sm text-blue-600 font-medium">Overall Score</div>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {atsResults.skillsMatch || 0}%
                  </div>
                  <div className="text-sm text-green-600 font-medium">Skills Match</div>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 rounded-lg">
                  <div className="text-3xl font-bold text-purple-600 mb-2">
                    {atsResults.keywordsMatch || 0}%
                  </div>
                  <div className="text-sm text-purple-600 font-medium">Keywords Match</div>
                </div>
              </div>

              {/* Grade */}
              <div className="text-center">
                <Badge
                  variant={atsResults.grade === 'A' ? 'default' : atsResults.grade === 'B' ? 'secondary' : 'destructive'}
                  className="text-lg px-4 py-2"
                >
                  Grade: {atsResults.grade || 'N/A'}
                </Badge>
              </div>

              {/* Suggestions */}
              {atsResults.suggestions && atsResults.suggestions.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
                  <div className="space-y-3">
                    {atsResults.suggestions.map((suggestion, index) => (
                      <Alert key={index} className={`border-l-4 ${
                        suggestion.type === 'success' ? 'border-green-500 bg-green-50' :
                        suggestion.type === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                        'border-blue-500 bg-blue-50'
                      }`}>
                        <div className="flex items-start gap-3">
                          {suggestion.type === 'success' ? (
                            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                          ) : suggestion.type === 'warning' ? (
                            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                          ) : (
                            <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                          )}
                          <div className="flex-1">
                            <div className="font-medium mb-1">{suggestion.title}</div>
                            <AlertDescription className="text-sm">
                              {suggestion.description}
                            </AlertDescription>
                            {suggestion.impact && (
                              <Badge variant="outline" className="mt-2 text-xs">
                                {suggestion.impact} impact
                              </Badge>
                            )}
                          </div>
                        </div>
                      </Alert>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills Analysis */}
              {atsResults.skillsAnalysis && atsResults.skillsAnalysis.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Skills Analysis</h3>
                  <div className="grid gap-3">
                    {atsResults.skillsAnalysis.map((skill, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="font-medium">{skill.skill}</span>
                          <Badge variant={skill.required ? "default" : "secondary"}>
                            {skill.required ? "Required" : "Optional"}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                skill.match >= 80 ? 'bg-green-500' :
                                skill.match >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${skill.match}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{skill.match}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 justify-center">
                <Button onClick={handleStartNewScan} variant="outline">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Start New Scan
                </Button>
                <Button onClick={handleCheckResults}>
                  <Eye className="w-4 h-4 mr-2" />
                  View Detailed Report
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <main role="main" aria-label="ATS Resume Checker" tabIndex={-1} className="space-y-6 px-2 sm:px-4 md:px-0 focus:outline-none">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
            <AlertDescription>
              <div className="flex justify-between items-center">
                <span>{error}</span>
                <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
              </div>
            </AlertDescription>
          </Alert>
        )}
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold mb-2">ATS Resume Checker</h1>
          <p className="text-muted-foreground">Analyze your resume against ATS systems and get actionable insights</p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="upload">Upload Resume</TabsTrigger>
              <TabsTrigger value="job-description">Job Description</TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="w-5 h-5" />
                    Upload Your Resume
                  </CardTitle>
                  <CardDescription>Upload your resume in PDF or DOCX format for analysis</CardDescription>
                </CardHeader>
                <CardContent>
                  <FileUploadATS onFileSelect={handleFileSelect} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="job-description" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Job Description
                  </CardTitle>
                  <CardDescription>Paste the job description or provide a job posting URL</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Job Posting URL (Optional)</label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Link className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                        <Input placeholder="https://linkedin.com/jobs/..." className="pl-10" />
                      </div>
                      <Button variant="outline">Fetch</Button>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Job Description</label>
                    <Textarea
                      placeholder="Paste the complete job description here..."
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      rows={10}
                      className="resize-none"
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Analysis Button */}
          <Card>
            <CardContent className="p-6 text-center">
              <Button
                size="lg"
                onClick={handleAnalyze}
                disabled={isAnalyzing || !resumeFile || !jobDescription}
                className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700"
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-5 h-5 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Analyzing Resume...
                  </>
                ) : (
                  <>
                    <Target className="w-5 h-5 mr-2" />
                    Check ATS Score
                  </>
                )}
              </Button>
              {isAnalyzing && (
                <p className="text-sm text-muted-foreground mt-4">
                  This may take a few moments while we analyze your resume...
                </p>
              )}
              {!resumeFile && (
                <p className="text-sm text-yellow-600 mt-4">Please upload a resume file</p>
              )}
              {!jobDescription && (
                <p className="text-sm text-yellow-600 mt-4">Please provide a job description</p>
              )}
            </CardContent>
          </Card>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold mb-2">ATS Compatibility</h3>
                <p className="text-sm text-muted-foreground">Check how well your resume passes through ATS systems</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold mb-2">Keyword Optimization</h3>
                <p className="text-sm text-muted-foreground">
                  Ensure your resume includes relevant keywords from job descriptions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold mb-2">AI Suggestions</h3>
                <p className="text-sm text-muted-foreground">Get personalized recommendations to improve your resume</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </ErrorBoundary>
  )
}
