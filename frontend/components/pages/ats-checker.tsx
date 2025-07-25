"use client"

import React, { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, FileText, Link, CheckCircle, AlertTriangle, TrendingUp, Target, Zap, Download } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { apiRequest } from "@/lib/utils";

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

export function ATSChecker() {
  const [activeTab, setActiveTab] = useState("upload");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [atsResults, setAtsResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!resumeFile || !jobDescription) {
      setError("Please upload a resume and provide a job description.");
      return;
    }
    setIsAnalyzing(true);
    setError(null);
    setShowResults(false);
    setAtsResults(null);
    try {
      const formData = new FormData();
      formData.append("resume_file", resumeFile);
      formData.append("job_description", jobDescription);
      const result = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/v1"}/ats-score`, {
        method: "POST",
        body: formData,
      });
      if (!result.ok) {
        const err = await result.json();
        throw new Error(err.message || "Failed to get ATS score");
      }
      const data = await result.json();
      setAtsResults(data);
      setShowResults(true);
    } catch (e: any) {
      setError(e.message || "An error occurred");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-green-600"
    if (score >= 70) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreGradient = (score: number) => {
    if (score >= 85) return "from-green-500 to-emerald-500"
    if (score >= 70) return "from-yellow-500 to-orange-500"
    return "from-red-500 to-pink-500"
  }

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

        {/* Score Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          <Card className="md:col-span-2">
            <CardHeader className="text-center">
              <CardTitle>Overall ATS Score</CardTitle>
              <CardDescription>Based on industry standards</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <div
                className={`text-4xl sm:text-6xl font-bold mb-2 bg-gradient-to-r ${getScoreGradient(atsResults?.score)} bg-clip-text text-transparent`}
              >
                {atsResults?.score}
              </div>
              <Badge
                className={`text-base sm:text-lg px-4 py-1 ${getScoreColor(atsResults?.score)} bg-transparent border-current`}
              >
                {atsResults?.grade}
              </Badge>
              <Progress value={atsResults?.score} className="mt-4 h-3" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base sm:text-lg">Skills Match</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl sm:text-3xl font-bold mb-2">{atsResults?.skillsMatch}%</div>
              <Progress value={atsResults?.skillsMatch} className="h-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base sm:text-lg">Keywords</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl sm:text-3xl font-bold mb-2">{atsResults?.keywordsMatch}%</div>
              <Progress value={atsResults?.keywordsMatch} className="h-2" />
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {/* Suggestions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Improvement Suggestions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {atsResults?.suggestions?.map((suggestion: any, index: number) => (
                <Alert
                  key={index}
                  className={
                    suggestion.type === "success"
                      ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950"
                      : suggestion.type === "warning"
                        ? "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950"
                        : "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950"
                  }
                >
                  <div className="flex items-start gap-3">
                    {suggestion.type === "success" ? (
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                    ) : suggestion.type === "warning" ? (
                      <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    ) : (
                      <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1 text-base sm:text-lg">{suggestion.title}</h4>
                      <AlertDescription className="text-xs sm:text-sm">{suggestion.description}</AlertDescription>
                      <Badge variant="outline" className="mt-2 text-xs sm:text-sm">
                        {suggestion.impact} impact
                      </Badge>
                    </div>
                  </div>
                </Alert>
              ))}
            </CardContent>
          </Card>

          {/* Skills Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Skills Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {atsResults?.skillsAnalysis?.map((skill: any, index: number) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{skill.skill}</span>
                      {skill.required && (
                        <Badge variant="destructive" className="text-xs">
                          Required
                        </Badge>
                      )}
                    </div>
                    <span className={`font-semibold ${getScoreColor(skill.match)}`}>{skill.match}%</span>
                  </div>
                  <Progress value={skill.match} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <Card>
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row flex-wrap gap-2 sm:gap-4 justify-center">
              <Button
                size="lg"
                className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700"
              >
                <Zap className="w-5 h-5 mr-2" />
                Auto-Improve Resume
              </Button>
              <Button size="lg" variant="outline">
                <Download className="w-5 h-5 mr-2" />
                Download Report
              </Button>
              <Button size="lg" variant="outline">
                <FileText className="w-5 h-5 mr-2" />
                Edit Resume
              </Button>
            </div>
          </CardContent>
        </Card>
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
                  <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center hover:border-muted-foreground/50 transition-colors">
                    <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">Drop your resume here</h3>
                    <p className="text-muted-foreground mb-4">or click to browse files</p>
                    <Button>
                      <FileText className="w-4 h-4 mr-2" />
                      Choose File
                    </Button>
                    <p className="text-xs text-muted-foreground mt-4">Supports PDF, DOC, DOCX files up to 10MB</p>
                  </div>
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
                disabled={isAnalyzing}
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
              {error && (
                <p className="text-sm text-red-500 mt-4">{error}</p>
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
