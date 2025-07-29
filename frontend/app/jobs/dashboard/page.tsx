'use client';

import useSWR from 'swr';
import { Card, Title, Text, Badge, Flex, Metric } from '@tremor/react';
import { Grid, Col } from '@tremor/react';
import { BarChart, DonutChart } from '@tremor/react';
import { fetchApplications } from '@/lib/applications';
import { Application } from '@/lib/applications';

interface JobApplication {
  id: string;
  job_title: string;
  company: string;
  job_match_score: number;
  ats_score: number;
  cover_letter: string;
  application_status: string;
  last_updated: string;
}

const valueFormatter = (number: number) => `${number}`;

const fetcher = async (url: string) => {
  // Assuming a user ID of 1 for now, replace with actual user ID later
  const userId = 1;
  const applications = await fetchApplications(userId);
  return applications.map(app => ({
    id: app.id.toString(),
    job_title: app.position,
    company: app.company,
    job_match_score: app.atsScore || 0, // Using atsScore as job_match_score for now
    ats_score: app.atsScore || 0,
    cover_letter: app.notes || '',
    application_status: app.status.toLowerCase(),
    last_updated: app.appliedDate,
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

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <Title>Job Application Dashboard</Title>
      <Text>Overview of your job application statuses and scores.</Text>

      <Grid numItemsMd={2} numItemsLg={3} className="gap-6 mt-6">
        <Card>
          <Text>Total Applications</Text>
          <Metric>{jobApplications.length}</Metric>
        </Card>
        <Card>
          <Text>Average Job Match Score</Text>
          <Metric>{(jobApplications.reduce((sum, app) => sum + app.job_match_score, 0) / jobApplications.length).toFixed(1)}%</Metric>
        </Card>
        <Card>
          <Text>Average ATS Score</Text>
          <Metric>{(jobApplications.reduce((sum, app) => sum + app.ats_score, 0) / jobApplications.length).toFixed(1)}%</Metric>
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
            colors={['blue', 'violet', 'indigo', 'rose', 'cyan']}
          />
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
                  color={app.application_status === 'submitted' ? 'emerald' : app.application_status === 'retrying' ? 'amber' : 'rose'}
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
            </Card>
          ))}
        </Grid>
      </div>
    </main>
  );
}