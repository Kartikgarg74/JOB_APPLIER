'use client';

import Link from "next/link";
import { useAuthorization } from "./hooks/useAuthorization";
import { supabase } from "../lib/supabase";

export default function AuthNav() {
  const { isAuthenticated, isLoading } = useAuthorization();

  const handleGoogleSignIn = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${location.origin}/api/auth/callback`,
      },
    });
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  if (isLoading) {
    return null; // Or a loading spinner
  }

  return (
    <nav className="bg-blue-600 p-4 text-white shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold">
          Job Applier Dashboard
        </Link>
        <ul className="flex space-x-4">
          {isAuthenticated ? (
            <>
              <li>
                <Link href="/" className="hover:underline">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/jobs" className="hover:underline">
                  Job Listings
                </Link>
              </li>
              <li>
                <Link href="/recommendations" className="hover:underline">
                  Recommendations
                </Link>
              </li>
              <li>
                <Link href="/application-status" className="hover:underline">
                  Application Status
                </Link>
              </li>
              <li>
                <Link href="/profile" className="hover:underline">
                  Profile
                </Link>
              </li>
              <li>
                <button
                  onClick={handleSignOut}
                  className="hover:underline bg-red-500 px-3 py-1 rounded"
                >
                  Sign Out
                </button>
              </li>
            </>
          ) : (
            <li>
              <button
                onClick={handleGoogleSignIn}
                className="hover:underline bg-green-500 px-3 py-1 rounded"
              >
                Sign In with Google
              </button>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
}