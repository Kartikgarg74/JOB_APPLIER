'use client';

import useSWR from 'swr';
import { Card, Title, Text, Badge, Flex, Metric } from '@tremor/react';
import { Grid, Col } from '@tremor/react';
import { BarChart, DonutChart } from '@tremor/react';
import { fetchApplications } from '@/lib/applications';
import type { Application } from '@/lib/applications';
import ManualApplicationForm from '@/components/ManualApplicationForm';
import InterviewScheduler from '@/components/InterviewScheduler';
import { useState } from 'react';
import ExportDataButton from '@/components/ExportDataButton';



const valueFormatter = (number: number) => `${number}`;

const fetcher = async (url: string) => {
  // Assuming a user ID of 1 for now, replace with actual user ID later
  const userId = 1;
  const applications = await fetchApplications(userId);
  return applications.map(app => ({
    id: app.id.toString(),
    job_title: app.position,
    company: app.company,
    job_match_score: app.jobMatchScore || 0,
    ats_score: app.atsScore || 0,
    cover_letter: app.notes || '',
    application_status: app.status.toLowerCase() as 'applied' | 'reviewed' | 'interview' | 'offer' | 'rejected',
    last_updated: app.appliedDate,
    response_time: app.responseTime ? parseFloat(app.responseTime) : undefined,
    interview_date: app.interviewDate,
    offer_details: app.offerDetails,
    rejection_reason: app.rejectionReason,
  }));
};

export default function JobMatchDashboard() {
  const { data: jobApplications, error } = useSWR('/api/job-applications', fetcher);

  if (error) return <Text>Failed to load job applications.</Text>;
  if (!jobApplications) return <Text>Loading job applications...</Text>;

  const statusData = jobApplications.reduce((acc, app) => {
    acc[app.application_status] = (acc[app.application_status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const chartData = Object.entries(statusData).map(([name, value]) => ({
    name,
    value,
  }));

  const totalApplications = jobApplications.length;
  const offerApplications = jobApplications.filter(app => app.application_status === 'offer').length;
  const successRate = totalApplications > 0 ? (offerApplications / totalApplications) * 100 : 0;

  const [showManualForm, setShowManualForm] = useState(false);
  const [showInterviewScheduler, setShowInterviewScheduler] = useState(false);

  const avgResponseTime = jobApplications.filter(app => app.response_time !== undefined && app.response_time !== null).reduce((sum, app) => sum + (app.response_time || 0), 0) / jobApplications.filter(app => app.response_time !== undefined && app.response_time !== null).length || 0;

  // TODO: Implement improvement suggestions based on analytics

  const handleLogNewApplication = (newAppData: any) => {
    // In a real application, you would send this to your backend/Supabase
    console.log('Logging new manual application:', newAppData);
    // For now, we'll just add it to the current data for display
    jobApplications.push({
      ...newAppData,
      id: `manual-${jobApplications.length + 1}`,
      job_match_score: 0, // Default for manual
      ats_score: 0, // Default for manual
      cover_letter: newAppData.notes || 'Manually logged application.',
      application_status: newAppData.status.toLowerCase(),
      last_updated: new Date().toISOString(),
    });
    // Trigger re-render (SWR revalidation or state update)
    // mutate('/api/job-applications'); // If using SWR's mutate
    setShowManualForm(false);
  };

  const handleScheduleInterview = (interviewData: any) => {
    console.log('Scheduling interview:', interviewData);
    // TODO: Send this data to backend/Supabase for persistent storage and reminders
    setShowInterviewScheduler(false);
  };

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <Title>Job Application Dashboard</Title>
      <Text>Overview of your job application statuses and scores.</Text>

      <Grid numItemsMd={2} numItemsLg={4} className="gap-6 mt-6">
        <Card>
          <Text>Total Applications</Text>
          <Metric>{totalApplications}</Metric>
        </Card>
        <Card>
          <Text>Average Job Match Score</Text>
          <Metric>{(jobApplications.reduce((sum, app) => sum + app.job_match_score, 0) / totalApplications).toFixed(1)}%</Metric>
        </Card>
        <Card>
          <Text>Average ATS Score</Text>
          <Metric>{(jobApplications.reduce((sum, app) => sum + app.ats_score, 0) / totalApplications).toFixed(1)}%</Metric>
        </Card>
        <Card>
          <Text>Success Rate</Text>
          <Metric>{successRate.toFixed(1)}%</Metric>
        </Card>
        <Card>
          <Text>Average Response Time</Text>
          <Metric>{avgResponseTime.toFixed(1)} days</Metric>
        </Card>
      </Grid>

      <div className="mt-6">
        <Card>
          <Title>Application Status Distribution</Title>
          <DonutChart
            className="mt-6"
            data={chartData}
            category="value"
            index="name"
            valueFormatter={valueFormatter}
            colors={['blue', 'violet', 'indigo', 'emerald', 'rose', 'cyan']}
          />
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Application Analytics</Title>
          {/* TODO: Add more charts for response times, success rates over time, etc. */}
          <Text className="mt-4">Improvement Suggestions: (TODO: Implement AI-driven suggestions)</Text>
          <Text className="text-sm text-gray-600">Based on your application history, consider applying to roles with higher ATS score potential.</Text>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Market Insights & Trends</Title>
          <Text className="mt-4">Stay updated with the latest job market trends and demand forecasting.</Text>
          {/* Placeholder for market trends chart/data */}
          <BarChart
            className="mt-6"
            data={[
              { name: 'Q1 2023', 'Job Openings': 120000 },
              { name: 'Q2 2023', 'Job Openings': 135000 },
              { name: 'Q3 2023', 'Job Openings': 110000 },
              { name: 'Q4 2023', 'Job Openings': 145000 },
            ]}
            index="name"
            categories={['Job Openings']}
            colors={['teal']}
            valueFormatter={valueFormatter}
          />
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Salary Benchmarking</Title>
          <Text className="mt-4">Compare your expected salary with market averages for your role and location.</Text>
          {/* Placeholder for salary benchmarking data */}
          <div className="mt-4">
            <Text>Average Salary for Software Engineer (NYC): <Metric>$120,000 - $150,000</Metric></Text>
            <Text>Your Expected Salary: <Metric>$130,000</Metric></Text>
            <Text className="text-sm text-gray-600 mt-2">Data based on recent market analysis.</Text>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Skill Gap Analysis & Learning Recommendations</Title>
          <Text className="mt-4">Identify skill gaps and get personalized learning recommendations.</Text>
          {/* Placeholder for skill gap data and recommendations */}
          <div className="mt-4">
            <Text>Your Skills: Python, React, SQL, Git</Text>
            <Text>In-Demand Skills (missing): Docker, Kubernetes, AWS</Text>
            <Text className="text-sm text-gray-600 mt-2">Recommendations:</Text>
            <ul className="list-disc list-inside text-sm text-gray-600">
              <li>Take a Docker & Kubernetes course on Coursera.</li>
              <li>Explore AWS certifications for cloud deployment.</li>
            </ul>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Personal Application Funnel Metrics</Title>
          <Text className="mt-4">Track your application progress through different stages.</Text>
          {/* This is already partially covered by the DonutChart, but can be expanded */}
          <div className="mt-4">
            <Text>Applications Started: {totalApplications}</Text>
            <Text>Applications Submitted: {totalApplications}</Text>
            <Text>Interviews Scheduled: {jobApplications.filter(app => app.application_status === 'interview').length}</Text>
            <Text>Offers Received: {offerApplications}</Text>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Interview Preparation Suggestions</Title>
          <Text className="mt-4">Get tailored suggestions based on common interview requirements.</Text>
          {/* Placeholder for interview prep suggestions */}
          <div className="mt-4">
            <Text className="text-sm text-gray-600">For a Software Engineer role:</Text>
            <ul className="list-disc list-inside text-sm text-gray-600">
              <li>Practice LeetCode (Data Structures & Algorithms).</li>
              <li>Review System Design concepts.</li>
              <li>Prepare behavioral questions (STAR method).</li>
            </ul>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Goal Setting & Progress Tracking</Title>
          <Text className="mt-4">Set and track your job search goals.</Text>
          {/* Placeholder for goal setting UI */}
          <div className="mt-4">
            <Text>Goal: Apply to 50 jobs by end of month</Text>
            <Text>Progress: {totalApplications} / 50</Text>
            <Text>Goal: Secure 3 interviews</Text>
            <Text>Progress: {jobApplications.filter(app => app.application_status === 'interview').length} / 3</Text>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <Title>Manual Application Logging</Title>
          <Text>Log applications that were not submitted through the automated system.</Text>
          <button
            onClick={() => setShowManualForm(true)}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Log New Manual Application
          </button>
        </Card>
      </div>

      {showManualForm && (
        <ManualApplicationForm
          onLogApplication={handleLogNewApplication}
          onClose={() => setShowManualForm(false)}
        />
      )}


      <div className="mt-6">
        <Card>
          <Title>Interview Scheduling & Reminders</Title>
          <Text>Schedule interviews and set follow-up reminders.</Text>
          <button
            onClick={() => setShowInterviewScheduler(true)}
            className="mt-4 px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600"
          >
            Schedule New Interview
          </button>
        </Card>
      </div>

      {showInterviewScheduler && (
        <InterviewScheduler
          onScheduleInterview={handleScheduleInterview}
          onClose={() => setShowInterviewScheduler(false)}
        />
      )}

      <div className="mt-6">
        <Card>
          <Title>Export Application Data</Title>
          <Text>Export your job application data to CSV or PDF.</Text>
          <div className="mt-4">
            <ExportDataButton data={jobApplications} />
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Title>Recent Job Applications</Title>
        <Grid numItemsMd={1} numItemsLg={1} className="gap-6 mt-6">
          {jobApplications.map((app) => (
            <Card key={app.id} className="w-full">
              <Flex alignItems="start" className="mb-4">
                <div className="truncate">
                  <Text>{app.company}</Text>
                  <Title>{app.job_title}</Title>
                </div>
                <Badge
                  color={app.application_status === 'applied' ? 'blue' : app.application_status === 'reviewed' ? 'violet' : app.application_status === 'interview' ? 'indigo' : app.application_status === 'offer' ? 'emerald' : 'rose'}
                >
                  {app.application_status}
                </Badge>
              </Flex>
              <Flex justifyContent="between" alignItems="center" className="mt-4">
                <div>
                  <Text>Job Match Score</Text>
                  <Metric>{app.job_match_score.toFixed(1)}%</Metric>
                </div>
                <div>
                  <Text>ATS Score</Text>
                  <Metric>{app.ats_score.toFixed(1)}%</Metric>
                </div>
              </Flex>
              <div className="mt-4">
                <Text className="font-semibold">Cover Letter Preview:</Text>
                <Text className="text-sm line-clamp-3">{app.cover_letter}</Text>
              </div>
              <Text className="text-xs text-gray-500 mt-2">Last Updated: {new Date(app.last_updated).toLocaleString()}</Text>
              {app.interview_date && (
                <Text className="text-xs text-gray-500 mt-1">Interview Date: {new Date(app.interview_date).toLocaleString()}</Text>
              )}
              {app.offer_details && (
                <Text className="text-xs text-gray-500 mt-1">Offer: {app.offer_details}</Text>
              )}
              {app.rejection_reason && (
                <Text className="text-xs text-gray-500 mt-1">Rejected: {app.rejection_reason}</Text>
              )}
              {app.response_time && (
                <Text className="text-xs text-gray-500 mt-1">Response Time: {app.response_time} days</Text>
              )}
            </Card>
          ))}
        </Grid>
      </div>
    </main>
  );
}