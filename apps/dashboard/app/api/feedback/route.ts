import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(req: NextRequest) {
  const { value, comment } = await req.json();
  const feedback = {
    value,
    comment,
    timestamp: new Date().toISOString(),
  };
  const feedbackPath = path.join(process.cwd(), 'output', 'onboarding_feedback.json');
  let feedbacks: any[] = [];
  try {
    if (fs.existsSync(feedbackPath)) {
      const raw = fs.readFileSync(feedbackPath, 'utf-8');
      feedbacks = JSON.parse(raw);
    }
  } catch (e) {
    feedbacks = [];
  }
  feedbacks.push(feedback);
  fs.writeFileSync(feedbackPath, JSON.stringify(feedbacks, null, 2));
  return NextResponse.json({ status: 'ok' });
}
