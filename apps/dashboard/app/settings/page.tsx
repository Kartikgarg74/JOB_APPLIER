"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

export default function SettingsPage() {
  const [theme, setTheme] = useState("system");
  const [notifications, setNotifications] = useState({ email: true, push: false });
  const [jobPrefs, setJobPrefs] = useState({ remote: true, companySize: "any", industry: "any" });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSettings();
  }, []);

  async function fetchSettings() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/settings");
      if (!res.ok) throw new Error("Failed to fetch settings");
      const data = await res.json();
      setTheme(data.theme);
      setNotifications(data.notifications);
      setJobPrefs(data.jobPrefs);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme, notifications, jobPrefs }),
      });
      if (!res.ok) throw new Error("Failed to save settings");
      setMessage("Settings saved!");
      setTimeout(() => setMessage(""), 2000);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 bg-white rounded-lg shadow-md mt-6">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500 mb-2">Error: {error}</div>}
      <form onSubmit={handleSave} className="space-y-6">
        <section>
          <h2 className="text-xl font-semibold mb-2">Theme</h2>
          <div className="flex gap-4">
            <label>
              <input type="radio" name="theme" value="light" checked={theme === "light"} onChange={() => setTheme("light")}/>
              Light
            </label>
            <label>
              <input type="radio" name="theme" value="dark" checked={theme === "dark"} onChange={() => setTheme("dark")}/>
              Dark
            </label>
            <label>
              <input type="radio" name="theme" value="system" checked={theme === "system"} onChange={() => setTheme("system")}/>
              System
            </label>
          </div>
        </section>
        <section>
          <h2 className="text-xl font-semibold mb-2">Notifications</h2>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={notifications.email} onChange={e => setNotifications(n => ({ ...n, email: e.target.checked }))}/>
            Email notifications
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={notifications.push} onChange={e => setNotifications(n => ({ ...n, push: e.target.checked }))}/>
            Push notifications
          </label>
        </section>
        <section>
          <h2 className="text-xl font-semibold mb-2">Job Search Preferences</h2>
          <label className="block mb-2">
            <input type="checkbox" checked={jobPrefs.remote} onChange={e => setJobPrefs(p => ({ ...p, remote: e.target.checked }))}/>
            Remote jobs only
          </label>
          <label className="block mb-2">
            Company size:
            <select value={jobPrefs.companySize} onChange={e => setJobPrefs(p => ({ ...p, companySize: e.target.value }))} className="ml-2 border rounded px-2 py-1">
              <option value="any">Any</option>
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </label>
          <label className="block mb-2">
            Industry:
            <input type="text" value={jobPrefs.industry} onChange={e => setJobPrefs(p => ({ ...p, industry: e.target.value }))} className="ml-2 border rounded px-2 py-1" placeholder="Any"/>
          </label>
        </section>
        <div className="flex gap-4 items-center">
          <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 focus:outline-none focus:ring" disabled={loading}>
            Save Settings
          </button>
          <Link href="/profile" className="text-blue-600 underline">
            Edit Profile
          </Link>
        </div>
        {message && <div className="text-green-600 font-semibold">{message}</div>}
      </form>
    </div>
  );
}
