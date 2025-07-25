import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

const FILES_DIR = path.join(process.cwd(), "output", "uploads");

export async function GET(request, { params }) {
  const { filename } = params;
  const filePath = path.join(FILES_DIR, filename);
  try {
    const file = await fs.readFile(filePath);
    return new Response(file, {
      headers: {
        "Content-Disposition": `attachment; filename=${filename}`,
        "Content-Type": "application/octet-stream",
      },
    });
  } catch (error) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }
}

export async function DELETE(request, { params }) {
  const { filename } = params;
  const filePath = path.join(FILES_DIR, filename);
  try {
    await fs.unlink(filePath);
    return NextResponse.json({ message: "File deleted" });
  } catch (error) {
    return NextResponse.json({ error: "Failed to delete file" }, { status: 500 });
  }
}
