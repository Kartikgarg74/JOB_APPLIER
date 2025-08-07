// frontend/lib/jobs.ts

export interface JobListing {
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

/**
 * Simulates fetching job data from an API.
 * In a real application, this would make an actual API call.
 *
 * @param page The page number to fetch.
 * @param limit The number of jobs per page.
 * @param filters Optional filters for location, salary, experience, company.
 * @param searchQuery Optional search query for job titles or keywords.
 * @returns A promise that resolves to an array of JobListing.
 */
export async function fetchJobs(
  page: number = 0,
  limit: number = 10,
  filters?: { location?: string; salary?: string; experience?: string; company?: string },
  searchQuery?: string
): Promise<JobListing[]> {
  console.log(`Fetching jobs - Page: ${page}, Limit: ${limit}, Filters: ${JSON.stringify(filters)}, Query: ${searchQuery}`);

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));

  const allJobs: JobListing[] = [
    {
      id: '1',
      title: 'Software Engineer',
      company: 'Tech Solutions Inc.',
      location: 'Remote',
      salary_range: '$100k - $150k',
      experience_level: 'mid',
      description: 'Develop and maintain web applications using React and Node.js.',
      ats_score: 85,
      bookmarked: false,
    },
    {
      id: '2',
      title: 'Senior Data Scientist',
      company: 'Data Insights Corp.',
      location: 'New York, NY',
      salary_range: '$130k - $180k',
      experience_level: 'senior',
      description: 'Lead data analysis projects and build machine learning models.',
      ats_score: 92,
      bookmarked: true,
    },
    {
      id: '3',
      title: 'UX Designer',
      company: 'Creative Agency',
      location: 'San Francisco, CA',
      salary_range: '$90k - $120k',
      experience_level: 'mid',
      description: 'Design user-friendly interfaces for various digital products.',
      ats_score: 78,
      bookmarked: false,
    },
    {
      id: '4',
      title: 'DevOps Engineer',
      company: 'Cloud Innovations',
      location: 'Remote',
      salary_range: '$110k - $160k',
      experience_level: 'senior',
      description: 'Manage and optimize cloud infrastructure and CI/CD pipelines.',
      ats_score: 88,
      bookmarked: false,
    },
    {
      id: '5',
      title: 'Product Manager',
      company: 'Innovate Co.',
      location: 'New York, NY',
      salary_range: '$120k - $170k',
      experience_level: 'mid',
      description: 'Define product vision, strategy, and roadmap.',
      ats_score: 80,
      bookmarked: false,
    },
    {
      id: '6',
      title: 'Junior Software Developer',
      company: 'Startup Hub',
      location: 'Austin, TX',
      salary_range: '$60k - $90k',
      experience_level: 'entry',
      description: 'Assist in the development of new software features.',
      ats_score: 70,
      bookmarked: false,
    },
    {
      id: '7',
      title: 'Marketing Specialist',
      company: 'Global Brands',
      location: 'Remote',
      salary_range: '$70k - $100k',
      experience_level: 'mid',
      description: 'Develop and execute marketing campaigns.',
      ats_score: 65,
      bookmarked: false,
    },
    {
      id: '8',
      title: 'Cybersecurity Analyst',
      company: 'SecureNet',
      location: 'Washington, D.C.',
      salary_range: '$95k - $140k',
      experience_level: 'mid',
      description: 'Monitor and respond to security incidents.',
      ats_score: 89,
      bookmarked: false,
    },
    {
      id: '9',
      title: 'Frontend Developer',
      company: 'Web Solutions',
      location: 'Remote',
      salary_range: '$90k - $130k',
      experience_level: 'mid',
      description: 'Build responsive user interfaces with modern JavaScript frameworks.',
      ats_score: 82,
      bookmarked: false,
    },
    {
      id: '10',
      title: 'Backend Engineer',
      company: 'API Masters',
      location: 'Seattle, WA',
      salary_range: '$110k - $160k',
      experience_level: 'senior',
      description: 'Design and implement robust backend services and APIs.',
      ats_score: 90,
      bookmarked: false,
    },
    {
      id: '11',
      title: 'Cloud Architect',
      company: 'Azure Experts',
      location: 'Remote',
      salary_range: '$140k - $200k',
      experience_level: 'senior',
      description: 'Architect scalable and secure cloud solutions on Azure.',
      ats_score: 95,
      bookmarked: false,
    },
    {
      id: '12',
      title: 'Mobile App Developer',
      company: 'App Innovators',
      location: 'San Jose, CA',
      salary_range: '$100k - $150k',
      experience_level: 'mid',
      description: 'Develop cross-platform mobile applications using React Native.',
      ats_score: 87,
      bookmarked: false,
    },
  ];

  let filteredJobs = allJobs;

  // Apply filters
  const currentFilters = filters || {};
  if (currentFilters.location) {
    filteredJobs = filteredJobs.filter(job => job.location.toLowerCase().includes(currentFilters.location.toLowerCase()));
  }
  if (currentFilters.salary) {
    // This is a very basic salary filter. In a real app, you'd parse ranges.
    if (currentFilters.salary === '0-50k') {
      filteredJobs = filteredJobs.filter(job => job.salary_range && parseInt(job.salary_range.split('-')[0].replace(/[^0-9]/g, '')) < 50);
    } else if (currentFilters.salary === '50k-100k') {
      filteredJobs = filteredJobs.filter(job => job.salary_range && parseInt(job.salary_range.split('-')[0].replace(/[^0-9]/g, '')) >= 50 && parseInt(job.salary_range.split('-')[0].replace(/[^0-9]/g, '')) < 100);
    } else if (currentFilters.salary === '100k+') {
      filteredJobs = filteredJobs.filter(job => job.salary_range && parseInt(job.salary_range.split('-')[0].replace(/[^0-9]/g, '')) >= 100);
    }
  }
  if (currentFilters.experience) {
    filteredJobs = filteredJobs.filter(job => job.experience_level === currentFilters.experience);
  }
  if (currentFilters.company) {
    filteredJobs = filteredJobs.filter(job => job.company.toLowerCase().includes(currentFilters.company.toLowerCase()));
  }

  // Apply search query
  if (searchQuery) {
    filteredJobs = filteredJobs.filter(
      job =>
        job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }

  const startIndex = page * limit;
  const endIndex = startIndex + limit;
  const paginatedJobs = filteredJobs.slice(startIndex, endIndex);

  return paginatedJobs;
}