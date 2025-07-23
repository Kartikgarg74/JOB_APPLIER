"use client";

import { useEffect, useState } from "react";

interface Recommendation {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  match_score: number;
  reason: string;
}

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<
    Recommendation[] | null
  >(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        const response = await fetch("/api/recommendations");
        if (!response.ok) {
          throw new Error(
            `Failed to fetch recommendations: ${response.statusText}`,
          );
        }
        const data: Recommendation[] = await response.json();
        setRecommendations(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unknown error occurred");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading job recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-4xl font-bold mb-8">Job Recommendations</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recommendations && recommendations.length > 0 ? (
          recommendations.map((rec) => (
            <div
              key={rec.id}
              className="bg-white p-6 rounded-lg shadow-md border border-gray-200"
            >
              <h2 className="text-xl font-semibold mb-2 text-blue-700">
                {rec.title}
              </h2>
              <p className="text-gray-600 mb-1">
                <strong>Company:</strong> {rec.company}
              </p>
              <p className="text-gray-600 mb-1">
                <strong>Location:</strong> {rec.location}
              </p>
              <p className="text-gray-700 text-sm mt-3">{rec.description}</p>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-green-600 font-bold">
                  Match Score: {rec.match_score}%
                </p>
                <p className="text-gray-500 text-sm">Reason: {rec.reason}</p>
              </div>
            </div>
          ))
        ) : (
          <p className="text-lg col-span-full">
            No job recommendations available at the moment.
          </p>
        )}
      </div>
    </div>
  );
}
