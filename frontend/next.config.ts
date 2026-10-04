import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_SERVICE_URL ||
      process.env.BACKEND_URL ||
      (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");

    if (backendUrl) {
      return [
        {
          source: "/api/:path*",
          destination: `${backendUrl}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
