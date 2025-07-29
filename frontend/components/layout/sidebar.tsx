"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Search,
  FileCheck,
  Edit3,
  Clock,
  Settings,
  Zap,
  ChevronLeft,
  ChevronRight,
  Menu as MenuIcon,
  X as CloseIcon,
  User,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Job Discovery", href: "/jobs", icon: Search },
  { name: "Job Dashboard", href: "/jobs/dashboard", icon: LayoutDashboard },
  { name: "ATS Checker", href: "/ats-checker", icon: FileCheck },
  { name: "Resume Editor", href: "/resume-editor", icon: Edit3 },
  { name: "Resume Upload", href: "/resume-upload", icon: FileCheck },
  { name: "Applications", href: "/applications", icon: Clock },
  { name: "Profile", href: "/profile", icon: User },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const pathname = usePathname()

  // Hamburger for mobile
  const Hamburger = (
    <Button
      variant="ghost"
      size="icon"
      className="fixed top-4 left-4 z-50 lg:hidden"
      aria-label={mobileOpen ? "Close sidebar" : "Open sidebar"}
      onClick={() => setMobileOpen((v) => !v)}
    >
      {mobileOpen ? <CloseIcon className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
    </Button>
  )

  return (
    <TooltipProvider>
      {Hamburger}
      {/* Sidebar overlay for mobile */}
      <div
        className={cn(
          "flex flex-col bg-card border-r border-border transition-all duration-300 z-40",
          collapsed ? "w-16" : "w-64",
          // Mobile overlay
          "fixed top-0 left-0 h-full lg:static lg:h-auto",
          mobileOpen ? "block" : "hidden lg:flex"
        )}
        aria-label="Sidebar navigation"
      >
        {/* Logo */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <div>
                <h1 className="font-bold text-lg">JobApplierAgent</h1>
                <p className="text-xs text-muted-foreground">Apply Smart. Track Better.</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            const navItem = (
              <Link href={item.href} key={item.name}>
                <Button
                  variant={isActive ? "default" : "ghost"}
                  className={cn(
                    "w-full justify-start gap-3 h-12 min-h-[44px] text-base",
                    collapsed && "justify-center px-2",
                    isActive && "bg-primary text-primary-foreground",
                  )}
                  aria-label={item.name}
                  tabIndex={0}
                  onClick={() => setMobileOpen(false)}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!collapsed && <span>{item.name}</span>}
                </Button>
              </Link>
            )

            if (collapsed) {
              return (
                <Tooltip key={item.name}>
                  <TooltipTrigger asChild>{navItem}</TooltipTrigger>
                  <TooltipContent side="right">{item.name}</TooltipContent>
                </Tooltip>
              )
            }

            return navItem
          })}
        </nav>

        {/* Collapse Toggle (desktop only) */}
        <div className="p-4 border-t border-border hidden lg:block">
          <Button variant="ghost" size="sm" onClick={() => setCollapsed(!collapsed)} className="w-full justify-center">
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </Button>
        </div>
      </div>
    </TooltipProvider>
  )
}
