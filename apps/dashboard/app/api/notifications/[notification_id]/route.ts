import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';

export async function DELETE(request: Request, { params }: { params: { notification_id: string } }) {
  const session = await getServerSession(authOptions);

  if (!session) {
    return new NextResponse(JSON.stringify({ message: 'Unauthorized' }), { status: 401 });
  }

  const { notification_id } = params;

  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/v1/notifications/${notification_id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      return new NextResponse(JSON.stringify({ message: errorData.detail || 'Failed to delete notification from backend' }), { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Error deleting notification ${notification_id}:`, error);
    return new NextResponse(JSON.stringify({ message: 'Internal server error' }), { status: 500 });
  }
}