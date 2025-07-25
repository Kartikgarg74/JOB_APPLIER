import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

const FILES_DIR = path.join(process.cwd(), "output", "uploads");

export async function GET() {
  try {
    await fs.mkdir(FILES_DIR, { recursive: true });
    const files = await fs.readdir(FILES_DIR);
    return NextResponse.json(files.map(name => ({ name, url: `/output/uploads/${name}` })));
  } catch (error) {
    return NextResponse.json({ error: "Failed to list files" }, { status: 500 });
  }
}

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!file || typeof file === "string") {
      return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
    }
    await fs.mkdir(FILES_DIR, { recursive: true });
    const filePath = path.join(FILES_DIR, file.name);
    const arrayBuffer = await file.arrayBuffer();
    await fs.writeFile(filePath, Buffer.from(arrayBuffer));
    return NextResponse.json({ name: file.name, url: `/output/uploads/${file.name}` });
  } catch (error) {
    return NextResponse.json({ error: "Failed to upload file" }, { status: 500 });
  }
}
