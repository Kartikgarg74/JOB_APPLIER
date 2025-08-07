import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { jobDescription, resumeText } = await request.json();

    if (!jobDescription || !resumeText) {
      return NextResponse.json({ error: 'Missing jobDescription or resumeText' }, { status: 400 });
    }

    const atsServiceUrl = process.env.NEXT_PUBLIC_ATS_SERVICE_URL;
    if (!atsServiceUrl) {
      throw new Error('NEXT_PUBLIC_ATS_SERVICE_URL is not defined');
    }

    const response = await fetch(`${atsServiceUrl}/v1/ats-score`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Add any necessary authentication headers here, e.g., Authorization
      },
      body: JSON.stringify({ job_description: jobDescription, resume_text: resumeText }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to calculate ATS score');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Error calculating ATS score:', error);
    return NextResponse.json({ error: error.message || 'Internal Server Error' }, { status: 500 });
  }
}