# Job Applier Agent Dashboard

## Purpose

This directory contains the user-friendly dashboard application for interacting with the Job Applier Agent. It provides a centralized interface for users to:

- View their resume and receive ATS score feedback.
- Explore job recommendations.
- Monitor the status of their job applications.
- Update their resume and personal preferences.
- Receive real-time notifications for application updates.

## Key Features

- **Resume Management**: Upload, view, and update your resume.
- **ATS Score & Feedback**: Get instant compatibility scores for your resume against job descriptions.
- **Job Recommendations**: Discover personalized job openings.
- **Application Tracking**: Monitor the status of your submitted applications.
- **User Preferences**: Manage your profile and application settings.
- **Real-time Notifications**: Stay informed about application progress.

## Technology Stack (Proposed)

- **Frontend Framework**: React (with Next.js for server-side rendering and API routes)
- **Styling**: Tailwind CSS
- **State Management**: React Context API or Zustand
- **Data Fetching**: SWR or React Query
- **Charting/Data Visualization**: Recharts or Chart.js

## Development Setup

(Instructions for setting up the dashboard locally will be added here.)

## API Endpoints Used

- `/upload-resume`
- `/ats-score`
- `/status`
- `/workflow/pause`
- `/workflow/resume`
- `/workflow/stop`
- `/config`
- `/health`

## Contributing

(Guidelines for contributing to the dashboard will be added here.)
