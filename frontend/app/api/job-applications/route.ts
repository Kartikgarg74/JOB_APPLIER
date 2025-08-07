import { NextResponse } from 'next/server';
import { fetchApplications } from '@/lib/applications';

export async function GET(request: Request) {
  try {
    // In a real application, you would get the user ID from the session or authentication context.
    // For now, we'll use a placeholder or a default.
    const userId = 1; // Placeholder user ID
    const applications = await fetchApplications(userId);
    return NextResponse.json(applications);
  } catch (error) {
    console.error('Error fetching job applications:', error);
    return NextResponse.json({ message: 'Failed to fetch job applications', error: (error as Error).message }, { status: 500 });
  }
}