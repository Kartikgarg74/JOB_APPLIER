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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
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
  Upload,
  FileText,
} from "lucide-react"
import { useApiServices } from '@/lib/api-context';
import { Application, fetchApplications, applyForJob, createApplicationManually } from '@/lib/applications';
import { uploadResume } from '@/lib/resume';
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

// Add Application Modal Component
function AddApplicationModal({ isOpen, onClose, onAdd }: {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (application: Omit<Application, 'id'>) => void;
}) {
  const [formData, setFormData] = useState({
    company: '',
    position: '',
    status: 'Applied' as Application['status'],
    salary: '',
    location: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onAdd({
        ...formData,
        appliedDate: new Date().toISOString(),
        atsScore: 0,
        logo: undefined
      });
      setFormData({
        company: '',
        position: '',
        status: 'Applied',
        salary: '',
        location: '',
        notes: ''
      });
      onClose();
    } catch (error) {
      console.error('Error adding application:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Application</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="company">Company</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData({...formData, company: e.target.value})}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <Input
                id="position"
                value={formData.position}
                onChange={(e) => setFormData({...formData, position: e.target.value})}
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="salary">Salary</Label>
              <Input
                id="salary"
                value={formData.salary}
                onChange={(e) => setFormData({...formData, salary: e.target.value})}
                placeholder="e.g., $50,000 - $70,000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
                placeholder="e.g., Remote, NYC"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select value={formData.status} onValueChange={(value: Application['status']) => setFormData({...formData, status: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Applied">Applied</SelectItem>
                <SelectItem value="Interview">Interview</SelectItem>
                <SelectItem value="Rejected">Rejected</SelectItem>
                <SelectItem value="Offer">Offer</SelectItem>
                <SelectItem value="On Hold">On Hold</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Any additional notes..."
            />
          </div>
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Application'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// File Upload Component
function FileUpload({ onUpload }: { onUpload: (file: File) => void }) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 text-center ${
        dragActive ? "border-purple-500 bg-purple-50" : "border-gray-300"
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <Upload className="mx-auto h-12 w-12 text-gray-400" />
      <div className="mt-4">
        <p className="text-sm text-gray-600">
          Drag and drop your resume here, or{" "}
          <button
            type="button"
            className="text-purple-600 hover:text-purple-500"
            onClick={() => inputRef.current?.click()}
          >
            browse
          </button>
        </p>
        <p className="text-xs text-gray-500 mt-1">PDF, DOC, DOCX up to 10MB</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".pdf,.doc,.docx"
        onChange={handleChange}
        aria-label="Upload resume file"
        title="Upload resume file"
      />
    </div>
  );
}

export function ApplicationsTracker() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobUrl, setJobUrl] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);

  const { fetchApplications, applyForJob, uploadResume: uploadResumeService } = useApiServices();

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
      // Refresh applications list
      const updatedApplications = await fetchApplications();
      setApplications(updatedApplications);
      setJobUrl("");
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message || "An error occurred");
      } else {
        setError("An unknown error occurred");
      }
    } finally {
      setLoading(false);
    }
  }, [jobUrl, applyForJob, fetchApplications]);

  const handleAddApplication = useCallback(async (application: Omit<Application, 'id'>) => {
    try {
      const newApp = await createApplicationManually(application);
      setApplications(prev => [newApp, ...prev]);
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message || "Failed to add application");
      } else {
        setError("Failed to add application");
      }
    }
  }, []);

  const handleFileUpload = useCallback(async (file: File) => {
    setUploadingFile(true);
    setError(null);
    try {
      await uploadResumeService(file);
      // Optionally refresh applications or show success message
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message || "Failed to upload file");
      } else {
        setError("Failed to upload file");
      }
    } finally {
      setUploadingFile(false);
    }
  }, [uploadResumeService]);

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
          <Button
            className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 w-full sm:w-auto"
            onClick={() => setShowAddModal(true)}
          >
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

        {/* File Upload Section */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Upload Resume</h3>
            <FileUpload onUpload={handleFileUpload} />
            {uploadingFile && (
              <div className="mt-4 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-sm text-gray-600 mt-2">Uploading...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Job URL Application */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Apply via Job URL</h3>
            <div className="flex gap-2">
              <Input
                placeholder="Enter job posting URL..."
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={handleApply}
                disabled={loading || !jobUrl}
                className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700"
              >
                {loading ? 'Applying...' : 'Apply'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats Cards */}
        {!loading && applications.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(stats).map(([status, count]) => (
              <Card key={status}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">{count}</p>
                      <p className="text-sm text-muted-foreground">{status}</p>
                    </div>
                    <Badge className={statusColors[status as keyof typeof statusColors]}>
                      {status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  ref={searchInputRef}
                  placeholder="Search applications..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="applied">Applied</SelectItem>
                  <SelectItem value="interview">Interview</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="offer">Offer</SelectItem>
                  <SelectItem value="on hold">On Hold</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Applications List */}
        {loading ? (
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="p-4 sm:p-6">
                  <div className="flex gap-4">
                    <Skeleton className="w-12 h-12 rounded-full" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/2" />
                      <Skeleton className="h-3 w-1/3" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid gap-4">
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
        )}

        {!loading && filteredApplications.length === 0 && (
          <Card>
            <CardContent className="p-8 sm:p-12 text-center">
              <Building2 className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No applications found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery || statusFilter !== "all"
                  ? "Try adjusting your search or filters"
                  : "Start by adding your first job application"}
              </p>
              <Button
                className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 w-full sm:w-auto"
                onClick={() => setShowAddModal(true)}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Application
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Add Application Modal */}
        <AddApplicationModal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddApplication}
        />
      </main>
    </ErrorBoundary>
  )
}
