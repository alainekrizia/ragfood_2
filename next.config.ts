import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  telemetry: false,
  typescript: {
    tsconfigPath: './tsconfig.json',
  },
}

export default nextConfig
