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
                    onClick={() => setShowFilters(!showFilters)}
                    aria-expanded={showFilters}
                    aria-controls="advanced-filters"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Filters
                  </Button>
                  <Button onClick={handleSearch} className="w-full sm:w-24">
                    <Search className="w-4 h-4 mr-2" />
                    Search
                  </Button>
                </div>
              </div>
            )}

            {showFilters && (
              <div id="advanced-filters" className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* More advanced filters can go here */}
                <Input placeholder="Experience Level" aria-label="Experience Level" />
                <Input placeholder="Company Size" aria-label="Company Size" />
                <Input placeholder="Remote/On-site" aria-label="Remote or On-site" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Job Listings */}
        <div className="grid gap-4">
          {searching ? (
            Array.from({ length: 5 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-4">
                    <Skeleton className="h-12 w-12 rounded-full" />
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-[250px]" />
                      <Skeleton className="h-4 w-[200px]" />
                    </div>
                  </div>
                  <Skeleton className="h-4 w-full mt-4" />
                  <Skeleton className="h-4 w-full mt-2" />
                  <div className="flex justify-end mt-4 space-x-2">
                    <Skeleton className="h-10 w-24" />
                    <Skeleton className="h-10 w-24" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : jobs.length > 0 ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">Showing {jobs.length} of {totalJobs} jobs</p>
              {jobs.map((job) => (
                <Card key={job.id} className="relative">
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-4">
                      <Avatar className="w-12 h-12">
                        <AvatarImage src={job.logo} alt={`${job.company} logo`} />
                        <AvatarFallback>{job.company.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <h2 className="text-lg font-semibold leading-tight">{job.title}</h2>
                        <p className="text-sm text-muted-foreground">{job.company} &bull; {job.location}</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          <Badge variant="secondary" className="flex items-center gap-1"><Clock className="w-3 h-3" /> {job.type}</Badge>
                          {job.salary && <Badge variant="secondary" className="flex items-center gap-1"><DollarSign className="w-3 h-3" /> {job.salary}</Badge>}
                          <Badge variant="secondary" className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {job.posted}</Badge>
                          {job.source && <Badge variant="secondary" className="flex items-center gap-1"><Building2 className="w-3 h-3" /> {job.source}</Badge>}
                        </div>
                        <div className="mt-3 text-sm text-gray-700 dark:text-gray-300 line-clamp-3">
                          {job.description}
                        </div>
                        {job.skills && job.skills.length > 0 && (
                          <div className="mt-3">
                            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Skills:</p>
                            <div className="flex flex-wrap gap-2">
                              {job.skills.map((skill, idx) => (
                                <Badge key={idx} variant="outline">{skill}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      {job.match !== undefined && ( // Only show match score if available
                        <div className="flex flex-col items-end">
                          <Badge className={cn("text-sm font-bold", getMatchColor(job.match))}>
                            {job.match.toFixed(1)}% Match
                          </Badge>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Star className="w-4 h-4 text-yellow-500 fill-yellow-500 mt-1 cursor-help" />
                            </TooltipTrigger>
                            <TooltipContent>AI Match Score</TooltipContent>
                          </Tooltip>
                        </div>
                      )}
                    </div>
                    <div className="flex justify-end gap-2 mt-4">
                      {job.applied ? (
                        <Button variant="outline" disabled className="flex items-center gap-1">
                          <CheckCircle className="w-4 h-4" /> Applied
                        </Button>
                      ) : (
                        <Button onClick={() => handleApply(job)} className="flex items-center gap-1">
                          <Zap className="w-4 h-4" /> Apply Now
                        </Button>
                      )}
                      <Button variant="secondary" onClick={() => handleSaveJob(job)}>
                        Save Job
                      </Button>
                      {job.url && (
                        <Button variant="outline" asChild>
                          <a href={job.url} target="_blank" rel="noopener noreferrer">
                            View Original
                          </a>
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : ( !searching &&
            <div className="text-center py-10">
              <p className="text-muted-foreground">No jobs found. Try adjusting your search or filters.</p>
            </div>
          )}
        </div>
      </main>
    </TooltipProvider>
    </ErrorBoundary>
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
                  <Button
                    onClick={handleSearch}
                    disabled={searching || !searchQuery.trim()}
                    className="px-3 w-full sm:w-auto"
                    aria-label="Search jobs"
                  >
                    {searching ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Search
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowFilters(!showFilters)}
                    className="px-3 w-full sm:w-auto"
                    aria-label="Show advanced filters"
                  >
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
            {searching ? (
              "Searching for jobs..."
            ) : jobs.length > 0 ? (
              <>
                Found <span className="font-semibold text-foreground">{totalJobs} jobs</span> matching your criteria
              </>
            ) : searchQuery ? (
              "No jobs found matching your criteria"
            ) : (
              "Enter a job title or keyword to start searching"
            )}
          </p>
          {jobs.length > 0 && (
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
          )}
        </div>

        {/* Job Cards */}
        {searching ? (
          <div className="grid gap-4" aria-busy="true" aria-label="Searching for jobs">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-40 w-full" />
            ))}
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid gap-4">
            {jobs.map((job) => (
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
                          {job.match && (
                            <Badge className={`ml-0 sm:ml-4 mt-2 sm:mt-0 ${getMatchColor(job.match)}`}>
                              {job.match}% Match
                            </Badge>
                          )}
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
                          {job.salary && (
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              {job.salary}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {job.posted}
                          </div>
                          {job.source && (
                            <div className="flex items-center gap-1">
                              <Building2 className="w-4 h-4" />
                              {job.source}
                            </div>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{job.description}</p>
                        {job.skills && job.skills.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-4">
                            {job.skills.map((skill) => (
                              <Badge key={skill} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-row md:flex-col gap-2 ml-0 md:ml-4 w-full md:w-auto">
                      {job.applied ? (
                        <Button disabled className="bg-green-100 text-green-800 hover:bg-green-100 w-full md:w-auto" aria-label="Already applied">
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Applied
                        </Button>
                      ) : (
                        <Button
                          className="bg-primary hover:bg-primary/90 w-full md:w-auto"
                          aria-label="Apply now"
                          onClick={() => handleApply(job)}
                        >
                          Apply Now
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full md:w-auto"
                        aria-label="Save job"
                        onClick={() => handleSaveJob(job)}
                      >
                        <Star className="w-4 h-4 mr-2" />
                        Save
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : !searching && searchQuery ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No jobs found</h3>
              <p className="text-muted-foreground mb-4">
                Try adjusting your search criteria or location
              </p>
              <Button onClick={() => setSearchQuery("")} variant="outline">
                Clear Search
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-8 text-center">
              <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">Start your job search</h3>
              <p className="text-muted-foreground mb-4">
                Enter a job title, company, or keyword to find opportunities
              </p>
            </CardContent>
          </Card>
        )}

        {/* Load More */}
        {jobs.length > 0 && (
          <div className="text-center">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Load More Jobs
            </Button>
          </div>
        )}
      </main>
    </ErrorBoundary>
  )
}
