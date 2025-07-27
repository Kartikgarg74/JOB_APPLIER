import { NextResponse } from "next/server";

export async function GET() {
  try {
    // TODO: Replace with real DB integration
    return NextResponse.json({ message: "ATS data fetching is under development." });
  } catch (error) {
    console.error("Error fetching ATS data:", error);
    return NextResponse.json(
      { error: "Failed to fetch ATS data" },
      { status: 500 },
    );
  }
}
