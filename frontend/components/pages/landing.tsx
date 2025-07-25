"use client"

import React, { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Zap, Target, TrendingUp, Shield, Star, ArrowRight, Play, Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Alert, AlertDescription } from "@/components/ui/alert"

const features = [
  {
    icon: Target,
    title: "Smart Job Matching",
    description: "AI-powered algorithm finds jobs that perfectly match your skills and experience",
    color: "text-blue-600",
  },
  {
    icon: Zap,
    title: "Auto-Apply Technology",
    description: "Apply to hundreds of jobs automatically with personalized cover letters",
    color: "text-purple-600",
  },
  {
    icon: TrendingUp,
    title: "ATS Optimization",
    description: "Ensure your resume passes through ATS systems with 95% success rate",
    color: "text-green-600",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description: "Your data is encrypted and secure. We never share your information",
    color: "text-orange-600",
  },
]

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Software Engineer",
    company: "Google",
    image: "/placeholder.svg?height=40&width=40",
    content: "JobApplier.AI helped me land my dream job at Google. The ATS optimization was game-changing!",
    rating: 5,
  },
  {
    name: "Michael Rodriguez",
    role: "Product Manager",
    company: "Microsoft",
    image: "/placeholder.svg?height=40&width=40",
    content: "I got 3x more interviews after using their resume optimization. Highly recommend!",
    rating: 5,
  },
  {
    name: "Emily Johnson",
    role: "Data Scientist",
    company: "Netflix",
    image: "/placeholder.svg?height=40&width=40",
    content: "The auto-apply feature saved me 20+ hours per week. Amazing platform!",
    rating: 5,
  },
]

const stats = [
  { number: "50K+", label: "Jobs Applied" },
  { number: "12K+", label: "Users Hired" },
  { number: "95%", label: "ATS Success Rate" },
  { number: "4.9/5", label: "User Rating" },
]

const partners = ["Google", "Microsoft", "Apple", "Amazon", "Netflix", "Meta"]

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

export function LandingPage() {
  const { theme, setTheme } = useTheme()
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  // Analytics hooks
  const handleDemoClick = () => {
    setIsVideoPlaying(true)
    console.log("Analytics: Demo video clicked")
  }

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Landing Page" tabIndex={-1} className="min-h-screen bg-background focus:outline-none">
        {/* Header */}
        <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl">JobApplier.AI</span>
            </div>

            <nav className="hidden md:flex items-center gap-8">
              <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
                Features
              </Link>
              <Link href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">
                Testimonials
              </Link>
              <Link href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </Link>
              <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">
                About
              </Link>
            </nav>

            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
                <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              </Button>
              <Link href="/login">
                <Button variant="ghost">Login</Button>
              </Link>
              <Link href="/signup">
                <Button className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="py-20 px-4">
          <div className="container mx-auto text-center max-w-4xl">
            <Badge className="mb-6 bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
              🚀 Now with AI-Powered Resume Optimization
            </Badge>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 bg-clip-text text-transparent">
              Apply Smart.
              <br />
              Track Better.
              <br />
              Get Hired.
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Automate your entire job application pipeline with AI. From discovering relevant jobs to optimizing your
              resume for ATS systems.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link href="/signup">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 text-lg px-8"
                >
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 bg-transparent"
                onClick={handleDemoClick}
              >
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-primary mb-2">{stat.number}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Hero Image/Video Placeholder */}
            <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900">
              <div className="aspect-video flex items-center justify-center">
                <div className="text-center">
                  <div className="w-20 h-20 mx-auto mb-4 bg-white/20 rounded-full flex items-center justify-center">
                    <Play className="w-8 h-8 text-white" />
                  </div>
                  <p className="text-white/80">Product Demo Video</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 px-4 bg-muted/30">
          <div className="container mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Everything you need to streamline your job search and land your dream role
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <Card
                    key={index}
                    className="border-0 shadow-lg hover:shadow-xl transition-shadow bg-card/50 backdrop-blur"
                  >
                    <CardContent className="p-6 text-center">
                      <div
                        className={`w-12 h-12 mx-auto mb-4 rounded-lg bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 flex items-center justify-center`}
                      >
                        <Icon className={`w-6 h-6 ${feature.color}`} />
                      </div>
                      <h3 className="font-semibold mb-2">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 px-4">
          <div className="container mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">How It Works</h2>
              <p className="text-xl text-muted-foreground">Get hired in 3 simple steps</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  step: "01",
                  title: "Upload Your Resume",
                  description: "Upload your resume and let our AI analyze and optimize it for ATS systems",
                },
                {
                  step: "02",
                  title: "Set Your Preferences",
                  description: "Tell us what kind of jobs you're looking for and we'll find the perfect matches",
                },
                {
                  step: "03",
                  title: "Auto-Apply & Track",
                  description: "Sit back while we apply to jobs for you and track all your applications",
                },
              ].map((item, index) => (
                <div key={index} className="text-center">
                  <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-semibold mb-4">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="py-20 px-4 bg-muted/30">
          <div className="container mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">What Our Users Say</h2>
              <p className="text-xl text-muted-foreground">Join thousands of professionals who found their dream jobs</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <Card key={index} className="border-0 shadow-lg bg-card/50 backdrop-blur">
                  <CardContent className="p-6">
                    <div className="flex items-center mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                    <p className="text-muted-foreground mb-6">"{testimonial.content}"</p>
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src={testimonial.image || "/placeholder.svg"} alt={testimonial.name} />
                        <AvatarFallback>
                          {testimonial.name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-semibold">{testimonial.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {testimonial.role} at {testimonial.company}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Trusted By */}
        <section className="py-16 px-4">
          <div className="container mx-auto text-center">
            <p className="text-muted-foreground mb-8">Trusted by professionals at</p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              {partners.map((partner, index) => (
                <div key={index} className="text-2xl font-bold text-muted-foreground">
                  {partner}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-blue-600">
          <div className="container mx-auto text-center text-white">
            <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Job Search?</h2>
            <p className="text-xl mb-8 opacity-90">Join thousands of professionals who are already using JobApplier.AI</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <Button size="lg" className="bg-white text-purple-600 hover:bg-gray-100 text-lg px-8">
                  Start Free Trial
                </Button>
              </Link>
              <Link href="/about">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white text-white hover:bg-white/10 text-lg px-8 bg-transparent"
                >
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 px-4 border-t border-border">
          <div className="container mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-bold text-xl">JobApplier.AI</span>
                </div>
                <p className="text-muted-foreground">Apply Smart. Track Better. Get Hired.</p>
              </div>

              <div>
                <h4 className="font-semibold mb-4">Product</h4>
                <div className="space-y-2 text-muted-foreground">
                  <div>
                    <Link href="#features" className="hover:text-foreground transition-colors">
                      Features
                    </Link>
                  </div>
                  <div>
                    <Link href="#pricing" className="hover:text-foreground transition-colors">
                      Pricing
                    </Link>
                  </div>
                  <div>
                    <Link href="/about" className="hover:text-foreground transition-colors">
                      About
                    </Link>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-4">Support</h4>
                <div className="space-y-2 text-muted-foreground">
                  <div>
                    <Link href="/help" className="hover:text-foreground transition-colors">
                      Help Center
                    </Link>
                  </div>
                  <div>
                    <Link href="/contact" className="hover:text-foreground transition-colors">
                      Contact
                    </Link>
                  </div>
                  <div>
                    <Link href="/status" className="hover:text-foreground transition-colors">
                      Status
                    </Link>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-4">Legal</h4>
                <div className="space-y-2 text-muted-foreground">
                  <div>
                    <Link href="/privacy" className="hover:text-foreground transition-colors">
                      Privacy Policy
                    </Link>
                  </div>
                  <div>
                    <Link href="/terms" className="hover:text-foreground transition-colors">
                      Terms of Service
                    </Link>
                  </div>
                  <div>
                    <Link href="/security" className="hover:text-foreground transition-colors">
                      Security
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-t border-border mt-8 pt-8 text-center text-muted-foreground">
              <p>&copy; 2024 JobApplier.AI. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </main>
    </ErrorBoundary>
  )
}
