import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function POST(request: Request) {
  try {
    const updatedResumeData = await request.json();
    const filePath = path.join(
      process.cwd(),
      "packages",
      "config",
      "user_resume.json",
    );

    // In a real application, you would validate the data and potentially store it in a database.
    // For this example, we're just overwriting the JSON file.
    await fs.writeFile(filePath, JSON.stringify(updatedResumeData, null, 2));

    return NextResponse.json({ message: "Resume updated successfully" });
  } catch (error) {
    console.error("Error updating resume:", error);
    return NextResponse.json(
      { message: "Failed to update resume" },
      { status: 500 },
    );
  }
}
