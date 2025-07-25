"use client"

import React, { useState, useEffect, useRef, useMemo, useCallback } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Search,
  Calendar,
  Building2,
  DollarSign,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  MessageSquare,
  Plus,
} from "lucide-react"
import { useApiServices } from '@/lib/api-context';
import { Application } from '@/lib/applications';
import Image from 'next/image';

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

export function ApplicationsTracker() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobUrl, setJobUrl] = useState("");

  const { fetchApplications, applyForJob } = useApiServices();

  // Fetch applications from backend
  useEffect(() => {
    setLoading(true);
    fetchApplications()
      .then(setApplications)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [fetchApplications]);

  const handleApply = useCallback(async () => {
    if (!jobUrl) {
      setError("Please enter a job posting URL.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await applyForJob(jobUrl);
      // Optionally refresh applications list here
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message || "An error occurred");
      } else {
        setError("An unknown error occurred");
      }
    } finally {
      setLoading(false);
    }
  }, [jobUrl, applyForJob]);

  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [selectedApplication, setSelectedApplication] = useState<number | null>(null)
  const [viewMode, setViewMode] = useState<"grid" | "timeline">("grid")

  const filteredApplications = useMemo(() =>
    applications.filter((app) => {
      const matchesSearch =
        app.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.position.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = statusFilter === "all" || app.status.toLowerCase() === statusFilter.toLowerCase()
      return matchesSearch && matchesStatus
    }),
    [applications, searchQuery, statusFilter]
  );

  const getStatusStats = useCallback(() => {
    const stats = applications.reduce(
      (acc, app) => {
        acc[app.status] = (acc[app.status] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )
    return stats
  }, [applications]);

  const stats = useMemo(() => getStatusStats(), [getStatusStats]);

  // Restore statusColors and statusIcons for application status display
  const statusColors = {
    Applied: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    Interview: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    Rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    Offer: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
    "On Hold": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  };
  const statusIcons = {
    Applied: Clock,
    Interview: AlertCircle,
    Rejected: XCircle,
    Offer: CheckCircle,
    "On Hold": Clock,
  };

  const searchInputRef = useRef<HTMLInputElement>(null)

  // Analytics hooks
  useEffect(() => {
    if (searchQuery) console.log("Analytics: Applications search", searchQuery)
  }, [searchQuery])
  useEffect(() => {
    if (statusFilter) console.log("Analytics: Status filter", statusFilter)
  }, [statusFilter])

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Applications Tracker" tabIndex={-1} className="space-y-6 px-2 sm:px-4 md:px-0 focus:outline-none">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold mb-2">Applications Tracker</h1>
            <p className="text-muted-foreground text-base sm:text-lg">Track and manage all your job applications in one place</p>
          </div>
          <Button className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 w-full sm:w-auto">
            <Plus className="w-4 h-4 mr-2" />
            Add Application
          </Button>
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

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4" aria-label="Loading stats">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4" aria-label="Loading filters">
              <Skeleton className="h-10 w-full sm:w-1/2" />
              <Skeleton className="h-10 w-full sm:w-48" />
              <Skeleton className="h-10 w-full sm:w-40" />
            </div>
          </CardContent>
        </Card>

        {/* Applications List */}
        <div className="grid gap-4" aria-label="Loading applications">
          {filteredApplications.map((application) => {
            const StatusIcon = statusIcons[application.status as keyof typeof statusIcons]
            return (
              <Card key={application.id} className="hover:shadow-md transition-shadow" tabIndex={0} aria-label={`Application ${application.position} at ${application.company}`}>
                <CardContent className="p-4 sm:p-6">
                  <div className="flex flex-col md:flex-row items-start justify-between gap-4 md:gap-0">
                    <div className="flex gap-4 flex-1">
                      <Avatar className="w-12 h-12">
                        <Image src={application.logo || "/placeholder.svg"} alt={application.company} width={48} height={48} className="rounded-full object-cover" />
                        <AvatarFallback>
                          <Building2 className="w-6 h-6" />
                        </AvatarFallback>
                      </Avatar>

                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-2 gap-2">
                          <div>
                            <h3 className="font-semibold text-base sm:text-lg mb-1">{application.position}</h3>
                            <p className="text-xs sm:text-sm text-muted-foreground font-medium">{application.company}</p>
                          </div>
                          <Badge className={statusColors[application.status as keyof typeof statusColors]}>
                            <StatusIcon className="w-3 h-3 mr-1" />
                            {application.status}
                          </Badge>
                        </div>

                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-3">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            Applied {new Date(application.appliedDate).toLocaleDateString()}
                          </div>
                          <div className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4" />
                            {application.salary}
                          </div>
                          <div className="flex items-center gap-1">
                            <Building2 className="w-4 h-4" />
                            {application.location}
                          </div>
                          <Badge variant="outline" className="text-xs">
                            ATS: {application.atsScore}%
                          </Badge>
                        </div>

                        {application.notes && (
                          <p className="text-xs sm:text-sm text-muted-foreground mb-3 bg-muted/50 p-2 rounded">
                            <MessageSquare className="w-4 h-4 inline mr-1" />
                            {application.notes}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-row md:flex-col gap-2 ml-0 md:ml-4 w-full md:w-auto">
                      <Button variant="outline" size="sm" className="w-full md:w-auto" onClick={() => setSelectedApplication(application.id)} aria-label={`View details for ${application.position}`}>
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {filteredApplications.length === 0 && (
          <Card>
            <CardContent className="p-8 sm:p-12 text-center">
              <Building2 className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No applications found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery || statusFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "Start by adding your first job application"}
              </p>
              <Button className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 w-full sm:w-auto">
                <Plus className="w-4 h-4 mr-2" />
                Add Application
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </ErrorBoundary>
  )
}
