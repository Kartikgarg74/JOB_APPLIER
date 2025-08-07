"use client"

import React, { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { FileText, Upload, X, CheckCircle, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { API_CONFIG } from '@/lib/config';
interface ResumeUploadProps {
  onFileSelect: (file: File | null) => void;
  onUploadSuccess: (data: any) => void; // Callback for successful upload and parsing
}

export function ResumeUpload({ onFileSelect, onUploadSuccess }: ResumeUploadProps) {
  const [fileName, setFileName] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [parsingStatus, setParsingStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [extractedData, setExtractedData] = useState<any>(null);

  const MAX_FILE_SIZE_MB = 5;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

  const handleFileUpload = useCallback(async (file: File) => {
    setParsingStatus('uploading'); // Set status to uploading when starting the actual upload
    setUploadProgress(0); // Reset progress

    const formData = new FormData();
    formData.append('file', file);

    try {
       const response = await fetch(`${API_CONFIG.RESUME_SERVICE}/api/parse-resume`, {
         method: 'POST',
        body: formData,
        // No 'Content-Type' header needed for FormData, browser sets it
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload resume.');
      }

      const result = await response.json();
      setUploadProgress(100);
      setParsingStatus('success');
      setExtractedData(result); // Store the extracted data
      onUploadSuccess(result);

    } catch (err: any) {
      setErrorMessage(err.message || 'An error occurred during upload.');
      setParsingStatus('error');
      setUploadProgress(0);
      // onFileSelect(null); // Keep the file selected even if upload fails, just show error
    }
  }, [onUploadSuccess]); // Dependencies for handleFileUpload

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setErrorMessage(null); // Clear previous errors
    setUploadProgress(0); // Reset progress
    setParsingStatus('idle'); // Reset status

    if (acceptedFiles.length === 0) {
      setErrorMessage('No file was selected or the file type is not accepted.');
      onFileSelect(null);
      return;
    }

    const file = acceptedFiles[0];

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorMessage(`File size exceeds the maximum limit of ${MAX_FILE_SIZE_MB}MB.`);
      onFileSelect(null);
      return;
    }

    setFileName(file.name); // Set the file name
    onFileSelect(file); // Notify parent component about the selected file

    // Call the async file upload handler
    handleFileUpload(file);

  }, [onFileSelect, handleFileUpload]);

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
    setFileName(null);
    setUploadProgress(0);
    setParsingStatus('idle');
    setErrorMessage(null);
    onFileSelect(null);
  };

  return (
    <div className="space-y-4">
      <Label htmlFor="resume-upload">Upload your Resume</Label>
      <div
        {...getRootProps()}
        className="flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-md cursor-pointer hover:border-primary transition-colors duration-200 ease-in-out"
      >
        <input {...getInputProps()} />
        {errorMessage && (
          <Alert variant="destructive" className="mb-4 w-full">
            <AlertDescription className="flex items-center">
              <X className="h-4 w-4 mr-2" /> {errorMessage}
            </AlertDescription>
          </Alert>
        )}

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
            <p className="mt-1 text-xs text-gray-500">(PDF, DOCX, TXT up to {MAX_FILE_SIZE_MB}MB)</p>
          </div>
        )}

        {(parsingStatus === 'uploading' || parsingStatus === 'parsing') && (
          <div className="w-full mt-4">
            <Progress value={uploadProgress} className="w-full" />
            <div className="flex justify-between text-sm mt-2">
              <span className="text-gray-500">{parsingStatus === 'uploading' ? 'Uploading...' : 'Parsing...'}</span>
              <span className="text-gray-500">{uploadProgress}%</span>
            </div>
          </div>
        )}

        {parsingStatus === 'success' && (
          <div className="w-full mt-4 flex items-center justify-center text-green-600">
            <CheckCircle className="h-5 w-5 mr-2" /> Resume parsed successfully!
          </div>
        )}

        {parsingStatus === 'error' && (
          <div className="w-full mt-4 flex items-center justify-center text-red-600">
            <X className="h-5 w-5 mr-2" /> Error parsing resume.
          </div>
        )}

        {fileName && parsingStatus === 'success' && extractedData && (
          <div className="w-full mt-4">
            <h3 className="text-lg font-semibold mb-2">Extracted Profile Data:</h3>
            <div className="space-y-2 text-sm text-gray-700">
              {extractedData.name && <p><strong>Name:</strong> {extractedData.name}</p>}
              {extractedData.email && <p><strong>Email:</strong> {extractedData.email}</p>}
              {extractedData.phone && <p><strong>Phone:</strong> {extractedData.phone}</p>}
              {extractedData.skills && extractedData.skills.length > 0 && (
                <p><strong>Skills:</strong> {extractedData.skills.join(', ')}</p>
              )}
              {extractedData.experience && extractedData.experience.length > 0 && (
                <div>
                  <strong>Experience:</strong>
                  <ul className="list-disc list-inside ml-4">
                    {extractedData.experience.map((exp: any, index: number) => (
                      <li key={index}>{exp.title} at {exp.company} ({exp.years})</li>
                    ))}
                  </ul>
                </div>
              )}
              {extractedData.education && extractedData.education.length > 0 && (
                <div>
                  <strong>Education:</strong>
                  <ul className="list-disc list-inside ml-4">
                    {extractedData.education.map((edu: any, index: number) => (
                      <li key={index}>{edu.degree} from {edu.university} ({edu.years})</li>
                    ))}
                  </ul>
                </div>
              )}
              <Badge variant="secondary" className="mt-4">Resume uploaded and parsed successfully. You can now proceed to the next step.</Badge>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}