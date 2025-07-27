import { NextResponse } from "next/server";

export async function GET() {
  // TODO: Replace with real DB integration
  const jobs = [];
  return NextResponse.json(jobs);
}
