import React, { useState, useRef } from "react";
import { Upload } from "lucide-react";

// File Upload Component
export function FileUpload({ onUpload }: { onUpload: (file: File) => void }) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  };

  return (
    <div
      className={`${dragActive ? "border-purple-600 bg-purple-50" : "border-gray-300 bg-white"} border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200 ease-in-out`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={onButtonClick}
      aria-label="File upload area"
      role="button"
      tabIndex={0}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={handleChange}
        aria-label="Upload resume file"
        title="Upload resume file"
      />
      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-3" />
      <p className="mb-2 text-sm text-gray-600">
        <span className="font-semibold">Click to upload</span> or drag and drop
      </p>
      <p className="text-xs text-gray-500">PDF, DOCX, or TXT (max 5MB)</p>
    </div>
  );
}