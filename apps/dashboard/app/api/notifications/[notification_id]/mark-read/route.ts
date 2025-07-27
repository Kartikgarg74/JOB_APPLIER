import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';

export async function POST(request: Request, { params }: { params: { notification_id: string } }) {
  const session = await getServerSession();

  if (!session) {
    return new NextResponse(JSON.stringify({ message: 'Unauthorized' }), { status: 401 });
  }

  const { notification_id } = params;

  try {
    const backendUrl = process.env.NEXT_PUBLIC_USER_SERVICE_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/v1/notifications/${notification_id}/mark-read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return new NextResponse(JSON.stringify({ message: errorData.detail || 'Failed to mark notification as read from backend' }), { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Error marking notification ${notification_id} as read:`, error);
    return new NextResponse(JSON.stringify({ message: 'Internal server error' }), { status: 500 });
  }
}
