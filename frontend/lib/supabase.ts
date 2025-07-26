import { createBrowserClient } from '@supabase/ssr';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://gbmkiycdhysljzmvrenm.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdibWtpeWNkaHlzbGp6bXZyZW5tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5MDM3MzcsImV4cCI6MjA2ODQ3OTczN30.biCOX2vi6KLKzQfk9zQdyuPax3X0pPpDkYOHgLq5ZNo';

export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);

// Helper functions for application data
export async function getApplications() {
  const { data, error } = await supabase
    .from('applications')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw error;
  return data || [];
}

export async function createApplication(application: any) {
  const { data, error } = await supabase
    .from('applications')
    .insert([application])
    .select();

  if (error) throw error;
  return data?.[0];
}

export async function updateApplication(id: number, updates: any) {
  const { data, error } = await supabase
    .from('applications')
    .update(updates)
    .eq('id', id)
    .select();

  if (error) throw error;
  return data?.[0];
}

export async function deleteApplication(id: number) {
  const { error } = await supabase
    .from('applications')
    .delete()
    .eq('id', id);

  if (error) throw error;
}
