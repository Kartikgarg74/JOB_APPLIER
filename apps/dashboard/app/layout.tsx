import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import SessionWrapper from "./SessionWrapper";
import { useEffect } from "react";
import AuthNav from "./AuthNav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Job Applier Agent Dashboard",
  description: "User-friendly dashboard for Job Applier Agent",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-100`}>
        <SessionWrapper>
          <AuthNav />
          <nav className="bg-gray-800 p-4">
            <ul className="flex space-x-4">
              <li>
                <Link href="/" className="text-white hover:text-gray-300">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/profile" className="text-white hover:text-gray-300">
                  Profile
                </Link>
              </li>
              <li>
                <Link href="/jobs" className="text-white hover:text-gray-300">
                  Jobs
                </Link>
              </li>
              <li>
                <Link href="/notifications" className="text-white hover:text-gray-300">
                  Notifications
                </Link>
              </li>
            </ul>
          </nav>
          <div className="container mx-auto p-4">{children}</div>
        </SessionWrapper>
      </body>
    </html>
  );
}
