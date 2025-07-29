import React from 'react';
import Link from 'next/link';

const JobMatcherLandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-4xl font-extrabold text-gray-900 text-center mb-6">Job Matcher API</h1>
        <p className="text-xl text-gray-700 text-center mb-8">
          Revolutionize your job search or recruitment process with our intelligent Job Matcher API. 
          Find the perfect fit by semantically matching resumes to job descriptions.
        </p>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Key Features:</h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>Semantic matching using advanced AI algorithms.</li>
              <li>High accuracy in identifying relevant skills and experience.</li>
              <li>Customizable matching criteria.</li>
              <li>Fast and scalable for large datasets.</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">How it Works:</h2>
            <ol className="list-decimal list-inside text-gray-600 space-y-2">
              <li>Send resume data and job description to the API.</li>
              <li>Receive a match score and highlighted keywords.</li>
              <li>Integrate into your platform for intelligent recommendations.</li>
            </ol>
          </div>
        </div>

        <div className="bg-green-50 border-l-4 border-green-400 text-green-800 p-4 mb-12" role="alert">
          <p className="font-bold">Freemium Access Available!</p>
          <p>Start matching with our free tier and scale up as your needs grow. Check out our flexible pricing plans.</p>
        </div>

        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Get Started Today!</h2>
          <p className="text-lg text-gray-700 mb-6">
            Access our API with a simple API key. Monitor your usage and manage your billing through our intuitive dashboard.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/signup" className="px-6 py-3 bg-indigo-600 text-white text-lg font-semibold rounded-md shadow-md hover:bg-indigo-700 transition duration-300">
              Sign Up for Free
            </Link>
            <Link href="/docs/api-keys" className="px-6 py-3 border border-indigo-600 text-indigo-600 text-lg font-semibold rounded-md shadow-md hover:bg-indigo-50 transition duration-300">
              View API Docs
            </Link>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-8 text-center text-gray-500 text-sm">
          <p>&copy; 2024 Job Applier. All rights reserved.</p>
          <p>Powered by cutting-edge AI technology.</p>
        </div>
      </div>
    </div>
  );
};

export default JobMatcherLandingPage;