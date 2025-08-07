'use client';

import { useState } from 'react';
import { Card, Title, TextInput, Button, Textarea } from '@tremor/react';
import { DatePicker, Text } from '@tremor/react';

interface InterviewSchedulerProps {
  onScheduleInterview: (data: any) => void;
  onClose: () => void;
}

export default function InterviewScheduler({ onScheduleInterview, onClose }: InterviewSchedulerProps) {
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [interviewDate, setInterviewDate] = useState<Date | undefined>(undefined);
  const [notes, setNotes] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!interviewDate) {
      alert('Please select an interview date.');
      return;
    }
    const interviewDetails = {
      job_title: jobTitle,
      company,
      interview_date: interviewDate.toISOString(),
      notes,
    };
    onScheduleInterview(interviewDetails);
    onClose();
  };

  return (
    <Card className="mt-6">
      <Title>Schedule Interview / Follow-up</Title>
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
          <Text>Interview Date</Text>
          <DatePicker
            value={interviewDate}
            onValueChange={setInterviewDate}
            placeholder="Select date"
          />
        </div>
        <div>
          <Text>Notes</Text>
          <Textarea
            placeholder="e.g., Interviewer names, topics to prepare..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>
        <div className="flex space-x-4">
          <Button type="submit">Schedule</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
        </div>
      </form>
    </Card>
  );
}