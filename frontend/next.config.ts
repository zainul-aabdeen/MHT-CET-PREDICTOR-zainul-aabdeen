import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allows local testing (optional, safe for dev)
// allowedDevOrigins: ['192.168.1.103', 'localhost'], // removed for production

  // Proxy API requests to the Python backend running on port 8000
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://mht-cet-predictor-zainul-aabdeen.onrender.com/api/:path*', // Proxy to Production Backend
      },
    ];
  },
};

export default nextConfig;