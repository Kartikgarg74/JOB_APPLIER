'use client';

import React, { useState, useRef } from 'react';

interface ResumeUploadFormProps {
  onUploadSuccess?: () => void;
}

export default function ResumeUploadForm({ onUploadSuccess }: ResumeUploadFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [uploading, setUploading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [showToast, setShowToast] = useState<boolean>(false);
  const [toastType, setToastType] = useState<'success' | 'error'>('success');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setMessage('');
      setError('');
      setProgress(0);
    } else {
      setSelectedFile(null);
    }
  };

  const handleToastClose = () => setShowToast(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Please select a resume file to upload.');
      setToastType('error');
      setShowToast(true);
      return;
    }
    setUploading(true);
    setMessage('');
    setError('');
    setProgress(0);

    // Analytics event (placeholder)
    console.log('Analytics: Resume upload started');

    const formData = new FormData();
    formData.append('resume', selectedFile);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/resume', true);
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          setProgress(Math.round((e.loaded / e.total) * 100));
        }
      };
      xhr.onload = () => {
        setUploading(false);
        if (xhr.status >= 200 && xhr.status < 300) {
          const data = JSON.parse(xhr.responseText);
          setMessage(data.message || 'Resume uploaded successfully!');
          setToastType('success');
          setShowToast(true);
          setSelectedFile(null);
          setProgress(100);
          if (fileInputRef.current) fileInputRef.current.value = '';
          // Analytics event (placeholder)
          console.log('Analytics: Resume upload success');
          if (onUploadSuccess) onUploadSuccess();
        } else {
          const data = JSON.parse(xhr.responseText);
          setError(data.error || 'Failed to upload resume.');
          setToastType('error');
          setShowToast(true);
          setProgress(0);
          // Analytics event (placeholder)
          console.log('Analytics: Resume upload error');
        }
      };
      xhr.onerror = () => {
        setUploading(false);
        setError('An unexpected error occurred during upload.');
        setToastType('error');
        setShowToast(true);
        setProgress(0);
        // Analytics event (placeholder)
        console.log('Analytics: Resume upload error');
      };
      xhr.send(formData);
    } catch (err) {
      setUploading(false);
      setError('An unexpected error occurred during upload.');
      setToastType('error');
      setShowToast(true);
      setProgress(0);
      // Analytics event (placeholder)
      console.log('Analytics: Resume upload error');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-4 sm:p-6 bg-white dark:bg-gray-900 rounded-lg shadow-md w-full">
      <h2 className="text-2xl sm:text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">Upload Your Resume</h2>
      <form onSubmit={handleSubmit} className="space-y-4" aria-label="Resume upload form">
        <div>
          <label htmlFor="resumeFile" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Select Resume File (PDF, DOCX):</label>
          <input
            type="file"
            id="resumeFile"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
            ref={fileInputRef}
            className="mt-1 block w-full text-xs sm:text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-xs sm:file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100 dark:file:bg-gray-800 dark:file:text-blue-300"
            aria-required="true"
            aria-describedby="resumeFile-desc"
          />
          <span id="resumeFile-desc" className="sr-only">Choose a PDF or DOCX file to upload as your resume.</span>
        </div>
        <button
          type="submit"
          disabled={!selectedFile || uploading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-xs sm:text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? (
            <span className="flex items-center">
              <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
              Uploading...
            </span>
          ) : 'Upload Resume'}
        </button>
        {progress > 0 && uploading && (
          <div
            className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mt-2"
            role="progressbar"
            {...(Number.isFinite(progress) ? {
              'aria-valuenow': Number(progress),
              'aria-valuemin': 0,
              'aria-valuemax': 100
            } : {})}
          >
            <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
          </div>
        )}
      </form>
      {/* Toast notification */}
      {showToast && (
        <div
          className={`fixed z-50 left-1/2 transform -translate-x-1/2 bottom-8 min-w-[200px] sm:min-w-[250px] max-w-[90vw] sm:max-w-xs px-4 py-3 rounded shadow-lg text-white ${toastType === 'success' ? 'bg-green-600' : 'bg-red-600'}`}
          role="alert"
          aria-live="assertive"
        >
          <div className="flex justify-between items-center">
            <span>{toastType === 'success' ? message : error}</span>
            <button onClick={handleToastClose} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Close notification">&times;</button>
          </div>
        </div>
      )}
      {/* Dismissible error alert for accessibility */}
      {error && !showToast && (
        <div className="mt-4 p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
          <button onClick={() => setError('')} className="absolute top-0 bottom-0 right-0 px-4 py-3" aria-label="Dismiss error">&times;</button>
        </div>
      )}
      {/* Success message for accessibility (if not using toast) */}
      {message && !showToast && (
        <div className="mt-4 p-3 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200 rounded" role="status">{message}</div>
      )}
    </div>
  );
}
