import { NextResponse } from "next/server";
import fsPromises from "fs/promises";
import path from "path";

export async function GET() {
  const filePath = path.join(
    process.cwd(),
    "packages",
    "config",
    "user_profile.json",
  );
  try {
    const jsonData = await fsPromises.readFile(filePath, "utf8");
    const objectData = JSON.parse(jsonData);
    return NextResponse.json(objectData);
  } catch (error) {
    console.error("Error reading user_profile.json:", error);
    return NextResponse.json(
      { error: "Failed to load profile data" },
      { status: 500 },
    );
  }
}
