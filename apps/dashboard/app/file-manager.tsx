"use client";

import React, { useRef, useState, useEffect } from "react";

export default function FileManager() {
  const [files, setFiles] = useState<{ name: string; url: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  async function fetchFiles() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/files");
      if (!res.ok) throw new Error("Failed to fetch files");
      const data = await res.json();
      setFiles(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("file", file);
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/files", {
          method: "POST",
          body: formData,
        });
        if (!res.ok) throw new Error("Failed to upload file");
        await fetchFiles();
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
  }

  async function handleDelete(name) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/files/${encodeURIComponent(name)}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete file");
      await fetchFiles();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleDownload(url, name) {
    // Just open the download link
    window.open(`/api/files/${encodeURIComponent(name)}`);
  }

  return (
    <div className="max-w-lg mx-auto p-4 bg-gray-100 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">File Manager</h2>
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        onChange={handleUpload}
        aria-label="Upload file"
      />
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded mb-4 hover:bg-blue-600 focus:outline-none focus:ring"
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
      >
        Upload File
      </button>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500 mb-2">Error: {error}</div>}
      <ul className="divide-y divide-gray-300">
        {files.map((file, idx) => (
          <li key={idx} className="py-2 flex items-center justify-between">
            <span>{file.name}</span>
            <div className="flex gap-2">
              <button
                className="text-blue-600 hover:underline focus:outline-none"
                aria-label={`Download ${file.name}`}
                onClick={() => handleDownload(file.url, file.name)}
              >
                Download
              </button>
              <button
                className="text-red-600 hover:underline focus:outline-none"
                aria-label={`Delete ${file.name}`}
                onClick={() => handleDelete(file.name)}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
