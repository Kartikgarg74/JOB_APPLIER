// [CONTEXT] Custom sign-in page for NextAuth.js
"use client";

import { signIn } from "next-auth/react";
import { FcGoogle } from "react-icons/fc";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { FaLinkedin, FaGithub, FaFacebook, FaTwitter } from "react-icons/fa";

export default function SignInPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const result = await signIn("credentials", {
      redirect: false,
      username,
      password,
    });

    if (result?.error) {
      setError(result.error);
    } else {
      router.push("/"); // Redirect to dashboard on successful login
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="px-8 py-6 mt-4 text-left bg-white shadow-lg rounded-lg">
        <h3 className="text-2xl font-bold text-center">
          Login to your account
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="mt-4">
            <div>
              <label className="block" htmlFor="username">
                Username
              </label>
              <input
                type="text"
                placeholder="Username"
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="mt-4">
              <label className="block" htmlFor="password">
                Password
              </label>
              <input
                type="password"
                placeholder="Password"
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            <div className="flex items-baseline justify-between">
              <button
                type="submit"
                className="px-6 py-2 mt-4 text-white bg-blue-600 rounded-lg hover:bg-blue-900"
              >
                Login
              </button>
              <a href="#" className="text-sm text-blue-600 hover:underline">
                Forgot password?
              </a>
            </div>
          </div>
        </form>
        <div className="mt-6">
          <button
            onClick={() => signIn("google", { callbackUrl: "/profile" })}
            className="flex w-full items-center justify-center space-x-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <FcGoogle className="h-6 w-6" />
            <span>Sign in with Google</span>
          </button>
          <div className="flex flex-col gap-2 mt-4">
            <button
              disabled
              className="flex w-full items-center justify-center space-x-2 rounded-md border border-gray-300 bg-gray-100 px-4 py-2 text-gray-400 cursor-not-allowed"
              title="Coming Soon"
            >
              <FaLinkedin className="h-6 w-6" />
              <span>Sign in with LinkedIn (Coming Soon)</span>
            </button>
            <button
              disabled
              className="flex w-full items-center justify-center space-x-2 rounded-md border border-gray-300 bg-gray-100 px-4 py-2 text-gray-400 cursor-not-allowed"
              title="Coming Soon"
            >
              <FaGithub className="h-6 w-6" />
              <span>Sign in with GitHub (Coming Soon)</span>
            </button>
            <button
              disabled
              className="flex w-full items-center justify-center space-x-2 rounded-md border border-gray-300 bg-gray-100 px-4 py-2 text-gray-400 cursor-not-allowed"
              title="Coming Soon"
            >
              <FaFacebook className="h-6 w-6" />
              <span>Sign in with Facebook (Coming Soon)</span>
            </button>
            <button
              disabled
              className="flex w-full items-center justify-center space-x-2 rounded-md border border-gray-300 bg-gray-100 px-4 py-2 text-gray-400 cursor-not-allowed"
              title="Coming Soon"
            >
              <FaTwitter className="h-6 w-6" />
              <span>Sign in with Twitter (Coming Soon)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
