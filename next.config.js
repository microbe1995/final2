const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: false
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    JWT_SECRET: process.env.JWT_SECRET || 'your-secret-key',
    API_URL: process.env.API_URL || 'http://localhost:3000/api',
  },
  images: {
    domains: ['localhost', 'vercel.app'],
  },
}

module.exports = withPWA(nextConfig) 