"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Search, Upload, Clock, TrendingUp, Target, CheckCircle, Building2, Calendar, BarChart3 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

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
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="gradient-bg rounded-2xl p-8 text-white">
        <div className="max-w-2xl">
          <h1 className="text-3xl font-bold mb-2">Good morning, Alex! 👋</h1>
          <p className="text-white/90 text-lg mb-6">
            Ready to supercharge your job search? You have 3 new job matches waiting for you.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button size="lg" className="bg-white text-purple-600 hover:bg-white/90">
              <Search className="w-5 h-5 mr-2" />
              Start New Scan
            </Button>
            <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/10 bg-transparent">
              <Upload className="w-5 h-5 mr-2" />
              Update Resume
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index} className="stats-card border-0">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-1">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.change}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Applications */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Recent Applications
            </CardTitle>
            <CardDescription>Your latest job applications and their current status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentApplications.map((app, index) => (
              <div key={index} className="flex items-center justify-between p-4 rounded-lg border bg-card/50">
                <div className="flex items-center gap-4">
                  <Avatar className="w-12 h-12">
                    <AvatarImage src={app.logo || "/placeholder.svg"} alt={app.company} />
                    <AvatarFallback>
                      <Building2 className="w-6 h-6" />
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="font-semibold">{app.position}</h4>
                    <p className="text-sm text-muted-foreground">{app.company}</p>
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
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Jump into your most used features</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-transparent" variant="outline">
              <Search className="w-4 h-4 mr-2" />
              Find New Jobs
            </Button>
            <Button className="w-full justify-start bg-transparent" variant="outline">
              <Upload className="w-4 h-4 mr-2" />
              Upload Resume
            </Button>
            <Button className="w-full justify-start bg-transparent" variant="outline">
              <CheckCircle className="w-4 h-4 mr-2" />
              Check ATS Score
            </Button>
            <Button className="w-full justify-start bg-transparent" variant="outline">
              <Clock className="w-4 h-4 mr-2" />
              View Applications
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Progress Section */}
      <Card>
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
    </div>
  )
}
