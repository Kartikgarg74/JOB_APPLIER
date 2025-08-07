/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@repo/ui"],
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "avatars.githubusercontent.com",
        port: "",
        pathname: "/**",
      },
    ],
  },
  async headers() {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self'; font-src 'self'; connect-src 'self' ${supabaseUrl} *.supabase.co;`,
          },
        ],
      },
    ];
  },
  rewrites: async () => {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NEXT_PUBLIC_AGENT_ORCHESTRATION_SERVICE_URL ? `${process.env.NEXT_PUBLIC_AGENT_ORCHESTRATION_SERVICE_URL}/:path*` : "http://localhost:8000/:path*",
      },
      {
        source: "/api/job-applications",
        destination: "/api/job-applications",


      },
    ];
  },
};

export default nextConfig;
