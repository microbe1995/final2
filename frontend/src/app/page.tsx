'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="mt-6 text-center text-4xl font-extrabold text-gray-900">
          LCA Final Project
        </h1>
        <p className="mt-4 text-center text-lg text-gray-600">
          마이크로서비스 아키텍처 기반 LCA 시스템
        </p>
        <p className="mt-2 text-center text-sm text-gray-500">
          Next.js + FastAPI + Docker
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10">
          <div className="space-y-6">
            <div>
              <button
                onClick={() => router.push('/login')}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                로그인
              </button>
            </div>

            <div>
              <button
                onClick={() => router.push('/register')}
                className="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                회원가입
              </button>
            </div>

            <div>
              <button
                onClick={() => router.push('/dashboard')}
                className="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                대시보드
              </button>
            </div>

            <div>
              <button
                onClick={() => router.push('/cbam')}
                className="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                🏭 CBAM 계산기
              </button>
            </div>
          </div>

          <div className="mt-8 text-center text-xs text-gray-500">
            <p>🔧 프론트엔드: Next.js + TypeScript + Zustand</p>
            <p>🚀 백엔드: FastAPI Gateway + MSA</p>
            <p>🐳 컨테이너: Docker + Docker Compose</p>
          </div>
        </div>
      </div>
    </div>
  );
} 