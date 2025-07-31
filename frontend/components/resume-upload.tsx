"use client"

import React, { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { FileText, Upload, X } from "lucide-react"

interface ResumeUploadProps {
  onFileSelect: (file: File | null) => void
}

export function ResumeUpload({ onFileSelect }: ResumeUploadProps) {
  const [fileName, setFileName] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      setFileName(file.name)
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  })

  const handleRemoveFile = () => {
    setFileName(null)
    onFileSelect(null)
  }

  return (
    <div className="space-y-4">
      <Label htmlFor="resume-upload">Upload your Resume</Label>
      <div
        {...getRootProps()}
        className="flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-md cursor-pointer hover:border-primary transition-colors duration-200 ease-in-out"
      >
        <input {...getInputProps()} />
        {fileName ? (
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-primary" />
            <span>{fileName}</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleRemoveFile}
              className="p-1 h-auto"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            {isDragActive ? (
              <p className="mt-2 text-sm text-gray-600">Drop the files here ...</p>
            ) : (
              <p className="mt-2 text-sm text-gray-600">Drag 'n' drop your resume here, or click to select files</p>
            )}
            <p className="mt-1 text-xs text-gray-500">(PDF, DOCX, TXT up to 5MB)</p>
          </div>
        )}
      </div>
    </div>
  )
}