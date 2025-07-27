"use client"

import React, { useEffect, useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import {
  User,
  Mail,
  Phone,
  MapPin,
  Globe,
  Linkedin,
  Github,
  Briefcase,
  GraduationCap,
  Award,
  Save,
  Edit3,
  X,
  Plus,
  Trash2
} from "lucide-react"
import { useApiServices } from '@/lib/api-context'

interface UserProfile {
  phone?: string;
  address?: string;
  portfolio_url?: string;
  personal_website?: string;
  linkedin_profile?: string;
  github_profile?: string;
  years_of_experience?: number;
  skills?: any[];
  onboarding_complete?: boolean;
  onboarding_step?: string;
  job_preferences?: any;
}

interface Education {
  id?: number;
  degree: string;
  university: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  description?: string;
}

interface Experience {
  id?: number;
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date?: string;
  description?: string;
}

interface Skill {
  id?: number;
  name: string;
  proficiency?: string;
  technologies?: string;
  url?: string;
}

export function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [education, setEducation] = useState<Education[]>([])
  const [experience, setExperience] = useState<Experience[]>([])
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [editMode, setEditMode] = useState(false)
  const [saving, setSaving] = useState(false)

  const { getUserProfile, updateUserProfile, getEducation, createEducation, getExperience, createExperience, getSkills, createSkill } = useApiServices()

  const loadProfileData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Load profile data
      const profileData = await getUserProfile()
      setProfile(profileData)

      // Load education data
      try {
        const educationData = await getEducation()
        setEducation(educationData)
      } catch (err) {
        console.warn("Failed to load education:", err)
        setEducation([])
      }

      // Load experience data
      try {
        const experienceData = await getExperience()
        setExperience(experienceData)
      } catch (err) {
        console.warn("Failed to load experience:", err)
        setExperience([])
      }

      // Load skills data
      try {
        const skillsData = await getSkills()
        setSkills(skillsData)
      } catch (err) {
        console.warn("Failed to load skills:", err)
        setSkills([])
      }

    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to load profile data")
      } else {
        setError("An unknown error occurred")
      }
    } finally {
      setLoading(false)
    }
  }, [getUserProfile, getEducation, getExperience, getSkills])

  useEffect(() => {
    loadProfileData()
  }, [loadProfileData])

  const handleSave = useCallback(async () => {
    if (!profile) return

    setSaving(true)
    setError(null)
    setMessage(null)

    try {
      await updateUserProfile(profile)
      setMessage("Profile updated successfully!")
      setEditMode(false)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to update profile")
      } else {
        setError("An unknown error occurred")
      }
    } finally {
      setSaving(false)
    }
  }, [profile, updateUserProfile])

  const handleProfileChange = useCallback((field: string, value: string | number) => {
    if (!profile) return
    setProfile(prev => prev ? { ...prev, [field]: value } : null)
  }, [profile])

  const handleAddEducation = useCallback(async () => {
    const newEducation: Education = {
      degree: "",
      university: "",
      field_of_study: "",
      start_date: "",
      end_date: "",
      description: ""
    }

    try {
      const created = await createEducation(newEducation)
      setEducation(prev => [...prev, created])
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to add education")
      } else {
        setError("An unknown error occurred")
      }
    }
  }, [createEducation])

  const handleAddExperience = useCallback(async () => {
    const newExperience: Experience = {
      title: "",
      company: "",
      location: "",
      start_date: "",
      end_date: "",
      description: ""
    }

    try {
      const created = await createExperience(newExperience)
      setExperience(prev => [...prev, created])
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to add experience")
      } else {
        setError("An unknown error occurred")
      }
    }
  }, [createExperience])

  const handleAddSkill = useCallback(async () => {
    const newSkill: Skill = {
      name: "",
      proficiency: "beginner",
      technologies: "",
      url: ""
    }

    try {
      const created = await createSkill(newSkill)
      setSkills(prev => [...prev, created])
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to add skill")
      } else {
        setError("An unknown error occurred")
      }
    }
  }, [createSkill])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-24" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-96 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Profile</h1>
          <p className="text-muted-foreground">Manage your professional information</p>
        </div>
        <div className="flex gap-2">
          {editMode ? (
            <>
              <Button variant="outline" onClick={() => setEditMode(false)}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? (
                  <>
                    <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </>
          ) : (
            <Button onClick={() => setEditMode(true)}>
              <Edit3 className="w-4 h-4 mr-2" />
              Edit Profile
            </Button>
          )}
        </div>
      </div>

      {/* Success Message */}
      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* Profile Content */}
      <Tabs defaultValue="personal" className="space-y-6">
        <TabsList>
          <TabsTrigger value="personal">Personal Info</TabsTrigger>
          <TabsTrigger value="experience">Experience</TabsTrigger>
          <TabsTrigger value="education">Education</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
        </TabsList>

        {/* Personal Information */}
        <TabsContent value="personal" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={profile?.phone || ""}
                    onChange={(e) => handleProfileChange("phone", e.target.value)}
                    disabled={!editMode}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={profile?.address || ""}
                    onChange={(e) => handleProfileChange("address", e.target.value)}
                    disabled={!editMode}
                    placeholder="San Francisco, CA"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="years_of_experience">Years of Experience</Label>
                  <Input
                    id="years_of_experience"
                    type="number"
                    value={profile?.years_of_experience || 0}
                    onChange={(e) => handleProfileChange("years_of_experience", parseInt(e.target.value) || 0)}
                    disabled={!editMode}
                    placeholder="5"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Online Presence</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="linkedin">LinkedIn</Label>
                    <Input
                      id="linkedin"
                      value={profile?.linkedin_profile || ""}
                      onChange={(e) => handleProfileChange("linkedin_profile", e.target.value)}
                      disabled={!editMode}
                      placeholder="linkedin.com/in/username"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="github">GitHub</Label>
                    <Input
                      id="github"
                      value={profile?.github_profile || ""}
                      onChange={(e) => handleProfileChange("github_profile", e.target.value)}
                      disabled={!editMode}
                      placeholder="github.com/username"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="portfolio">Portfolio</Label>
                    <Input
                      id="portfolio"
                      value={profile?.portfolio_url || ""}
                      onChange={(e) => handleProfileChange("portfolio_url", e.target.value)}
                      disabled={!editMode}
                      placeholder="portfolio.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="website">Personal Website</Label>
                    <Input
                      id="website"
                      value={profile?.personal_website || ""}
                      onChange={(e) => handleProfileChange("personal_website", e.target.value)}
                      disabled={!editMode}
                      placeholder="mysite.com"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Experience */}
        <TabsContent value="experience" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Work Experience
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {experience.map((exp, index) => (
                <div key={exp.id || index} className="border rounded-lg p-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`exp-title-${index}`}>Job Title</Label>
                      <Input
                        id={`exp-title-${index}`}
                        value={exp.title}
                        disabled={!editMode}
                        placeholder="Senior Software Engineer"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`exp-company-${index}`}>Company</Label>
                      <Input
                        id={`exp-company-${index}`}
                        value={exp.company}
                        disabled={!editMode}
                        placeholder="Google"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`exp-location-${index}`}>Location</Label>
                      <Input
                        id={`exp-location-${index}`}
                        value={exp.location || ""}
                        disabled={!editMode}
                        placeholder="San Francisco, CA"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`exp-dates-${index}`}>Duration</Label>
                      <Input
                        id={`exp-dates-${index}`}
                        value={`${exp.start_date} - ${exp.end_date || "Present"}`}
                        disabled={!editMode}
                        placeholder="2020 - Present"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor={`exp-description-${index}`}>Description</Label>
                    <Textarea
                      id={`exp-description-${index}`}
                      value={exp.description || ""}
                      disabled={!editMode}
                      placeholder="Describe your responsibilities and achievements..."
                      rows={3}
                    />
                  </div>
                </div>
              ))}
              {editMode && (
                <Button onClick={handleAddExperience} variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Experience
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Education */}
        <TabsContent value="education" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="w-5 h-5" />
                Education
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {education.map((edu, index) => (
                <div key={edu.id || index} className="border rounded-lg p-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`edu-degree-${index}`}>Degree</Label>
                      <Input
                        id={`edu-degree-${index}`}
                        value={edu.degree}
                        disabled={!editMode}
                        placeholder="Bachelor of Science"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`edu-university-${index}`}>University</Label>
                      <Input
                        id={`edu-university-${index}`}
                        value={edu.university}
                        disabled={!editMode}
                        placeholder="Stanford University"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`edu-field-${index}`}>Field of Study</Label>
                      <Input
                        id={`edu-field-${index}`}
                        value={edu.field_of_study}
                        disabled={!editMode}
                        placeholder="Computer Science"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`edu-dates-${index}`}>Duration</Label>
                      <Input
                        id={`edu-dates-${index}`}
                        value={`${edu.start_date} - ${edu.end_date || "Present"}`}
                        disabled={!editMode}
                        placeholder="2016 - 2020"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor={`edu-description-${index}`}>Description</Label>
                    <Textarea
                      id={`edu-description-${index}`}
                      value={edu.description || ""}
                      disabled={!editMode}
                      placeholder="Additional details about your education..."
                      rows={3}
                    />
                  </div>
                </div>
              ))}
              {editMode && (
                <Button onClick={handleAddEducation} variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Education
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Skills */}
        <TabsContent value="skills" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                Skills & Technologies
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <Badge key={skill.id || index} variant="secondary">
                    {skill.name}
                    {skill.proficiency && (
                      <span className="ml-1 text-xs">({skill.proficiency})</span>
                    )}
                  </Badge>
                ))}
              </div>
              {editMode && (
                <Button onClick={handleAddSkill} variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Skill
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
