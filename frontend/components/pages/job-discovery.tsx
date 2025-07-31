"use client"

import React, { useEffect, useState, useRef, useCallback } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Search, MapPin, Calendar, DollarSign, Building2, Clock, CheckCircle, Filter, Star, Loader2, Zap } from "lucide-react"
import { useApiServices } from '@/lib/api-context';
import { cn } from '@/lib/utils';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

// Types for job data
export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  salary?: string;
  posted: string;
  match?: number;
  logo?: string;
  description: string;
  skills: string[];
  applied: boolean;
  url?: string;
  source?: string;
}



export function JobDiscovery() {
  const [searchQuery, setSearchQuery] = useState("")
  const [location, setLocation] = useState("")
  const [selectedType, setSelectedType] = useState("")
  const [salaryRange, setSalaryRange] = useState("")
  const [showFilters, setShowFilters] = useState(false)
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [totalJobs, setTotalJobs] = useState(0)
  const searchInputRef = useRef<HTMLInputElement>(null)

  const { searchJobs } = useApiServices();

  const getMatchColor = (match: number) => {
    if (match >= 90) return "text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200"
    if (match >= 80) return "text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-200"
    if (match >= 70) return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200"
    return "text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200"
  }

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      setError("Please enter a job title or keyword to search");
      return;
    }

    setSearching(true);
    setError(null);
    setJobs([]);
    setTotalJobs(0);

    try {
      const results = await searchJobs(searchQuery, location, selectedType, salaryRange);

      if (results && results.jobs) {
        setJobs(results.jobs);
        setTotalJobs(results.total || results.jobs.length);
      } else {
        setJobs([]);
        setTotalJobs(0);
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to search jobs. Please try again.");
      } else {
        setError("An unknown error occurred while searching jobs.");
      }
      setJobs([]);
      setTotalJobs(0);
    } finally {
      setSearching(false);
    }
  }, [searchQuery, location, selectedType, salaryRange, searchJobs]);

  const handleApply = useCallback(async (job: Job) => {
    try {
      // This would integrate with the job application system
      console.log("Applying to job:", job);
      // Update the job to show as applied
      setJobs(prev => prev.map(j =>
        j.id === job.id ? { ...j, applied: true } : j
      ));
    } catch (err) {
      setError("Failed to apply to job. Please try again.");
    }
  }, []);

  const handleSaveJob = useCallback(async (job: Job) => {
    try {
      console.log("Saving job:", job);
      // This would save the job to user's saved jobs
    } catch (err) {
      setError("Failed to save job. Please try again.");
    }
  }, []);

  // Load initial jobs on component mount
  useEffect(() => {
    setLoading(true);
    // Simulate initial load
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <TooltipProvider>
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
                    onChange={e => setSearchQuery(e.target.value)}
                    onKeyPress={e => e.key === 'Enter' && handleSearch()}
                    className="pl-10 w-full"
                    aria-label="Search jobs, companies, or keywords"
                  />
                </div>
                <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                  <Input
                    placeholder="Location (e.g., San Francisco, CA)"
                    value={location}
                    onChange={e => setLocation(e.target.value)}
                    className="w-full sm:w-48"
                    aria-label="Job location"
                  />
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger className="w-full sm:w-40">
                      <SelectValue placeholder="Job Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Types</SelectItem>
                      <SelectItem value="full-time">Full-time</SelectItem>
                      <SelectItem value="part-time">Part-time</SelectItem>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Salary (e.g., $80k - $120k)"
                    value={salaryRange}
                    onChange={e => setSalaryRange(e.target.value)}
                    className="w-full sm:w-48"
                    aria-label="Salary range"
                  />
                  <Button
                    variant="outline"
                    className="w-full sm:w-24 lg:hidden"
                    onClick={() => setShowFilters(!showFilters)}
                  >
                    <Filter className="h-4 w-4 mr-2" /> Filters
                  </Button>
                  <Button
                    onClick={handleSearch}
                    className="w-full sm:w-24"
                    disabled={searching}
                  >
                    {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                    <span className="ml-2">{searching ? "Searching..." : "Search"}</span>
                  </Button>
                </div>
              </div>
            )}

            {showFilters && (
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Additional filter options can go here */}
                <p className="text-sm text-muted-foreground col-span-full">More filter options coming soon!</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Job Listings */}
        <section aria-labelledby="job-listings-heading">
          <h2 id="job-listings-heading" className="text-xl font-bold mb-4">Job Listings ({totalJobs} found)</h2>

          {searching && jobs.length === 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" aria-live="polite" aria-atomic="true">
              {[...Array(6)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-4 mb-4">
                      <Skeleton className="h-12 w-12 rounded-full" />
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-[200px]" />
                        <Skeleton className="h-4 w-[150px]" />
                      </div>
                    </div>
                    <Skeleton className="h-4 w-[250px] mb-2" />
                    <Skeleton className="h-4 w-[200px] mb-4" />
                    <div className="flex flex-wrap gap-2 mb-4">
                      <Skeleton className="h-6 w-20 rounded-full" />
                      <Skeleton className="h-6 w-24 rounded-full" />
                    </div>
                    <div className="flex justify-between">
                      <Skeleton className="h-10 w-24" />
                      <Skeleton className="h-10 w-24" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!searching && jobs.length === 0 && !error && (
            <div className="text-center py-10">
              <p className="text-muted-foreground">No jobs found. Try adjusting your search criteria.</p>
            </div>
          )}

          {!searching && jobs.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {jobs.map(job => (
                <Card key={job.id} className="flex flex-col">
                  <CardContent className="p-4 flex-grow">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={job.logo} alt={`${job.company} logo`} />
                          <AvatarFallback>{job.company[0]}</AvatarFallback>
                        </Avatar>
                        <div>
                          <h3 className="text-lg font-semibold leading-tight">{job.title}</h3>
                          <p className="text-sm text-muted-foreground">{job.company}</p>
                        </div>
                      </div>
                      {job.match !== undefined && (
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Badge className={cn("text-xs font-bold", getMatchColor(job.match))}>
                              <Zap className="h-3 w-3 mr-1" /> {job.match.toFixed(0)}%
                            </Badge>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>AI Match Score: {job.match.toFixed(2)}%</p>
                          </TooltipContent>
                        </Tooltip>
                      )}
                    </div>
                    <div className="flex items-center text-sm text-muted-foreground mb-2">
                      <MapPin className="h-4 w-4 mr-1" /> {job.location}
                      <span className="mx-2">•</span>
                      <Clock className="h-4 w-4 mr-1" /> {job.type}
                      {job.salary && (
                        <>
                          <span className="mx-2">•</span>
                          <DollarSign className="h-4 w-4 mr-1" /> {job.salary}
                        </>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-3 mb-4">{job.description}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills.map((skill, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                  <div className="p-4 border-t flex justify-between items-center">
                    <Button variant="outline" size="sm" onClick={() => handleSaveJob(job)}>
                      <Star className="h-4 w-4 mr-2" /> Save
                    </Button>
                    <Button size="sm" onClick={() => handleApply(job)} disabled={job.applied}>
                      {job.applied ? <CheckCircle className="h-4 w-4 mr-2" /> : null} {job.applied ? "Applied" : "Apply Now"}
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </section>
      </main>

    </TooltipProvider>
  )
}
