import React from 'react';
import Link from 'next/link';

const ApiDashboardPage = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl w-full bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-4xl font-extrabold text-gray-900 text-center mb-6">API Usage Dashboard</h1>
        <p className="text-xl text-gray-700 text-center mb-8">
          Monitor your API key usage, manage your subscriptions, and view detailed analytics for all our services.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <div className="bg-blue-50 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">API Keys</h2>
            <p className="text-gray-600 mb-4">Generate, revoke, and manage your API keys securely.</p>
            <Link href="/settings/api-keys" className="text-indigo-600 hover:underline font-semibold">Manage Keys &rarr;</Link>
          </div>
          
          <div className="bg-green-50 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Usage Analytics</h2>
            <p className="text-gray-600 mb-4">View detailed graphs and statistics of your API calls over time.</p>
            <Link href="/dashboard/analytics" className="text-indigo-600 hover:underline font-semibold">View Analytics &rarr;</Link>
          </div>

          <div className="bg-yellow-50 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Billing & Subscriptions</h2>
            <p className="text-gray-600 mb-4">Manage your payment methods, view invoices, and upgrade/downgrade plans.</p>
            <Link href="/settings/billing" className="text-indigo-600 hover:underline font-semibold">Manage Billing &rarr;</Link>
          </div>

          <div className="bg-purple-50 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Rate Limits</h2>
            <p className="text-gray-600 mb-4">Understand your current rate limits and how to request increases.</p>
            <Link href="/docs/rate-limits" className="text-indigo-600 hover:underline font-semibold">Learn More &rarr;</Link>
          </div>

          <div className="bg-red-50 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Support</h2>
            <p className="text-gray-600 mb-4">Get help with any issues or questions regarding your API usage.</p>
            <Link href="/support" className="text-indigo-600 hover:underline font-semibold">Contact Support &rarr;</Link>
          </div>

          <div className="bg-indigo-50 p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Documentation</h2>
            <p className="text-gray-600 mb-4">Explore our comprehensive API documentation for all services.</p>
            <Link href="/docs" className="text-indigo-600 hover:underline font-semibold">Read Docs &rarr;</Link>
          </div>
        </div>

        <div className="text-center mt-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Need More?</h2>
          <p className="text-lg text-gray-700 mb-6">
            If you have specific requirements or need enterprise-level solutions, please contact our sales team.
          </p>
          <Link href="/contact" className="px-6 py-3 bg-indigo-600 text-white text-lg font-semibold rounded-md shadow-md hover:bg-indigo-700 transition duration-300">
            Contact Sales
          </Link>
        </div>

        <div className="border-t border-gray-200 pt-8 text-center text-gray-500 text-sm mt-12">
          <p>&copy; 2024 Job Applier. All rights reserved.</p>
          <p>Your central hub for API management.</p>
        </div>
      </div>
    </div>
  );
};

export default ApiDashboardPage;