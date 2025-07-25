import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";
import { getServerSession } from "next-auth";

export async function GET(request) {
  const session = await getServerSession();
  if (!session || !session.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const userId = session.user.id;
  const SETTINGS_PATH = path.join(process.cwd(), "packages", "config", `user_settings_${userId}.json`);
  try {
    const data = await fs.readFile(SETTINGS_PATH, "utf8");
    return NextResponse.json(JSON.parse(data));
  } catch (error) {
    // If file doesn't exist, return defaults
    return NextResponse.json({
      theme: "system",
      notifications: { email: true, push: false },
      jobPrefs: { remote: true, companySize: "any", industry: "any" },
    });
  }
}

export async function POST(request) {
  const session = await getServerSession();
  if (!session || !session.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const userId = session.user.id;
  const SETTINGS_PATH = path.join(process.cwd(), "packages", "config", `user_settings_${userId}.json`);
  try {
    const settings = await request.json();
    await fs.writeFile(SETTINGS_PATH, JSON.stringify(settings, null, 2));
    return NextResponse.json({ message: "Settings updated" });
  } catch (error) {
    return NextResponse.json({ error: "Failed to update settings" }, { status: 500 });
  }
}
