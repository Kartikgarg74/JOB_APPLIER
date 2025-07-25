import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';

export async function GET(request: Request) {
  const session = await getServerSession();

  if (!session) {
    return new NextResponse(JSON.stringify({ message: 'Unauthorized' }), { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('userId');
  const limit = searchParams.get('limit') || '10';
  const offset = searchParams.get('offset') || '0';

  if (!userId) {
    return new NextResponse(JSON.stringify({ message: 'User ID is required' }), { status: 400 });
  }

  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/v1/notifications/${userId}?limit=${limit}&offset=${offset}`);

    if (!response.ok) {
      const errorData = await response.json();
      return new NextResponse(JSON.stringify({ message: errorData.detail || 'Failed to fetch notifications from backend' }), { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching notifications:', error);
    return new NextResponse(JSON.stringify({ message: 'Internal server error' }), { status: 500 });
  }
}
