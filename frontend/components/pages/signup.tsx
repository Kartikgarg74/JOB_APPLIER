"use client"

import React, { useState, useCallback, useRef } from "react"
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Zap,
  Sun,
  Moon,
  ArrowRight,
  CheckCircle,
  FileText,
  Upload,
  X,
  Eye,
  EyeOff,
} from "lucide-react"
import { useTheme } from "next-themes"
import { useApiServices } from '@/lib/api-context';
import { supabase } from '@/lib/supabase';
import { pwnedPassword } from 'hibp';
import { ResumeUpload } from '@/components/resume-upload';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';




const profileSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address"),
  phone: z.string().optional(),
  linkedin: z.string().optional(),
  // Add more fields as needed for skills, education, experience
});

export function SignupPage() {
  const { theme, setTheme } = useTheme()
  const [step, setStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [parsedResumeData, setParsedResumeData] = useState<any>(null); // State to store parsed resume data
  const router = useRouter();

  const { control, handleSubmit, formState: { errors }, setValue } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      linkedin: '',
    }
  });

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    agreeToTerms: false,
    agreeToMarketing: false,
  })

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleStep1Submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    const isPasswordSafe = await checkPassword(formData.password);
    if (!isPasswordSafe) {
      return;
    }
    setStep(2);
  }

  const checkPassword = async (password: string) => {
    try {
      const count = await pwnedPassword(password);
      if (count > 0) {
        setError(`This password has been exposed in a data breach ${count} times. Please choose another one.`);
        return false;
      }
      return true;
    } catch (err: any) {
      console.error("Error checking pwned password:", err);
      setError("Could not check password against known breaches. Please try again.");
      return false;
    }
  };

  const handleProfileSave = async (data: z.infer<typeof profileSchema>) => {
    setIsLoading(true);
    setError("");
    try {
      // Update user metadata in Supabase
      const { error: updateError } = await supabase.auth.updateUser({
        data: {
          first_name: data.firstName,
          last_name: data.lastName,
          phone: data.phone,
          linkedin: data.linkedin,
        },
      });

      if (updateError) {
        throw updateError;
      }

      // Optionally, send data to USER_SERVICE if needed for further processing/sync
      // For now, we assume Supabase update is sufficient for profile data.

      console.log("Profile updated successfully!");
      router.push('/dashboard'); // Redirect to dashboard after saving profile

    } catch (err: any) {
      setError(err.message || "Failed to save profile. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinalSubmit = async () => {
    setIsLoading(true)
    setError("")
    try {

      const { data, error } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            first_name: formData.firstName,
            last_name: formData.lastName,
          },
        },
      });

      if (error) {
        throw error;
      }

      if (data.user) {
        console.log("Account created successfully:", data.user);
        // If resume was uploaded, proceed to profile verification step
        if (parsedResumeData) {
          setStep(3);
        } else {
          // Otherwise, redirect to dashboard
          router.push('/dashboard');
        }
      } else if (error) {
        throw error;
      }

    } catch (err: any) {
      
      // Supabase errors often have a 'message' property
      setError(err.message || "Failed to create account. Please try again.");
    } finally {
      setIsLoading(false);
    }

  };

  const getPasswordStrength = (password: string) => {
    if (password.length === 0) return { score: 0, label: "", color: "" }
    if (password.length < 6) return { score: 25, label: "Weak", color: "text-red-500" }
    if (password.length < 8) return { score: 50, label: "Fair", color: "text-yellow-500" }
    if (password.length < 10) return { score: 75, label: "Good", color: "text-blue-500" }
    return { score: 100, label: "Strong", color: "text-green-500" }
  }

  const passwordStrength = getPasswordStrength(formData.password)

  const handleFileSelect = useCallback((file: File | null) => {
    setResumeFile(file);
    setError("");
    setParsedResumeData(null); // Clear parsed data on new file selection
  }, []);

  const handleResumeUploadSuccess = useCallback((data: any) => {
    setParsedResumeData(data);
    setError("");
    // Set form values with parsed data
    setValue('firstName', data.first_name || '');
    setValue('lastName', data.last_name || '');
    setValue('email', data.email || '');
    setValue('phone', data.phone || '');
    setValue('linkedin', data.linkedin || '');
    setStep(3); // Move to a new step for profile verification/editing
  }, [setValue]);



  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold">Join Job Applier</CardTitle>
          <CardDescription>
            {step === 1
              ? "Enter your details to create an account"
              : "Upload your resume to complete your profile"}
          </CardDescription>

          {error && (
            <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardHeader>
        <CardContent>
          {step === 1 && (
            <form onSubmit={handleStep1Submit} className="space-y-4">
              <div>
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  type="text"
                  placeholder="John"
                  value={formData.firstName}
                  onChange={(e) => handleInputChange("firstName", e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  type="text"
                  placeholder="Doe"
                  value={formData.lastName}
                  onChange={(e) => handleInputChange("lastName", e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  value={formData.email}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="********"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-1"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div>
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type={showPassword ? "text" : "password"}
                  placeholder="********"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                  required
                />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="terms"
                  checked={formData.agreeToTerms}
                  onCheckedChange={(checked) => handleInputChange("agreeToTerms", checked as boolean)}
                />
                <label
                  htmlFor="terms"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  I agree to the <a href="#" className="underline">terms and conditions</a>
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="marketing"
                  checked={formData.agreeToMarketing}
                  onCheckedChange={(checked) => handleInputChange("agreeToMarketing", checked as boolean)}
                />
                <label
                  htmlFor="marketing"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  I agree to receive marketing communications
                </label>
              </div>
              <Button type="submit" className="w-full" disabled={isLoading || !formData.agreeToTerms}>
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </form>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <ResumeUpload onFileSelect={handleFileSelect} onUploadSuccess={handleResumeUploadSuccess} />
              <Button variant="outline" onClick={() => setStep(1)} className="w-full">
                Back to Account Details
              </Button>
            </div>
          )}

          {step === 3 && parsedResumeData && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-center">Verify Your Profile</h2>
              <p className="text-center text-gray-600">Please review the extracted information from your resume. You can edit it before saving.</p>
              <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md space-y-2">
                <h3 className="text-lg font-semibold">Personal Information</h3>
                <form onSubmit={handleSubmit(handleProfileSave)} className="space-y-4">
                  <div>
                    <Label htmlFor="firstName">First Name</Label>
                    <Controller
                      name="firstName"
                      control={control}
                      render={({ field }) => <Input id="firstName" {...field} />}
                    />
                    {errors.firstName && <p className="text-red-500 text-sm">{errors.firstName.message}</p>}
                  </div>
                  <div>
                    <Label htmlFor="lastName">Last Name</Label>
                    <Controller
                      name="lastName"
                      control={control}
                      render={({ field }) => <Input id="lastName" {...field} />}
                    />
                    {errors.lastName && <p className="text-red-500 text-sm">{errors.lastName.message}</p>}
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Controller
                      name="email"
                      control={control}
                      render={({ field }) => <Input id="email" type="email" {...field} />}
                    />
                    {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone</Label>
                    <Controller
                      name="phone"
                      control={control}
                      render={({ field }) => <Input id="phone" {...field} />}
                    />
                    {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
                  </div>
                  <div>
                    <Label htmlFor="linkedin">LinkedIn Profile</Label>
                    <Controller
                      name="linkedin"
                      control={control}
                      render={({ field }) => <Input id="linkedin" {...field} />}
                    />
                    {errors.linkedin && <p className="text-red-500 text-sm">{errors.linkedin.message}</p>}
                  </div>

                  {parsedResumeData.skills && parsedResumeData.skills.length > 0 && (
                    <>
                      <h3 className="text-lg font-semibold mt-4">Skills</h3>
                      <div className="flex flex-wrap gap-2">
                        {parsedResumeData.skills.map((skill: any, index: number) => (
                          <Badge key={index} variant="secondary">{skill.name}</Badge>
                        ))}
                      </div>
                    </>
                  )}

                  {parsedResumeData.education && parsedResumeData.education.length > 0 && (
                    <>
                      <h3 className="text-lg font-semibold mt-4">Education</h3>
                      {parsedResumeData.education.map((edu: any, index: number) => (
                        <div key={index} className="border-t pt-2 mt-2">
                          <p><strong>Degree:</strong> {edu.degree}</p>
                          <p><strong>Institution:</strong> {edu.institution}</p>
                          <p><strong>Years:</strong> {edu.start_date} - {edu.end_date || 'Present'}</p>
                        </div>
                      ))}
                    </>
                  )}

                  {parsedResumeData.experience && parsedResumeData.experience.length > 0 && (
                    <>
                      <h3 className="text-lg font-semibold mt-4">Experience</h3>
                      {parsedResumeData.experience.map((exp: any, index: number) => (
                        <div key={index} className="border-t pt-2 mt-2">
                          <p><strong>Title:</strong> {exp.title}</p>
                          <p><strong>Company:</strong> {exp.company}</p>
                          <p><strong>Years:</strong> {exp.start_date} - {exp.end_date || 'Present'}</p>
                          <p className="text-sm text-gray-500">{exp.description}</p>
                        </div>
                      ))}
                    </>
                  )}
                </form>
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Saving Profile...' : 'Save Profile and Continue'}
              </Button>
              <Button variant="outline" onClick={() => setStep(2)} className="w-full mt-2">
                Re-upload Resume
              </Button>
            </div>
          )}
        </CardContent>
        <div className="mt-6 text-center text-sm">
          {step === 1 ? (
            <>Already have an account? <a href="/login" className="underline">Login</a></>
          ) : (
            <Button variant="link" onClick={() => setStep(1)} className="px-0">
              Back to details
            </Button>
          )}
        </div>

        <div className="mt-8 text-center">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
        </div>
      </Card>
    </div>
  );
}
