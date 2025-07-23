"use client"

import { useState } from "react"
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

export function JobDiscovery() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedLocation, setSelectedLocation] = useState("")
  const [selectedType, setSelectedType] = useState("")
  const [showFilters, setShowFilters] = useState(false)

  const getMatchColor = (match: number) => {
    if (match >= 90) return "text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200"
    if (match >= 80) return "text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-200"
    if (match >= 70) return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200"
    return "text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Job Discovery</h1>
        <p className="text-muted-foreground">Find your perfect job match with AI-powered recommendations</p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search jobs, companies, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                <SelectTrigger className="w-48">
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
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Job Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full-time">Full-time</SelectItem>
                  <SelectItem value="part-time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" onClick={() => setShowFilters(!showFilters)} className="px-3">
                <Filter className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <>
              <Separator className="my-4" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Salary Range</label>
                  <Select>
                    <SelectTrigger>
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
                    <SelectTrigger>
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
                    <SelectTrigger>
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
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          Found <span className="font-semibold text-foreground">247 jobs</span> matching your criteria
        </p>
        <Select defaultValue="match">
          <SelectTrigger className="w-48">
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
      <div className="grid gap-4">
        {mockJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex gap-4 flex-1">
                  <Avatar className="w-12 h-12">
                    <AvatarImage src={job.logo || "/placeholder.svg"} alt={job.company} />
                    <AvatarFallback>
                      <Building2 className="w-6 h-6" />
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-lg mb-1">{job.title}</h3>
                        <p className="text-muted-foreground font-medium">{job.company}</p>
                      </div>
                      <Badge className={`ml-4 ${getMatchColor(job.match)}`}>{job.match}% Match</Badge>
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

                <div className="flex flex-col gap-2 ml-4">
                  {job.applied ? (
                    <Button disabled className="bg-green-100 text-green-800 hover:bg-green-100">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Applied
                    </Button>
                  ) : (
                    <Button className="bg-primary hover:bg-primary/90">Apply Now</Button>
                  )}
                  <Button variant="outline" size="sm">
                    <Star className="w-4 h-4 mr-2" />
                    Save
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Load More */}
      <div className="text-center">
        <Button variant="outline" size="lg">
          Load More Jobs
        </Button>
      </div>
    </div>
  )
}
