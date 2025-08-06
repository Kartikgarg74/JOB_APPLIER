'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
export default function CallbackPage() {
  const router = useRouter();

  useEffect(() => {
    // This page is primarily for handling the redirect from Supabase OAuth.
    // The actual session exchange happens in the API route.
    // We can redirect to the dashboard or a loading state here.
    router.push('/dashboard');
  }, [router]);

  return (
    <div>
      <p>Processing authentication...</p>
    </div>
  );
}