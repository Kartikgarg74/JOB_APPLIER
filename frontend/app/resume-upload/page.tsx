'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function ResumeUploadPage() {
  const [resumeText, setResumeText] = useState('');
  const [fileName, setFileName] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target && typeof e.target.result === 'string') {
          setResumeText(e.target.result);
        }
      };
      reader.readAsText(file); // For simplicity, reading as text. For DOCX/PDF, would need a backend parser.
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: false,
  });

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setResumeText(e.target.value);
    setFileName(''); // Clear file name if text is manually edited
  };

  const handleSubmit = () => {
    console.log('Resume Text:', resumeText);
    console.log('File Name:', fileName);
    // Here you would typically send the resumeText or file to your backend
    alert('Resume submitted! Check console for details.');
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Upload Your Resume</CardTitle>
          <CardDescription>Drag and drop your PDF/DOCX file, or paste your resume text below.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed p-6 text-center rounded-lg cursor-pointer
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}`}
          >
            <input {...getInputProps()} />
            {
              isDragActive ?
                <p>Drop the files here ...</p> :
                <p>Drag 'n' drop your resume here, or click to select files</p>
            }
            {fileName && <p className="mt-2 text-sm text-gray-600">Selected file: {fileName}</p>}
          </div>

          <div className="relative flex py-5 items-center">
            <div className="flex-grow border-t border-gray-300"></div>
            <span className="flex-shrink mx-4 text-gray-400">OR</span>
            <div className="flex-grow border-t border-gray-300"></div>
          </div>

          <Textarea
            placeholder="Paste your resume text here..."
            value={resumeText}
            onChange={handleTextChange}
            rows={15}
            className="w-full"
          />

          <Button onClick={handleSubmit} className="w-full">
            Submit Resume
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}