"use client"

import React, { useEffect, useState, useCallback } from "react"
import { useForm, Controller, useFieldArray } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
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
  Trash2,
  Loader2
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
  skills?: Skill[];
  education?: Education[];
  experience?: Experience[];
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

const profileSchema = z.object({
  phone: z.string().optional(),
  address: z.string().optional(),
  portfolio_url: z.string().url("Invalid URL").optional().or(z.literal('')),
  personal_website: z.string().url("Invalid URL").optional().or(z.literal('')),
  linkedin_profile: z.string().url("Invalid URL").optional().or(z.literal('')),
  github_profile: z.string().url("Invalid URL").optional().or(z.literal('')),
  years_of_experience: z.preprocess(
    (val) => (val === "" ? undefined : Number(val)),
    z.number().min(0, "Cannot be negative").optional()
  ),
  skills: z.array(z.object({
    id: z.number().optional(),
    name: z.string().min(1, "Skill name is required"),
    proficiency: z.string().optional(),
    technologies: z.string().optional(),
    url: z.string().url("Invalid URL").optional().or(z.literal(''))
  })).optional(),
  onboarding_complete: z.boolean().optional(),
  onboarding_step: z.string().optional(),
  job_preferences: z.any().optional(), // Adjust as per actual job preferences structure
  education: z.array(z.object({
    id: z.number().optional(),
    degree: z.string().min(1, "Degree is required"),
    university: z.string().min(1, "University is required"),
    field_of_study: z.string().min(1, "Field of study is required"),
    start_date: z.string().min(1, "Start date is required"),
    end_date: z.string().optional(),
    description: z.string().optional(),
  })).optional(),
  experience: z.array(z.object({
    id: z.number().optional(),
    title: z.string().min(1, "Title is required"),
    company: z.string().min(1, "Company is required"),
    location: z.string().optional(),
    start_date: z.string().min(1, "Start date is required"),
    end_date: z.string().optional(),
    description: z.string().optional(),
  })).optional(),
});

export function ProfilePage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [editMode, setEditMode] = useState(false)
  const [saving, setSaving] = useState(false)
  const [education, setEducation] = useState<Education[]>([])
  const [experience, setExperience] = useState<Experience[]>([])

  const { getUserProfile, updateUserProfile, getEducation, createEducation, getExperience, createExperience, getSkills, createSkill } = useApiServices()

  const { control, handleSubmit, reset, formState: { errors } } = useForm<UserProfile>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      phone: "",
      address: "",
      portfolio_url: "",
      personal_website: "",
      linkedin_profile: "",
      github_profile: "",
      years_of_experience: undefined,
    },
  });

  const { fields: educationFields, append: appendEducation, remove: removeEducation } = useFieldArray({
    control,
    name: "education",
  });

  const { fields: experienceFields, append: appendExperience, remove: removeExperience } = useFieldArray({
    control,
    name: "experience",
  });

  const { fields: skillFields, append: appendSkill, remove: removeSkill } = useFieldArray({
    control,
    name: "skills",
  });

  const loadProfileData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const profileData = await getUserProfile()
      reset(profileData); // Populate form with fetched data

      try {
        const educationData = await getEducation()
        setEducation(educationData)
      } catch (err) {
        console.warn("Failed to load education:", err)
        setEducation([])
      }

      try {
        const experienceData = await getExperience()
        setExperience(experienceData)
      } catch (err) {
        console.warn("Failed to load experience:", err)
        setExperience([])
      }

      try {
        const skillsData = await getSkills()
        reset((prev: any) => ({
          ...prev,
          skills: skillsData,
        }));
      } catch (err) {
        console.warn("Failed to load skills:", err)
        reset((prev: any) => ({
          ...prev,
          skills: [],
        }));
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
  }, [getUserProfile, getEducation, getExperience, getSkills, reset])

  useEffect(() => {
    loadProfileData()
  }, [loadProfileData])

  const onSubmit = useCallback(async (data: UserProfile) => {
    setSaving(true)
    setError(null)
    setMessage(null)

    try {
      // Separate profile data from nested arrays for individual updates
      const { skills, education, experience, ...profileData } = data;

      // Update education
      for (const edu of education) {
        if (edu.id) {
          // await updateEducation(edu.id, edu);
        } else {
          // await createEducation(edu);
        }
      }

      // Update experience
      for (const exp of experience) {
        if (exp.id) {
          // await updateExperience(exp.id, exp);
        } else {
          // await createExperience(exp);
        }
      }

      // Update skills
      for (const skill of skills) {
        if (skill.id) {
          // await updateSkill(skill.id, skill);
        } else {
          // await createSkill(skill);
        }
      }

      await updateUserProfile(profileData);

      // TODO: Implement API calls for updating education, experience, and skills
      // For now, we'll just log them to console
      console.log("Skills to update:", skills);
      console.log("Education to update:", education);
      console.log("Experience to update:", experience);
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
  }, [updateUserProfile])

  const handleSave = useCallback(async () => {
    await handleSubmit(onSubmit)();
  }, [handleSubmit, onSubmit]);

  const handleAddEducation = useCallback(async () => {
    appendEducation({
      degree: "",
      university: "",
      field_of_study: "",
      start_date: "",
      end_date: "",
      description: ""
    });
  }, [createEducation])

  const handleAddExperience = useCallback(async () => {
    appendExperience({
      title: "",
      company: "",
      location: "",
      start_date: "",
      end_date: "",
      description: ""
    });
  }, [appendExperience])

  const handleAddSkill = useCallback(() => {
    appendSkill({
      name: "",
      proficiency: "",
      technologies: "",
      url: ""
    });
  }, [appendSkill]);



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
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
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
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Controller
                    name="phone"
                    control={control}
                    render={({ field }) => (
                      <Input
                        type="text"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Controller
                    name="address"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="address"
                        type="text"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.address && <p className="text-red-500 text-sm">{errors.address.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="portfolio_url">Portfolio URL</Label>
                  <Controller
                    name="portfolio_url"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="portfolio_url"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.portfolio_url && <p className="text-red-500 text-sm">{errors.portfolio_url.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="personal_website">Personal Website</Label>
                  <Controller
                    name="personal_website"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="personal_website"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.personal_website && <p className="text-red-500 text-sm">{errors.personal_website.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="linkedin_profile">LinkedIn Profile</Label>
                  <Controller
                    name="linkedin_profile"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="linkedin_profile"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.linkedin_profile && <p className="text-red-500 text-sm">{errors.linkedin_profile.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="github_profile">GitHub Profile</Label>
                  <Controller
                    name="github_profile"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="github_profile"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.github_profile && <p className="text-red-500 text-sm">{errors.github_profile.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="years_of_experience">Years of Experience</Label>
                  <Controller
                    name="years_of_experience"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="years_of_experience"
                        type="number"
                        {...field}
                        onChange={(e) => field.onChange(e.target.value === '' ? undefined : Number(e.target.value))}
                        disabled={!editMode || saving}
                      />
                    )}
                  {errors.years_of_experience && <p className="text-red-500 text-sm">{errors.years_of_experience.message}</p>}
                </div>
              </div>
              {editMode && (
                <Button type="submit" className="w-full" disabled={saving}>
                  {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />} 
                  {saving ? "Saving..." : "Save Profile"}
                </Button>
              )}
            </form>
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
                {experienceFields.map((field, index) => (
                  <div key={field.id} className="border rounded-lg p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.title`}>Job Title</Label>
                        <Controller
                          name={`experience.${index}.title`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.title`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Senior Software Engineer"
                            />
                          )
                      />
                      {errors.experience?.[index]?.title && <p className="text-red-500 text-sm">{errors.experience[index].title.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.company`}>Company</Label>
                        <Controller
                          name={`experience.${index}.company`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.company`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Google"
                            />
                          )}
                        />
                        {errors.experience?.[index]?.company && <p className="text-red-500 text-sm">{errors.experience[index].company.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.location`}>Location</Label>
                        <Controller
                          name={`experience.${index}.location`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.location`}
                              {...field}
                              disabled={!editMode}
                              placeholder="San Francisco, CA"
                            />
                          )}
                        />
                        {errors.experience?.[index]?.location && <p className="text-red-500 text-sm">{errors.experience[index].location.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.start_date`}>Start Date</Label>
                        <Controller
                          name={`experience.${index}.start_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.start_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.experience?.[index]?.start_date && <p className="text-red-500 text-sm">{errors.experience[index].start_date.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.end_date`}>End Date</Label>
                        <Controller
                          name={`experience.${index}.end_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.end_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.experience?.[index]?.end_date && <p className="text-red-500 text-sm">{errors.experience[index].end_date.message}</p>}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`experience.${index}.description`}>Description</Label>
                      <Controller
                        name={`experience.${index}.description`}
                        control={control}
                        render={({ field }) => (
                          <Textarea
                            id={`experience.${index}.description`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Describe your responsibilities and achievements"
                          />
                        )}
                      />
                      {errors.experience?.[index]?.description && <p className="text-red-500 text-sm">{errors.experience[index].description.message}</p>}
                    </div>
                    </div>
                    {editMode && (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => removeExperience(index)}
                        className="mt-2"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Remove Experience
                      </Button>
                    )}
                  </div>
                ))}
                {editMode && (
                  <Button type="button" onClick={handleAddExperience} className="w-full">
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
                {educationFields.map((field, index) => (
                  <div key={field.id} className="border rounded-lg p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.degree`}>Degree</Label>
                        <Controller
                          name={`education.${index}.degree`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.degree`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Bachelor of Science"
                            />
                          )}
                        />
                        {errors.education?.[index]?.degree && <p className="text-red-500 text-sm">{errors.education[index].degree.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.university`}>University</Label>
                        <Controller
                          name={`education.${index}.university`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.university`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Stanford University"
                            />
                          )}
                        />
                        {errors.education?.[index]?.university && <p className="text-red-500 text-sm">{errors.education[index].university.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.field_of_study`}>Field of Study</Label>
                        <Controller
                          name={`education.${index}.field_of_study`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.field_of_study`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Computer Science"
                            />
                          )}
                        />
                        {errors.education?.[index]?.field_of_study && <p className="text-red-500 text-sm">{errors.education[index].field_of_study.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.start_date`}>Start Date</Label>
                        <Controller
                          name={`education.${index}.start_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.start_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.education?.[index]?.start_date && <p className="text-red-500 text-sm">{errors.education[index].start_date.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.end_date`}>End Date</Label>
                        <Controller
                          name={`education.${index}.end_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.end_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.education?.[index]?.end_date && <p className="text-red-500 text-sm">{errors.education[index].end_date.message}</p>}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`education.${index}.description`}>Description</Label>
                      <Controller
                        name={`education.${index}.description`}
                        control={control}
                        render={({ field }) => (
                          <Textarea
                            id={`education.${index}.description`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Additional details about your education..."
                            rows={3}
                          />
                        )}
                      />
                      {errors.education?.[index]?.description && <p className="text-red-500 text-sm">{errors.education[index].description.message}</p>}
                    </div>
                    {editMode && (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => removeEducation(index)}
                        className="mt-2"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Remove Education
                      </Button>
                    )}
                  </div>
                ))}
                {editMode && (
                  <Button type="button" onClick={handleAddEducation} className="w-full">
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
              {skillFields.map((field, index) => (
                <div key={field.id} className="border rounded-lg p-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.name`}>Skill Name</Label>
                      <Controller
                        name={`skills.${index}.name`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.name`}
                            {...field}
                            disabled={!editMode}
                            placeholder="React, Python, etc."
                          />
                        )}
                      />
                      {errors.skills?.[index]?.name && <p className="text-red-500 text-sm">{errors.skills[index].name.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.proficiency`}>Proficiency</Label>
                      <Controller
                        name={`skills.${index}.proficiency`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.proficiency`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Beginner, Intermediate, Advanced"
                          />
                        )}
                      />
                      {errors.skills?.[index]?.proficiency && <p className="text-red-500 text-sm">{errors.skills[index].proficiency.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.technologies`}>Technologies</Label>
                      <Controller
                        name={`skills.${index}.technologies`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.technologies`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Redux, Django, AWS"
                          />
                        )}
                      />
                      {errors.skills?.[index]?.technologies && <p className="text-red-500 text-sm">{errors.skills[index].technologies.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.url`}>URL (e.g., certification)</Label>
                      <Controller
                        name={`skills.${index}.url`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.url`}
                            type="url"
                            {...field}
                            disabled={!editMode}
                            placeholder="https://example.com/certificate"
                          />
                        )}
                      />
                      {errors.skills?.[index]?.url && <p className="text-red-500 text-sm">{errors.skills[index].url.message}</p>}
                    </div>
                  </div>
                  {editMode && (
                    <Button type="button" variant="destructive" onClick={() => removeSkill(index)}>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Remove Skill
                    </Button>
                  )}
                </div>
              ))}
              {editMode && (
                <Button type="button" onClick={handleAddSkill} className="w-full">
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
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Controller
                    name="phone"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="phone"
                        type="text"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Controller
                    name="address"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="address"
                        type="text"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.address && <p className="text-red-500 text-sm">{errors.address.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="portfolio_url">Portfolio URL</Label>
                  <Controller
                    name="portfolio_url"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="portfolio_url"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.portfolio_url && <p className="text-red-500 text-sm">{errors.portfolio_url.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="personal_website">Personal Website</Label>
                  <Controller
                    name="personal_website"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="personal_website"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.personal_website && <p className="text-red-500 text-sm">{errors.personal_website.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="linkedin_profile">LinkedIn Profile</Label>
                  <Controller
                    name="linkedin_profile"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="linkedin_profile"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.linkedin_profile && <p className="text-red-500 text-sm">{errors.linkedin_profile.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="github_profile">GitHub Profile</Label>
                  <Controller
                    name="github_profile"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="github_profile"
                        type="url"
                        {...field}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.github_profile && <p className="text-red-500 text-sm">{errors.github_profile.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="years_of_experience">Years of Experience</Label>
                  <Controller
                    name="years_of_experience"
                    control={control}
                    render={({ field }) => (
                      <Input
                        id="years_of_experience"
                        type="number"
                        {...field}
                        onChange={(e) => field.onChange(e.target.value === '' ? undefined : Number(e.target.value))}
                        disabled={!editMode || saving}
                      />
                    )}
                  />
                  {errors.years_of_experience && <p className="text-red-500 text-sm">{errors.years_of_experience.message}</p>}
                </div>
              </div>
              {editMode && (
                <Button type="submit" className="w-full" disabled={saving}>
                  {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                  {saving ? "Saving..." : "Save Profile"}
                </Button>
              )}
            </form>
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
                {experienceFields.map((field, index) => (
                  <div key={field.id} className="border rounded-lg p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.title`}>Job Title</Label>
                        <Controller
                          name={`experience.${index}.title`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.title`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Senior Software Engineer"
                            />
                          )}
                        />
                      />
                      {errors.experience?.[index]?.description && <p className="text-red-500 text-sm">{errors.experience[index].description.message}</p>}
                    </div>
                    {editMode && (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => removeExperience(index)}
                        className="mt-2"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Remove Experience
                      </Button>
                    )}
                  </div>
                ))}
                {editMode && (
                  <Button type="button" onClick={handleAddExperience} className="w-full">
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
                {educationFields.map((field, index) => (
                  <div key={field.id} className="border rounded-lg p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.degree`}>Degree</Label>
                        <Controller
                          name={`education.${index}.degree`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.degree`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Bachelor of Science"
                            />
                          )}
                        />
                        {errors.education?.[index]?.degree && <p className="text-red-500 text-sm">{errors.education[index].degree.message}</p>}
                      </div>
                              disabled={!editMode}
                              placeholder="Senior Software Engineer"
                            />
                          )}
                        />
                        {errors.experience?.[index]?.title && <p className="text-red-500 text-sm">{errors.experience[index].title.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.company`}>Company</Label>
                        <Controller
                          name={`experience.${index}.company`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.company`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Google"
                            />
                          )}
                        />
                        {errors.experience?.[index]?.company && <p className="text-red-500 text-sm">{errors.experience[index].company.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.location`}>Location</Label>
                        <Controller
                          name={`experience.${index}.location`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.location`}
                              {...field}
                              disabled={!editMode}
                              placeholder="San Francisco, CA"
                            />
                          )}
                        />
                        {errors.experience?.[index]?.location && <p className="text-red-500 text-sm">{errors.experience[index].location.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.start_date`}>Start Date</Label>
                        <Controller
                          name={`experience.${index}.start_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.start_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.experience?.[index]?.start_date && <p className="text-red-500 text-sm">{errors.experience[index].start_date.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`experience.${index}.end_date`}>End Date</Label>
                        <Controller
                          name={`experience.${index}.end_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`experience.${index}.end_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.experience?.[index]?.end_date && <p className="text-red-500 text-sm">{errors.experience[index].end_date.message}</p>}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`experience.${index}.description`}>Description</Label>
                      <Controller
                        name={`experience.${index}.description`}
                        control={control}
                        render={({ field }) => (
                          <Textarea
                            id={`experience.${index}.description`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Describe your responsibilities and achievements"
                          />
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
                {educationFields.map((field, index) => (
                  <div key={field.id} className="border rounded-lg p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.degree`}>Degree</Label>
                        <Controller
                          name={`education.${index}.degree`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.degree`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Bachelor of Science"
                            />
                          )}
                        />
                        {errors.education?.[index]?.degree && <p className="text-red-500 text-sm">{errors.education[index].degree.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.university`}>University</Label>
                        <Controller
                          name={`education.${index}.university`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.university`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Stanford University"
                            />
                          )}
                        />
                        {errors.education?.[index]?.university && <p className="text-red-500 text-sm">{errors.education[index].university.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.field_of_study`}>Field of Study</Label>
                        <Controller
                          name={`education.${index}.field_of_study`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.field_of_study`}
                              {...field}
                              disabled={!editMode}
                              placeholder="Computer Science"
                            />
                          )}
                        />
                        {errors.education?.[index]?.field_of_study && <p className="text-red-500 text-sm">{errors.education[index].field_of_study.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.start_date`}>Start Date</Label>
                        <Controller
                          name={`education.${index}.start_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.start_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.education?.[index]?.start_date && <p className="text-red-500 text-sm">{errors.education[index].start_date.message}</p>}
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`education.${index}.end_date`}>End Date</Label>
                        <Controller
                          name={`education.${index}.end_date`}
                          control={control}
                          render={({ field }) => (
                            <Input
                              id={`education.${index}.end_date`}
                              type="date"
                              value={field.value ? new Date(field.value).toISOString().split('T')[0] : ''}
                              onChange={field.onChange}
                              disabled={!editMode}
                            />
                          )}
                        />
                        {errors.education?.[index]?.end_date && <p className="text-red-500 text-sm">{errors.education[index].end_date.message}</p>}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`education.${index}.description`}>Description</Label>
                      <Controller
                        name={`education.${index}.description`}
                        control={control}
                        render={({ field }) => (
                          <Textarea
                            id={`education.${index}.description`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Additional details about your education..."
                            rows={3}
                          />
                        )}
                      />
                      {errors.education?.[index]?.description && <p className="text-red-500 text-sm">{errors.education[index].description.message}</p>}
                    </div>
                    {editMode && (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => removeEducation(index)}
                        className="mt-2"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Remove Education
                      </Button>
                    )}
                  </div>
                ))}
                {editMode && (
                  <Button type="button" onClick={handleAddEducation} className="w-full">
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
              {skillFields.map((field, index) => (
                <div key={field.id} className="border rounded-lg p-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.name`}>Skill Name</Label>
                      <Controller
                        name={`skills.${index}.name`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.name`}
                            {...field}
                            disabled={!editMode}
                            placeholder="React, Python, etc."
                          />
                        )}
                      />
                      {errors.skills?.[index]?.name && <p className="text-red-500 text-sm">{errors.skills[index].name.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.proficiency`}>Proficiency</Label>
                      <Controller
                        name={`skills.${index}.proficiency`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.proficiency`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Beginner, Intermediate, Advanced"
                          />
                        )}
                      />
                      {errors.skills?.[index]?.proficiency && <p className="text-red-500 text-sm">{errors.skills[index].proficiency.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.technologies`}>Technologies</Label>
                      <Controller
                        name={`skills.${index}.technologies`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.technologies`}
                            {...field}
                            disabled={!editMode}
                            placeholder="Redux, Django, AWS"
                          />
                        )}
                      />
                      {errors.skills?.[index]?.technologies && <p className="text-red-500 text-sm">{errors.skills[index].technologies.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`skills.${index}.url`}>URL (e.g., certification)</Label>
                      <Controller
                        name={`skills.${index}.url`}
                        control={control}
                        render={({ field }) => (
                          <Input
                            id={`skills.${index}.url`}
                            type="url"
                            {...field}
                            disabled={!editMode}
                            placeholder="https://example.com/certificate"
                          />
                        )}
                      />
                      {errors.skills?.[index]?.url && <p className="text-red-500 text-sm">{errors.skills[index].url.message}</p>}
                    </div>
                  </div>
                  {editMode && (
                    <Button type="button" variant="destructive" onClick={() => removeSkill(index)}>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Remove Skill
                    </Button>
                  )}
                </div>
              ))}
              {editMode && (
                <Button type="button" onClick={handleAddSkill} className="w-full">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Skill
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </div>
  )
}
