import type { NextConfig } from "next";

// Backend (ModelForge FastAPI service) URL. Same idea as the old Vite
// `server.proxy` config in model_forge_v2/frontend/vite.config.ts — the
// browser calls relative "/api/..." paths and Next.js forwards them to the
// FastAPI backend, so no CORS/base-URL plumbing is needed in the UI code.
const BACKEND_URL = process.env.MODELFORGE_BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
