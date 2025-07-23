import { createBrowserClient } from '@supabase/ssr';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://gbmkiycdhysljzmvrenm.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdibWtpeWNkaHlzbGp6bXZyZW5tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5MDM3MzcsImV4cCI6MjA2ODQ3OTczN30.biCOX2vi6KLKzQfk9zQdyuPax3X0pPpDkYOHgLq5ZNo';

export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);