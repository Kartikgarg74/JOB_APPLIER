"use client"

import React, { useEffect, useState, useRef } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Search, MapPin, Calendar, DollarSign, Building2, Clock, CheckCircle, Filter, Star } from "lucide-react"

const mockJobs = [
  {
    id: 1,
    title: "Senior Frontend Developer",
    company: "Google",
    location: "Mountain View, CA",
    type: "Full-time",
    salary: "$150k - $200k",
    posted: "2 days ago",
    match: 95,
    logo: "/placeholder.svg?height=48&width=48",
    description: "Build the next generation of web applications...",
    skills: ["React", "TypeScript", "Node.js"],
    applied: false,
  },
  {
    id: 2,
    title: "Full Stack Engineer",
    company: "Microsoft",
    location: "Seattle, WA",
    type: "Full-time",
    salary: "$140k - $180k",
    posted: "1 day ago",
    match: 88,
    logo: "/placeholder.svg?height=48&width=48",
    description: "Join our cloud platform team...",
    skills: ["React", "C#", "Azure"],
    applied: true,
  },
  {
    id: 3,
    title: "React Developer",
    company: "Netflix",
    location: "Los Gatos, CA",
    type: "Full-time",
    salary: "$130k - $170k",
    posted: "3 days ago",
    match: 92,
    logo: "/placeholder.svg?height=48&width=48",
    description: "Help build the streaming experience...",
    skills: ["React", "JavaScript", "GraphQL"],
    applied: false,
  },
  {
    id: 4,
    title: "Frontend Engineer",
    company: "Airbnb",
    location: "San Francisco, CA",
    type: "Full-time",
    salary: "$145k - $185k",
    posted: "5 days ago",
    match: 85,
    logo: "/placeholder.svg?height=48&width=48",
    description: "Create beautiful user experiences...",
    skills: ["React", "TypeScript", "CSS"],
    applied: false,
  },
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

export function JobDiscovery() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedLocation, setSelectedLocation] = useState("")
  const [selectedType, setSelectedType] = useState("")
  const [showFilters, setShowFilters] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Simulate async fetch
  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      // setError("Failed to fetch jobs. Please try again.")
    }, 1200)
  }, [])

  // Analytics hooks
  useEffect(() => {
    if (searchQuery) console.log("Analytics: Job search", searchQuery)
  }, [searchQuery])
  useEffect(() => {
    if (selectedLocation || selectedType) console.log("Analytics: Filter", { selectedLocation, selectedType })
  }, [selectedLocation, selectedType])

  const getMatchColor = (match: number) => {
    if (match >= 90) return "text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200"
    if (match >= 80) return "text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-200"
    if (match >= 70) return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200"
    return "text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200"
  }

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Job Discovery" tabIndex={-1} className="space-y-6 px-2 sm:px-4 md:px-0 focus:outline-none">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold mb-2">Job Discovery</h1>
          <p className="text-muted-foreground text-base sm:text-lg">Find your perfect job match with AI-powered recommendations</p>
        </div>

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

        {/* Search and Filters */}
        <Card>
          <CardContent className="p-4 sm:p-6">
            {loading ? (
              <div className="flex flex-col gap-4 lg:flex-row" aria-busy="true" aria-label="Loading filters">
                <Skeleton className="h-10 w-full lg:w-1/2" />
                <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                  <Skeleton className="h-10 w-full sm:w-48" />
                  <Skeleton className="h-10 w-full sm:w-40" />
                  <Skeleton className="h-10 w-full sm:w-24" />
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-4 lg:flex-row">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    ref={searchInputRef}
                    placeholder="Search jobs, companies, or keywords..."
                    value={searchQuery}
                    onChange={e => {
                      setSearchQuery(e.target.value)
                      console.log("Analytics: Search input", e.target.value)
                    }}
                    className="pl-10 w-full"
                    aria-label="Search jobs, companies, or keywords"
                  />
                </div>
                <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                  <Select value={selectedLocation} onValueChange={v => { setSelectedLocation(v); console.log("Analytics: Location filter", v) }}>
                    <SelectTrigger className="w-full sm:w-48" aria-label="Location filter">
                      <MapPin className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Location" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="remote">Remote</SelectItem>
                      <SelectItem value="san-francisco">San Francisco, CA</SelectItem>
                      <SelectItem value="seattle">Seattle, WA</SelectItem>
                      <SelectItem value="new-york">New York, NY</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={selectedType} onValueChange={v => { setSelectedType(v); console.log("Analytics: Job type filter", v) }}>
                    <SelectTrigger className="w-full sm:w-40" aria-label="Job type filter">
                      <SelectValue placeholder="Job Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full-time">Full-time</SelectItem>
                      <SelectItem value="part-time">Part-time</SelectItem>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={() => setShowFilters(!showFilters)} className="px-3 w-full sm:w-auto" aria-label="Show advanced filters">
                    <Filter className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}

            {/* Advanced Filters */}
            {showFilters && (
              <>
                <Separator className="my-4" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Salary Range</label>
                    <Select>
                      <SelectTrigger className="w-full">
                        <DollarSign className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Any" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="50-75">$50k - $75k</SelectItem>
                        <SelectItem value="75-100">$75k - $100k</SelectItem>
                        <SelectItem value="100-150">$100k - $150k</SelectItem>
                        <SelectItem value="150+">$150k+</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Experience Level</label>
                    <Select>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Any" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="entry">Entry Level</SelectItem>
                        <SelectItem value="mid">Mid Level</SelectItem>
                        <SelectItem value="senior">Senior Level</SelectItem>
                        <SelectItem value="lead">Lead/Principal</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Company Size</label>
                    <Select>
                      <SelectTrigger className="w-full">
                        <Building2 className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Any" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="startup">Startup (1-50)</SelectItem>
                        <SelectItem value="small">Small (51-200)</SelectItem>
                        <SelectItem value="medium">Medium (201-1000)</SelectItem>
                        <SelectItem value="large">Large (1000+)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Results Summary */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
          <p className="text-muted-foreground text-sm sm:text-base">
            Found <span className="font-semibold text-foreground">247 jobs</span> matching your criteria
          </p>
          <Select defaultValue="match">
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="match">Best Match</SelectItem>
              <SelectItem value="date">Most Recent</SelectItem>
              <SelectItem value="salary">Highest Salary</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Job Cards */}
        {loading ? (
          <div className="grid gap-4" aria-busy="true" aria-label="Loading job cards">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-40 w-full" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4">
            {mockJobs.map((job) => (
              <Card key={job.id} className="hover:shadow-md transition-shadow" tabIndex={0} aria-label={`Job card for ${job.title} at ${job.company}`}>
                <CardContent className="p-4 sm:p-6">
                  <div className="flex flex-col md:flex-row items-start justify-between gap-4 md:gap-0">
                    <div className="flex gap-4 flex-1">
                      <Avatar className="w-12 h-12">
                        <AvatarImage src={job.logo || "/placeholder.svg"} alt={job.company} />
                        <AvatarFallback>
                          <Building2 className="w-6 h-6" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-2 gap-2">
                          <div>
                            <h3 className="font-semibold text-lg mb-1">{job.title}</h3>
                            <p className="text-muted-foreground font-medium">{job.company}</p>
                          </div>
                          <Badge className={`ml-0 sm:ml-4 mt-2 sm:mt-0 ${getMatchColor(job.match)}`}>{job.match}% Match</Badge>
                        </div>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-3">
                          <div className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {job.location}
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {job.type}
                          </div>
                          <div className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4" />
                            {job.salary}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {job.posted}
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{job.description}</p>
                        <div className="flex flex-wrap gap-2 mb-4">
                          {job.skills.map((skill) => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-row md:flex-col gap-2 ml-0 md:ml-4 w-full md:w-auto">
                      {job.applied ? (
                        <Button disabled className="bg-green-100 text-green-800 hover:bg-green-100 w-full md:w-auto" aria-label="Already applied">
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Applied
                        </Button>
                      ) : (
                        <Button className="bg-primary hover:bg-primary/90 w-full md:w-auto" aria-label="Apply now" onClick={() => console.log("Analytics: Apply", job)}>
                          Apply Now
                        </Button>
                      )}
                      <Button variant="outline" size="sm" className="w-full md:w-auto" aria-label="Save job" onClick={() => console.log("Analytics: Save", job)}>
                        <Star className="w-4 h-4 mr-2" />
                        Save
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Load More */}
        <div className="text-center">
          <Button variant="outline" size="lg" className="w-full sm:w-auto">
            Load More Jobs
          </Button>
        </div>
      </main>
    </ErrorBoundary>
  )
}
