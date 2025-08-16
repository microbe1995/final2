'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="mt-6 text-center text-4xl font-extrabold text-gray-900">
          CBMA 프로젝트_GreenSteel
        </h1>
        <p className="mt-4 text-center text-lg text-gray-600">
          마이크로서비스 아키텍처 기반 탄소국경조정메커니즘 계산기
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg rounded-lg sm:px-10">
          <div className="space-y-4">
            <button
              onClick={() => router.push('/login')}
              className="w-full py-3 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              로그인
            </button>

            <button
              onClick={() => router.push('/register')}
              className="w-full py-3 px-4 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              회원가입
            </button>

            <button
              onClick={() => router.push('/dashboard')}
              className="w-full py-3 px-4 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              대시보드
            </button>

            <button
              onClick={() => router.push('/cbam')}
              className="w-full py-3 px-4 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              🏭 CBAM 계산기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 