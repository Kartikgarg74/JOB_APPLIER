import { NextResponse } from 'next/server';
import fsPromises from 'fs/promises';
import path from 'path';

export async function GET() {
  const filePath = path.join(
    process.cwd(),
    'packages',
    'config',
    'user_resume.json',
  );
  try {
    const jsonData = await fsPromises.readFile(filePath, 'utf8');
    const objectData = JSON.parse(jsonData);
    return NextResponse.json(objectData);
  } catch (error) {
    console.error('Error reading user_resume.json:', error);
    return NextResponse.json(
      { error: 'Failed to load resume data' },
      { status: 500 },
    );
  }
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const resumeFile = formData.get('resume') as File;

    if (!resumeFile) {
      return NextResponse.json({ error: 'No resume file provided.' }, { status: 400 });
    }

    // Placeholder for resume processing and ATS score calculation
    // In a real application, you would send this file to an external service
    // or use a library to parse it and calculate the ATS score.
    console.log(`Received resume file: ${resumeFile.name}, size: ${resumeFile.size} bytes`);

    return NextResponse.json({ message: 'Resume uploaded successfully. ATS score and job suggestions will be processed.', fileName: resumeFile.name });
  } catch (error) {
    console.error('Error uploading resume:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
