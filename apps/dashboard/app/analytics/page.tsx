"use client";

import React, { useEffect, useState } from "react";
import { Alert, AlertDescription } from "../../../../frontend/components/ui/alert";
import { Button } from "../../../../frontend/components/ui/button";
import { Skeleton } from "../../../../frontend/components/ui/skeleton";
import dynamic from "next/dynamic";

const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const PieChart = dynamic(() => import("recharts").then(m => m.PieChart), { ssr: false });
const Pie = dynamic(() => import("recharts").then(m => m.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(m => m.Cell), { ssr: false });

function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [error, setError] = useState<Error | null>(null);
  return error ? (
    <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
      <AlertDescription>
        <div className="flex justify-between items-center">
          <span>{error.message || "An unexpected error occurred. Please try again."}</span>
          <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
        </div>
      </AlertDescription>
    </Alert>
  ) : (
    <ErrorBoundaryInner setError={setError}>{children}</ErrorBoundaryInner>
  );
}
class ErrorBoundaryInner extends React.Component<{ setError: (e: Error) => void; children: React.ReactNode }> {
  componentDidCatch(error: Error) {
    this.props.setError(error);
  }
  render() {
    return this.props.children;
  }
}

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // Simulate async fetch
    setTimeout(() => {
      setData({
        trends: [
          { date: "2024-06-01", applications: 2, interviews: 1 },
          { date: "2024-06-02", applications: 4, interviews: 2 },
          { date: "2024-06-03", applications: 3, interviews: 1 },
          { date: "2024-06-04", applications: 5, interviews: 2 },
        ],
        atsScores: [
          { label: "Resume 1", score: 85 },
          { label: "Resume 2", score: 92 },
          { label: "Resume 3", score: 78 },
        ],
        matchDistribution: [
          { name: "80-100%", value: 12 },
          { name: "60-79%", value: 8 },
          { name: "<60%", value: 3 },
        ],
      });
      setLoading(false);
    }, 1200);
  }, []);

  const handleExport = (type: "csv" | "json") => {
    if (!data) return;
    let content = "";
    let filename = "analytics-export." + type;
    if (type === "json") {
      content = JSON.stringify(data, null, 2);
    } else {
      // Simple CSV export for trends
      content = "date,applications,interviews\n" +
        data.trends.map((row: any) => `${row.date},${row.applications},${row.interviews}`).join("\n");
    }
    const blob = new Blob([content], { type: type === "json" ? "application/json" : "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Analytics" tabIndex={-1} className="p-6 max-w-5xl mx-auto focus:outline-none">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Analytics & Trends</h1>
          <div className="flex gap-2">
            <button
              aria-label="Export analytics as CSV"
              className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 focus:outline-none focus:ring"
              onClick={() => handleExport("csv")}
              disabled={!data}
            >
              Export CSV
            </button>
            <button
              aria-label="Export analytics as JSON"
              className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 focus:outline-none focus:ring"
              onClick={() => handleExport("json")}
              disabled={!data}
            >
              Export JSON
            </button>
          </div>
        </div>
        {error && (
          <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
            <AlertDescription>
              <div className="flex justify-between items-center">
                <span>{error}</span>
                <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
              </div>
            </AlertDescription>
          </Alert>
        )}
        {loading ? (
          <div className="space-y-6">
            <Skeleton className="h-10 w-1/2" />
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : (
          <>
            <section className="mb-12">
              <h2 className="text-xl font-semibold mb-2">Application Trends</h2>
              {LineChart && Line && XAxis && YAxis && CartesianGrid && Tooltip ? (
                <LineChart width={600} height={300} data={data.trends} aria-label="Application Trends Chart">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="applications" stroke="#8884d8" name="Applications" />
                  <Line type="monotone" dataKey="interviews" stroke="#82ca9d" name="Interviews" />
                </LineChart>
              ) : <Skeleton className="h-64 w-full" />}
            </section>
            <section className="mb-12">
              <h2 className="text-xl font-semibold mb-2">ATS Scores</h2>
              {BarChart && Bar && XAxis && YAxis && CartesianGrid && Tooltip ? (
                <BarChart width={600} height={300} data={data.atsScores} aria-label="ATS Scores Chart">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="score" fill="#8884d8" name="ATS Score" />
                </BarChart>
              ) : <Skeleton className="h-64 w-full" />}
            </section>
            <section className="mb-12">
              <h2 className="text-xl font-semibold mb-2">Job Match Distribution</h2>
              {PieChart && Pie && Cell && Tooltip ? (
                <PieChart width={400} height={300} aria-label="Job Match Distribution Chart">
                  <Pie data={data.matchDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                    {data.matchDistribution.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={["#82ca9d", "#8884d8", "#ffc658"][index % 3]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              ) : <Skeleton className="h-64 w-full" />}
            </section>
          </>
        )}
      </main>
    </ErrorBoundary>
  );
}
