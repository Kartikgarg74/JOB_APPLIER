'use client';

import { useState } from 'react';
import { Card, Title, TextInput, Select, SelectItem, Button, Textarea, Text } from '@tremor/react';

interface ManualApplicationFormProps {
  onLogApplication: (data: any) => void;
  onClose: () => void;
}

export default function ManualApplicationForm({ onLogApplication, onClose }: ManualApplicationFormProps) {
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [status, setStatus] = useState('applied');
  const [notes, setNotes] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newApplication = {
      job_title: jobTitle,
      company,
      application_status: status,
      notes,
      last_updated: new Date().toISOString(),
      // Add other fields as necessary
    };
    onLogApplication(newApplication);
    onClose();
  };

  return (
    <Card className="mt-6">
      <Title>Log New Manual Application</Title>
      <form onSubmit={handleSubmit} className="space-y-4 mt-4">
        <div>
          <Text>Job Title</Text>
          <TextInput
            placeholder="e.g., Software Engineer"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <Text>Company</Text>
          <TextInput
            placeholder="e.g., Google"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            required
          />
        </div>
        <div>
          <Text>Status</Text>
          <Select value={status} onValueChange={setStatus} className="mt-1">
            <SelectItem value="applied">Applied</SelectItem>
            <SelectItem value="reviewed">Reviewed</SelectItem>
            <SelectItem value="interview">Interview</SelectItem>
            <SelectItem value="offer">Offer</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </Select>
        </div>
        <div>
          <Text>Notes</Text>
          <Textarea
            placeholder="Any relevant notes about this application..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>
        <div className="flex space-x-4">
          <Button type="submit">Log Application</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
        </div>
      </form>
    </Card>
  );
}