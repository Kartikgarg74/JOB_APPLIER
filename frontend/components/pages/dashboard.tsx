"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Search, Upload, Clock, TrendingUp, Target, CheckCircle, Building2, Calendar, BarChart3 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import React, { useState, useEffect } from "react";
import useSWR from 'swr';
import { supabase } from '@/lib/supabase';
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

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

const fetcher = async (url: string) => {
  const { data, error } = await supabase.from('job_applications').select('*');
  if (error) throw error;
  return data;
};

// Helper to calculate job match score
const calculateJobMatchScore = (application: any) => {
  const { job_description, resume_content } = application;
  if (!job_description || !resume_content) return 0;

  // Simple keyword matching for demo purposes
  const jobKeywords = job_description.toLowerCase().split(/\W+/);
  const resumeKeywords = resume_content.toLowerCase().split(/\W+/);

  let matchCount = 0;
  jobKeywords.forEach((keyword: string) => {
    if (resumeKeywords.includes(keyword)) {
      matchCount++;
    }
  });

  return Math.min(100, Math.round((matchCount / jobKeywords.length) * 100));
};

// Helper to calculate ATS score (placeholder)
const calculateAtsScore = (application: any) => {
  // In a real application, this would involve more complex NLP or an external ATS API
  // For now, let's return a random score to simulate variability
  return Math.floor(Math.random() * (95 - 70 + 1)) + 70;
};

export function Dashboard() {
  const { data: applications, error, isLoading } = useSWR('job_applications', fetcher);

  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!isLoading) {
      setLoading(false);
    }
  }, [isLoading]);

  const stats = applications ? [
    {
      title: "Jobs Applied",
      value: applications.length.toString(),
      change: "", // Dynamic change calculation can be added here
      icon: Target,
      color: "text-blue-600",
    },
    {
      title: "Success Rate",
      value: `${((applications.filter((app: any) => app.status === 'Interview' || app.status === 'Offer').length / applications.length) * 100 || 0).toFixed(0)}%`,
      change: "",
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      title: "ATS Average Score",
      value: `${(applications.reduce((sum: number, app: any) => sum + calculateAtsScore(app), 0) / applications.length || 0).toFixed(0)}`,
      change: "",
      icon: BarChart3,
      color: "text-purple-600",
    },
    {
      title: "Interviews Scheduled",
      value: applications.filter((app: any) => app.status === 'Interview').length.toString(),
      change: "",
      icon: Calendar,
      color: "text-orange-600",
    },
  ] : [];

  const recentApplications = applications ? applications.slice(0, 3).map((app: any) => ({
    company: app.company_name,
    position: app.job_title,
    appliedDate: new Date(app.created_at).toLocaleDateString(), // Format date as needed
    status: app.status,
    logo: app.company_logo_url || "/placeholder.svg?height=40&width=40",
    jobMatchScore: calculateJobMatchScore(app),
    atsScore: calculateAtsScore(app),
    coverLetterPreview: app.cover_letter_content ? app.cover_letter_content.substring(0, 50) + '...' : 'No cover letter',
  })) : [];

  // Analytics event hooks
  const handleQuickAction = (action: string) => {
    console.log(`Analytics: Quick action clicked - ${action}`);
  };
  const handleStatClick = (title: string) => {
    console.log(`Analytics: Stat clicked - ${title}`);
  };

  if (error) {
    return (
      <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
        <AlertDescription>
          <div className="flex justify-between items-center">
            <span>Failed to load dashboard data: {error.message}</span>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (loading) {
    // Skeleton loaders for stats and recent applications
    return (
      <main role="main" aria-label="Dashboard" tabIndex={-1} className="space-y-8 px-2 sm:px-4 md:px-0 focus:outline-none">
        <Skeleton className="gradient-bg rounded-2xl p-8 h-32 w-full" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="rounded-lg h-24 w-full" />
          ))}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <Skeleton className="sm:col-span-2 rounded-lg h-40 w-full" />
          <Skeleton className="rounded-lg h-40 w-full" />
        </div>
        <Skeleton className="rounded-lg h-32 w-full" />
      </main>
    );
  }

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Dashboard" tabIndex={-1} className="space-y-8 px-2 sm:px-4 md:px-0 focus:outline-none">
        {/* Welcome Section */}
        <div className="gradient-bg rounded-2xl p-4 sm:p-8 text-white">
          <div className="max-w-2xl">
            <h1 className="text-2xl sm:text-3xl font-bold mb-2">Good morning, Alex! 👋</h1>
            <p className="text-white/90 text-base sm:text-lg mb-6">
              Ready to supercharge your job search? You have 3 new job matches waiting for you.
            </p>
            <div className="flex flex-col sm:flex-row flex-wrap gap-3 w-full">
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6" aria-label="Dashboard stats">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <Card key={index} className="stats-card border-0 cursor-pointer focus:ring-2 focus:ring-blue-500" tabIndex={0} aria-label={stat.title} onClick={() => handleStatClick(stat.title)}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs sm:text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl sm:text-3xl font-bold mb-1">{stat.value}</div>
                  <p className="text-xs sm:text-sm text-muted-foreground">{stat.change}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Recent Applications */}
          <Card className="sm:col-span-2" aria-label="Recent applications">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Recent Applications
              </CardTitle>
              <CardDescription>Your latest job applications and their current status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentApplications.map((app, index) => (
                <div key={index} className="flex flex-col sm:flex-row items-center justify-between p-4 rounded-lg border bg-card/50 gap-2 sm:gap-4">
                  <div className="flex items-center gap-4 w-full sm:w-auto">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src={app.logo || "/placeholder.svg"} alt={app.company} />
                      <AvatarFallback>
                        <Building2 className="w-6 h-6" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <h3 className="font-semibold text-base sm:text-lg">{app.position}</h3>
                      <p className="text-sm text-muted-foreground">{app.company} &bull; {app.appliedDate}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1 sm:gap-2">
                    <Badge variant="outline" className={`px-3 py-1 rounded-full text-xs sm:text-sm ${app.status === 'Interview' ? 'bg-blue-100 text-blue-800' : app.status === 'Offer' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {app.status}
                    </Badge>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span className="font-medium">Job Match: {app.jobMatchScore}%</span>
                      <Progress value={app.jobMatchScore} className="w-20 h-2" />
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span className="font-medium">ATS Score: {app.atsScore}%</span>
                      <Progress value={app.atsScore} className="w-20 h-2" />
                    </div>
                  </div>
                  <div className="w-full text-sm text-muted-foreground mt-2 sm:mt-0">
                    <p className="font-medium">Cover Letter Preview:</p>
                    <p className="line-clamp-2">{app.coverLetterPreview}</p>
                  </div>
                </div>
              ))}
            {recentApplications.length === 0 && !loading && (
              <p className="text-center text-muted-foreground">No recent applications found.</p>
            )}
            <Button variant="outline" className="w-full mt-4">
              View All Applications
            </Button>
          </Card>

          {/* Job Match Score Distribution (Placeholder for a chart) */}
          <Card aria-label="Job match score distribution">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Job Match Score Distribution
              </CardTitle>
              <CardDescription>Overview of your job application match scores</CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center items-center h-48">
              {/* This is where a chart component (e.g., from Tremor or Recharts) would go */}
              <p className="text-muted-foreground">Chart coming soon...</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card aria-label="Quick actions">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>Perform common tasks quickly</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button variant="outline" onClick={() => handleQuickAction("New Application")}>
              <Upload className="mr-2 h-4 w-4" /> New Application
            </Button>
            <Button variant="outline" onClick={() => handleQuickAction("Search Jobs")}>
              <Search className="mr-2 h-4 w-4" /> Search Jobs
            </Button>
            <Button variant="outline" onClick={() => handleQuickAction("Update Profile")}>
              <Avatar className="mr-2 h-4 w-4" /> Update Profile
            </Button>
            <Button variant="outline" onClick={() => handleQuickAction("View Analytics")}>
              <BarChart3 className="mr-2 h-4 w-4" /> View Analytics
            </Button>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="border-t border-gray-200 pt-8 text-center text-gray-500 text-sm mt-12">
          <p>&copy; 2024 Job Applier. All rights reserved.</p>
          <p>Your central hub for job application management.</p>
        </div>
      </main>
    </ErrorBoundary>
  );
}

            </CardContent>
          </Card>

          {/* Job Match Score Distribution (Placeholder for a chart) */}
          <Card aria-label="Job match score distribution">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Job Match Score Distribution
              </CardTitle>
              <CardDescription>Overview of your job application match scores</CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center items-center h-48">
              {/* This is where a chart component (e.g., from Tremor or Recharts) would go */}
              <p className="text-muted-foreground">Chart coming soon...</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card aria-label="Quick actions">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>Perform common tasks quickly</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button variant="outline" onClick={() => handleQuickAction("New Application")}>
              <Upload className="mr-2 h-4 w-4" /> New Application
            </Button>
            <Button variant="outline" onClick={() => handleQuickAction("Search Jobs")}>
              <Search className="mr-2 h-4 w-4" /> Search Jobs
            </Button>
            <Button variant="outline" onClick={() => handleQuickAction("Update Profile")}>
              <Avatar className="mr-2 h-4 w-4" /> Update Profile
            </Button>
            <Button variant="outline" onClick={() => handleQuickAction("View Analytics")}>
              <BarChart3 className="mr-2 h-4 w-4" /> View Analytics
            </Button>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="border-t border-gray-200 pt-8 text-center text-gray-500 text-sm mt-12">
          <p>&copy; 2024 Job Applier. All rights reserved.</p>
          <p>Your central hub for job application management.</p>
        </div>
      </main>
    </ErrorBoundary>
  );
}
