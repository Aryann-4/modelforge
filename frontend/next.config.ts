import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // API routes in src/app/api/ handle /api/v1/* directly (serverless).
  // To use the separate FastAPI backend instead, uncomment below:
  // async rewrites() {
  //   return [
  //     {
  //       source: "/api/:path*",
  //       destination: `${process.env.MODELFORGE_BACKEND_URL || "http://localhost:8000"}/api/:path*`,
  //     },
  //   ];
  // },
};

export default nextConfig;
