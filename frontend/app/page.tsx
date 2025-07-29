'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createBrowserClient } from '@supabase/ssr';
import { AppLayout } from "@/components/layout/app-layout";
import { Dashboard } from "@/components/pages/dashboard";

export default function Home() {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push('/login');
      } else {
        setLoading(false);
      }
    };

    checkUser();
  }, [router, supabase]);

  if (loading) {
    return <AppLayout><div>Loading...</div></AppLayout>; // Or a more sophisticated loading component
  }

  return (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  );
}
