'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function DashboardPage() {
  const { user, isAuthenticated, logout, checkAuth } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    const initAuth = async () => {
      const isAuth = await checkAuth();
      if (!isAuth) {
        router.push('/login');
      }
    };
    initAuth();
  }, [checkAuth, router]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
              <p className="text-gray-600 mt-2">
                환영합니다, {user.name}님!
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {user.role === 'admin' ? '관리자' : '사용자'}
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>

        {/* 사용자 정보 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">사용자 정보</h3>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-500">이름:</span>
                <p className="font-medium">{user.name}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">이메일:</span>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">역할:</span>
                <p className="font-medium">
                  {user.role === 'admin' ? '관리자' : '사용자'}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-500">가입일:</span>
                <p className="font-medium">
                  {new Date(user.createdAt).toLocaleDateString('ko-KR')}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">PWA 기능</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">오프라인 지원</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">홈 화면 설치</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">푸시 알림</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">반응형 디자인</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">보안 상태</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">JWT 토큰 인증</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">HTTPS 보안</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">세션 관리</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm">자동 로그아웃</span>
              </div>
            </div>
          </div>
        </div>

        {/* 기능 카드들 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">통계</h3>
            <p className="text-gray-600 text-sm">사용 통계 및 분석</p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">⚙️</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">설정</h3>
            <p className="text-gray-600 text-sm">계정 및 앱 설정</p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">🔔</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">알림</h3>
            <p className="text-gray-600 text-sm">푸시 알림 관리</p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
            <div className="text-4xl mb-4">📱</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">설치</h3>
            <p className="text-gray-600 text-sm">홈 화면에 설치</p>
          </div>
        </div>
      </div>
    </div>
  );
} 