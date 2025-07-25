"use client"

import React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Zap,
  Shield,
  Target,
  TrendingUp,
  Users,
  Award,
  Lock,
  Eye,
  Database,
  CheckCircle,
  ArrowRight,
  Moon,
  Sun,
} from "lucide-react"
import { useTheme } from "next-themes"
import { Alert, AlertDescription } from "@/components/ui/alert"

const features = [
  {
    icon: Target,
    title: "AI-Powered Job Matching",
    description:
      "Our advanced algorithms analyze your skills, experience, and preferences to find the perfect job matches with 95% accuracy.",
  },
  {
    icon: Zap,
    title: "Automated Applications",
    description:
      "Apply to hundreds of jobs automatically with personalized cover letters and optimized resumes for each position.",
  },
  {
    icon: TrendingUp,
    title: "ATS Optimization",
    description:
      "Ensure your resume passes through Applicant Tracking Systems with our industry-leading optimization technology.",
  },
  {
    icon: Shield,
    title: "Privacy & Security",
    description:
      "Your data is encrypted end-to-end and never shared with third parties. We follow SOC 2 Type II compliance standards.",
  },
]

const benefits = [
  "Save 20+ hours per week on job applications",
  "Increase interview callbacks by 300%",
  "Get personalized career insights and recommendations",
  "Track all applications in one centralized dashboard",
  "Receive real-time job alerts matching your criteria",
  "Access to exclusive job opportunities from our partners",
]

const securityFeatures = [
  {
    icon: Lock,
    title: "End-to-End Encryption",
    description: "All your data is encrypted using AES-256 encryption both in transit and at rest.",
  },
  {
    icon: Eye,
    title: "Privacy by Design",
    description: "We collect only the minimum data necessary and never sell your information to third parties.",
  },
  {
    icon: Database,
    title: "Secure Infrastructure",
    description: "Our platform is hosted on enterprise-grade cloud infrastructure with 99.9% uptime.",
  },
  {
    icon: Shield,
    title: "Compliance",
    description: "We're SOC 2 Type II compliant and follow GDPR, CCPA, and other privacy regulations.",
  },
]

// ErrorBoundary component
function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [error, setError] = React.useState<Error | null>(null)
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

export function AboutPage() {
  const { theme, setTheme } = useTheme()

  // Analytics hooks for CTA
  const handleCtaClick = (action: string) => {
    console.log("Analytics: About CTA", action)
  }

  return (
    <ErrorBoundary>
      <main role="main" aria-label="About Page" tabIndex={-1} className="min-h-screen bg-background focus:outline-none">
        {/* Header */}
        <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <Link href="/welcome" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl">JobApplier.AI</span>
            </Link>

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
              About JobApplier.AI
            </Badge>

            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 bg-clip-text text-transparent">
              Revolutionizing Job Search with AI
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              JobApplier.AI is the world's first fully automated job application platform that uses advanced artificial
              intelligence to help professionals find and apply to their dream jobs effortlessly.
            </p>
          </div>
        </section>

        {/* Mission Section */}
        <section className="py-16 px-4 bg-muted/30">
          <div className="container mx-auto max-w-4xl">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Our Mission</h2>
              <p className="text-lg text-muted-foreground">
                To democratize access to career opportunities by eliminating the tedious, time-consuming aspects of job
                searching and empowering professionals to focus on what matters most - their career growth.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <Card className="text-center border-0 shadow-lg bg-card/50 backdrop-blur">
                <CardContent className="p-6">
                  <div className="w-12 h-12 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold mb-2">50,000+</h3>
                  <p className="text-sm text-muted-foreground">Professionals using our platform</p>
                </CardContent>
              </Card>

              <Card className="text-center border-0 shadow-lg bg-card/50 backdrop-blur">
                <CardContent className="p-6">
                  <div className="w-12 h-12 mx-auto mb-4 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold mb-2">12,000+</h3>
                  <p className="text-sm text-muted-foreground">Successful job placements</p>
                </CardContent>
              </Card>

              <Card className="text-center border-0 shadow-lg bg-card/50 backdrop-blur">
                <CardContent className="p-6">
                  <div className="w-12 h-12 mx-auto mb-4 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold mb-2">300%</h3>
                  <p className="text-sm text-muted-foreground">Average increase in interview callbacks</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4">
          <div className="container mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">How JobApplier.AI Works</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Our platform combines cutting-edge AI technology with deep industry expertise to transform your job search
                experience.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              {features.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <Card key={index} className="border-0 shadow-lg bg-card/50 backdrop-blur">
                    <CardContent className="p-8">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Icon className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                          <p className="text-muted-foreground">{feature.description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-20 px-4 bg-muted/30">
          <div className="container mx-auto max-w-4xl">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">Why Choose JobApplier.AI?</h2>
              <p className="text-xl text-muted-foreground">
                Join thousands of professionals who have transformed their careers with our platform
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>{benefit}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Security Section */}
        <section className="py-20 px-4">
          <div className="container mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">Security & Privacy</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Your privacy and data security are our top priorities. We implement industry-leading security measures to
                protect your information.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {securityFeatures.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <Card key={index} className="text-center border-0 shadow-lg bg-card/50 backdrop-blur">
                    <CardContent className="p-6">
                      <div className="w-12 h-12 mx-auto mb-4 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900 rounded-lg flex items-center justify-center">
                        <Icon className="w-6 h-6 text-green-600" />
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

        {/* CTA Section */}
        <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-blue-600">
          <div className="container mx-auto text-center text-white max-w-3xl">
            <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Career?</h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of professionals who are already using JobApplier.AI to land their dream jobs faster than
              ever before.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <Button size="lg" className="bg-white text-purple-600 hover:bg-gray-100 text-lg px-8" onClick={() => handleCtaClick("Start Free Trial")}>
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link href="/welcome">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white text-white hover:bg-white/10 bg-transparent text-lg px-8"
                  onClick={() => handleCtaClick("Learn More")}
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
                    <Link href="/welcome#features" className="hover:text-foreground transition-colors">
                      Features
                    </Link>
                  </div>
                  <div>
                    <Link href="/welcome#pricing" className="hover:text-foreground transition-colors">
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
