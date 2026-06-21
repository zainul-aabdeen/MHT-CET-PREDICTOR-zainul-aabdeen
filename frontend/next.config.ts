import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allows you to test on your phone using your computer's local IP address
  // (Note: Next.js 15+ requires this to avoid Invalid Host header errors)
  allowedDevOrigins: ['192.168.1.103', 'localhost'],

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*', // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
