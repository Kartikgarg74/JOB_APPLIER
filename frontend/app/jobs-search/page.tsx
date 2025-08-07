'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, Title, Text, TextInput, Select, SelectItem, Button, Flex, Grid, Col, Badge, Metric } from '@tremor/react';
import { HeartIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import useSWRInfinite from 'swr/infinite';
import { useInView } from 'react-intersection-observer';
import { fetchJobs } from '@/lib/jobs'; // Assuming a new lib/jobs.ts for fetching job data

interface JobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  experience_level: string;
  description: string;
  ats_score: number;
  bookmarked: boolean;
}

const getKey = (pageIndex: number, previousPageData: JobListing[]) => {
  if (previousPageData && !previousPageData.length) return null; // Reached the end
  return `/api/jobs?page=${pageIndex}&limit=10`; // API endpoint for jobs
};

const fetcher = async (url: string) => {
  // Placeholder for actual job fetching logic
  // In a real app, this would call your backend API
  console.log(`Fetching from: ${url}`);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch jobs');
  }
  const data = await response.json();
  return data.jobs; // Assuming the API returns { jobs: [], total: N }
};

export default function JobSearchPage() {
  const [filters, setFilters] = useState({
    location: '',
    salary: '',
    experience: '',
    company: '',
  });
  const [searchQuery, setSearchQuery] = useState('');

  const { data, error, size, setSize, isValidating } = useSWRInfinite(getKey, fetcher);
  const jobs = data ? [].concat(...data) : [];
  const isLoadingInitialData = !data && !error;
  const isLoadingMore = isLoadingInitialData || (size > 0 && data && typeof data[size - 1] === 'undefined');
  const isEmpty = data?.[0]?.length === 0;
  const isReachingEnd = isEmpty || (data && data[data.length - 1]?.length < 10); // Assuming limit is 10

  const { ref, inView } = useInView({
    threshold: 0,
  });

  useEffect(() => {
    if (inView && !isReachingEnd && !isLoadingMore) {
      setSize(size + 1);
    }
  }, [inView, isReachingEnd, isLoadingMore, setSize, size]);

  const handleFilterChange = (name: string, value: string) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleSearch = () => {
    // Trigger a re-fetch with new search query/filters
    setSize(1); // Reset to first page
    // In a real app, you'd pass filters and searchQuery to getKey/fetcher
  };

  const toggleBookmark = (id: string) => {
    // TODO: Implement bookmarking logic (e.g., update backend, local state)
    console.log(`Toggling bookmark for job ${id}`);
  };

  const oneClickApply = (jobId: string) => {
    // TODO: Integrate with JOB_APPLIER service
    console.log(`One-click apply for job ${jobId}`);
    alert('Applying for job... (Integration with JOB_APPLIER service)');
  };

  if (error) return <Text>Failed to load jobs.</Text>;

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <Title>Job Search & Discovery</Title>
      <Text>Find your next career opportunity.</Text>

      <Card className="mt-6">
        <Flex className="space-x-4">
          <TextInput
            icon={MagnifyingGlassIcon}
            placeholder="Search job title or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-grow"
          />
          <Button onClick={handleSearch}>Search</Button>
        </Flex>
        <Grid numItemsMd={2} numItemsLg={4} className="gap-4 mt-4">
          <Select
            value={filters.location}
            onValueChange={(value) => handleFilterChange('location', value)}
            placeholder="Location"
          >
            <SelectItem value="">All Locations</SelectItem>
            <SelectItem value="remote">Remote</SelectItem>
            <SelectItem value="new_york">New York</SelectItem>
            <SelectItem value="san_francisco">San Francisco</SelectItem>
          </Select>
          <Select
            value={filters.salary}
            onValueChange={(value) => handleFilterChange('salary', value)}
            placeholder="Salary Range"
          >
            <SelectItem value="">Any Salary</SelectItem>
            <SelectItem value="0-50k">$0 - $50k</SelectItem>
            <SelectItem value="50k-100k">$50k - $100k</SelectItem>
            <SelectItem value="100k+">$100k+</SelectItem>
          </Select>
          <Select
            value={filters.experience}
            onValueChange={(value) => handleFilterChange('experience', value)}
            placeholder="Experience Level"
          >
            <SelectItem value="">Any Experience</SelectItem>
            <SelectItem value="entry">Entry Level</SelectItem>
            <SelectItem value="mid">Mid-Level</SelectItem>
            <SelectItem value="senior">Senior Level</SelectItem>
          </Select>
          <TextInput
            placeholder="Company"
            value={filters.company}
            onChange={(e) => handleFilterChange('company', e.target.value)}
          />
        </Grid>
      </Card>

      <div className="mt-6">
        <Title>Job Listings</Title>
        {isLoadingInitialData ? (
          <Text>Loading jobs...</Text>
        ) : isEmpty ? (
          <Text>No jobs found matching your criteria.</Text>
        ) : (
          <Grid numItemsSm={1} numItemsMd={2} numItemsLg={3} className="gap-6 mt-6">
            {jobs.map((job: JobListing) => (
              <Card key={job.id} className="relative">
                <Flex justifyContent="between" alignItems="start">
                  <div>
                    <Title>{job.title}</Title>
                    <Text className="mt-1">{job.company} - {job.location}</Text>
                    {job.salary_range && <Text className="mt-1">Salary: {job.salary_range}</Text>}
                    <Text className="mt-1">Experience: {job.experience_level}</Text>
                  </div>
                  <button
                    onClick={() => toggleBookmark(job.id)}
                    className={`p-2 rounded-full ${job.bookmarked ? 'text-red-500' : 'text-gray-400'} hover:text-red-500`}
                    aria-label={job.bookmarked ? 'Remove from bookmarks' : 'Add to bookmarks'}
                  >
                    <HeartIcon className="h-6 w-6" />
                  </button>
                </Flex>
                <Text className="mt-4 text-sm line-clamp-3">{job.description}</Text>
                <Flex justifyContent="between" alignItems="center" className="mt-4">
                  <Badge color="blue">ATS Score: {job.ats_score}%</Badge>
                  <Button size="xs" onClick={() => oneClickApply(job.id)}>One-Click Apply</Button>
                </Flex>
              </Card>
            ))}
          </Grid>
        )}

        <div ref={ref} className="mt-6 text-center">
          {isLoadingMore && <Text>Loading more jobs...</Text>}
          {isReachingEnd && !isEmpty && <Text>You have reached the end of the job listings.</Text>}
        </div>
      </div>

      {/* TODO: Job Alerts System */}
      <Card className="mt-6">
        <Title>Job Alerts</Title>
        <Text>Get notified when new jobs matching your criteria are posted.</Text>
        <Button className="mt-4">Create Job Alert</Button>
      </Card>

      {/* TODO: Job Search Analytics and User Behavior Tracking */}
      <Card className="mt-6">
        <Title>Search Analytics</Title>
        <Text>Insights into your job search activity.</Text>
        {/* Placeholder for charts/metrics */}
        <Metric className="mt-4">Total Searches: 120</Metric>
        <Metric>Jobs Viewed: 500</Metric>
      </Card>
    </main>
  );
}