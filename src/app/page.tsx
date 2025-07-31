'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import Link from 'next/link';

export default function Home() {
  const { user, isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            PWA Next.js 애플리케이션
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            React, Zustand, Axios, TypeScript로 구축된 Progressive Web App
          </p>

          {isAuthenticated ? (
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                환영합니다!
              </h2>
              <p className="text-gray-600 mb-4">
                {user?.name}님, 로그인되었습니다.
              </p>
              <p className="text-sm text-gray-500 mb-4">
                이메일: {user?.email}
              </p>
              <p className="text-sm text-gray-500 mb-6">
                역할: {user?.role === 'admin' ? '관리자' : '사용자'}
              </p>
              <Link
                href="/dashboard"
                className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                대시보드로 이동
              </Link>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                시작하기
              </h2>
              <p className="text-gray-600 mb-6">
                계정을 만들거나 로그인하여 서비스를 이용하세요.
              </p>
              <div className="space-y-3">
                <Link
                  href="/login"
                  className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center"
                >
                  로그인
                </Link>
                <Link
                  href="/register"
                  className="block w-full bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors text-center"
                >
                  회원가입
                </Link>
              </div>
            </div>
          )}

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                🚀 PWA 기능
              </h3>
              <p className="text-gray-600">
                오프라인 지원, 홈 화면 설치, 네이티브 앱과 같은 경험을 제공합니다.
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                🔐 JWT 인증
              </h3>
              <p className="text-gray-600">
                안전한 토큰 기반 인증으로 사용자 세션을 관리합니다.
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                📱 반응형 디자인
              </h3>
              <p className="text-gray-600">
                모든 디바이스에서 최적화된 사용자 경험을 제공합니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 