"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Search, Upload, Clock, TrendingUp, Target, CheckCircle, Building2, Calendar, BarChart3 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import React, { useState, useEffect } from "react";
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

const stats = [
  {
    title: "Jobs Applied",
    value: "47",
    change: "+12 this week",
    icon: Target,
    color: "text-blue-600",
  },
  {
    title: "Success Rate",
    value: "23%",
    change: "+5% from last month",
    icon: TrendingUp,
    color: "text-green-600",
  },
  {
    title: "ATS Average Score",
    value: "87",
    change: "+3 points",
    icon: BarChart3,
    color: "text-purple-600",
  },
  {
    title: "Interviews Scheduled",
    value: "8",
    change: "+2 this week",
    icon: Calendar,
    color: "text-orange-600",
  },
]

const recentApplications = [
  {
    company: "Google",
    position: "Senior Frontend Developer",
    appliedDate: "2 days ago",
    status: "Interview",
    logo: "/placeholder.svg?height=40&width=40",
  },
  {
    company: "Microsoft",
    position: "Full Stack Engineer",
    appliedDate: "5 days ago",
    status: "Applied",
    logo: "/placeholder.svg?height=40&width=40",
  },
  {
    company: "Netflix",
    position: "React Developer",
    appliedDate: "1 week ago",
    status: "Shortlisted",
    logo: "/placeholder.svg?height=40&width=40",
  },
]

export function Dashboard() {
  // Simulate async data loading and error for demo
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false);
      // setError("Failed to load dashboard data."); // Uncomment to test error UI
    }, 1200);
    return () => clearTimeout(timer);
  }, []);

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
            <span>{error}</span>
            <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
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
              <Button size="lg" className="bg-white text-purple-600 hover:bg-white/90 w-full sm:w-auto" onClick={() => handleQuickAction('Start New Scan')}>
                <Search className="w-5 h-5 mr-2" />
                Start New Scan
              </Button>
              <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/10 bg-transparent w-full sm:w-auto" onClick={() => handleQuickAction('Update Resume')}>
                <Upload className="w-5 h-5 mr-2" />
                Update Resume
              </Button>
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
                    <div>
                      <h4 className="font-semibold text-base sm:text-lg">{app.position}</h4>
                      <p className="text-xs sm:text-sm text-muted-foreground">{app.company}</p>
                      <p className="text-xs text-muted-foreground">{app.appliedDate}</p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      app.status === "Interview" ? "default" : app.status === "Shortlisted" ? "secondary" : "outline"
                    }
                    className={
                      app.status === "Interview"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        : app.status === "Shortlisted"
                          ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                          : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
                    }
                  >
                    {app.status}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card aria-label="Quick actions">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Jump into your most used features</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start bg-transparent text-base sm:text-lg" variant="outline" onClick={() => handleQuickAction('Find New Jobs')}>
                <Search className="w-4 h-4 mr-2" />
                Find New Jobs
              </Button>
              <Button className="w-full justify-start bg-transparent text-base sm:text-lg" variant="outline" onClick={() => handleQuickAction('Upload Resume')}>
                <Upload className="w-4 h-4 mr-2" />
                Upload Resume
              </Button>
              <Button className="w-full justify-start bg-transparent text-base sm:text-lg" variant="outline" onClick={() => handleQuickAction('Check ATS Score')}>
                <CheckCircle className="w-4 h-4 mr-2" />
                Check ATS Score
              </Button>
              <Button className="w-full justify-start bg-transparent text-base sm:text-lg" variant="outline" onClick={() => handleQuickAction('View Applications')}>
                <Clock className="w-4 h-4 mr-2" />
                View Applications
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Progress Section */}
        <Card aria-label="Weekly progress">
          <CardHeader>
            <CardTitle>Weekly Progress</CardTitle>
            <CardDescription>You're doing great! Keep up the momentum.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Applications Goal</span>
                  <span>12/15</span>
                </div>
                <Progress value={80} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Resume Updates</span>
                  <span>3/5</span>
                </div>
                <Progress value={60} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Interview Prep</span>
                  <span>2/3</span>
                </div>
                <Progress value={67} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </ErrorBoundary>
  )
}
