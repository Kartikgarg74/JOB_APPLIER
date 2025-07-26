# Job Applier Frontend

A modern React/Next.js frontend for the Job Applier application that connects to multiple deployed backend services.

## 🚀 Deployed Services

The frontend connects to the following deployed backend services:

- **Job Applier Agent**: https://job-applier-job-applier.onrender.com
- **ATS Service**: https://job-applier-ats-ervice.onrender.com
- **User Service**: https://job-applier-user-services.onrender.com
- **Agent Orchestration Service**: https://job-applier-agent-orchestration-service.onrender.com

## 🛠️ Setup

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Environment Variables**

   Create a `.env.local` file in the frontend directory with the following variables:

   ```env
   # Backend Service URLs
   NEXT_PUBLIC_JOB_APPLIER_AGENT_URL=https://job-applier-job-applier.onrender.com
   NEXT_PUBLIC_ATS_SERVICE_URL=https://job-applier-ats-ervice.onrender.com
   NEXT_PUBLIC_USER_SERVICE_URL=https://job-applier-user-services.onrender.com
   NEXT_PUBLIC_AGENT_ORCHESTRATION_SERVICE_URL=https://job-applier-agent-orchestration-service.onrender.com

   # Legacy support (for backward compatibility)
   NEXT_PUBLIC_API_BASE_URL=https://job-applier-job-applier.onrender.com
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗️ Architecture

The frontend is built with:

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **React Context** - State management

### API Integration

The frontend connects to multiple microservices:

- **ATS Service**: Resume scoring and job search
- **User Service**: User profiles, education, experience, skills
- **Job Applier Agent**: Job applications and resume uploads
- **Agent Orchestration Service**: Job matching and automation

### Key Features

- 📊 ATS Resume Scoring
- 🔍 Job Search & Matching
- 👤 User Profile Management
- 📝 Application Tracking
- 🎯 Job Recommendations
- 📄 Resume Upload & Parsing

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect your repository** to Vercel
2. **Set environment variables** in Vercel dashboard:
   - `NEXT_PUBLIC_JOB_APPLIER_AGENT_URL`
   - `NEXT_PUBLIC_ATS_SERVICE_URL`
   - `NEXT_PUBLIC_USER_SERVICE_URL`
   - `NEXT_PUBLIC_AGENT_ORCHESTRATION_SERVICE_URL`
3. **Deploy** - Vercel will automatically build and deploy

### Netlify

1. **Connect your repository** to Netlify
2. **Set environment variables** in Netlify dashboard
3. **Build command**: `npm run build`
4. **Publish directory**: `.next`

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Railway
- Render
- DigitalOcean App Platform
- AWS Amplify

## 📁 Project Structure

```
frontend/
├── app/                 # Next.js App Router pages
├── components/          # Reusable UI components
├── lib/                 # Utilities and API functions
│   ├── config.ts       # API configuration
│   ├── ats.ts          # ATS service API calls
│   ├── applications.ts # Job application API calls
│   ├── user.ts         # User service API calls
│   ├── resume.ts       # Resume upload API calls
│   └── api-context.tsx # API context provider
├── hooks/              # Custom React hooks
├── public/             # Static assets
└── styles/             # Global styles
```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### API Development

The frontend uses a centralized API configuration in `lib/config.ts` that maps to different backend services. To add new API endpoints:

1. Add the endpoint to `API_CONFIG.ENDPOINTS`
2. Create the API function in the appropriate service file
3. Add the function to the `ApiServices` interface in `api-context.tsx`
4. Export the function from the context provider

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
