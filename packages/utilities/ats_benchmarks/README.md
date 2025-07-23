# ATS Benchmarking Data

## Purpose
This directory contains sample resume and job description data specifically designed for benchmarking and testing the performance of the ATS (Applicant Tracking System) scoring and resume enhancement agents. This data allows for consistent and repeatable evaluation of how well the agents match resumes to job descriptions and identify areas for improvement.

## Key Components
- `SAMPLE_RESUMES`: A list of dictionaries, each representing a sample resume. Each resume includes:
  - `id`: A unique identifier for the resume.
  - `content`: The full text content of the resume.
  - `keywords`: A list of key terms extracted or associated with the resume.
  - `skills`: A list of skills identified in the resume.

- `SAMPLE_JOB_DESCRIPTIONS`: A list of dictionaries, each representing a sample job description. Each job description includes:
  - `id`: A unique identifier for the job description.
  - `title`: The job title.
  - `company`: The company offering the job.
  - `description`: The full text content of the job description.
  - `requirements`: Key requirements listed in the job description.
  - `keywords`: A list of key terms extracted or associated with the job description.
  - `skills`: A list of skills required for the job.

- `EXPECTED_ATS_SCORES`: A dictionary mapping tuples of `(resume_id, job_id)` to their expected ATS score and a brief reason. This serves as the ground truth for evaluating the ATS Scorer Agent's accuracy.

## Usage
This data is primarily used by automated tests and benchmarking scripts to:
1. **Evaluate ATS Scoring**: The `ATSScorerAgent` can be run against pairs of `SAMPLE_RESUMES` and `SAMPLE_JOB_DESCRIPTIONS`, and its output can be compared against the `EXPECTED_ATS_SCORES` to measure accuracy.
2. **Test Resume Enhancement**: Future `ResumeEnhancerAgent` functionality can use this data to identify how well it suggests improvements to resumes based on job descriptions.
3. **Regression Testing**: Ensures that changes to the ATS scoring or resume parsing logic do not negatively impact existing performance.

## Adding New Benchmarks
To add new sample data for benchmarking:
1. Create new entries in `SAMPLE_RESUMES` and `SAMPLE_JOB_DESCRIPTIONS` following the existing schema.
2. Manually assess the expected ATS score for each new `(resume_id, job_id)` pair and add it to `EXPECTED_ATS_SCORES` with a brief `reason` for the score.
3. Ensure the new data covers various scenarios, including high matches, low matches, and edge cases.

## Contributing
Contributions that expand the diversity and realism of the benchmarking data are highly encouraged. Please ensure new data is well-formatted and includes corresponding expected scores.