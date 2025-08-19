'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/zustand/authStore';
import { useAuthAPI } from '@/hooks/useAuthAPI';
import { useAppNavigation } from '@/hooks/useNavigation';
import { useAsync } from '@/hooks';
import ProfileForm from '@/organisms/ProfileForm';
import Button from '@/atoms/Button';

// ============================================================================
// 👤 프로필 페이지 컴포넌트
// ============================================================================

export default function ProfilePage() {
  // ============================================================================
  // 🎯 상태 및 훅 사용 - 단일 책임
  // ============================================================================
  
  const { user, token, isAuthenticated, updateUser, logout } = useAuthStore();
  const { updateProfile, changePassword } = useAuthAPI();
  const { goToLogin } = useAppNavigation();
  const { isLoading, error, success, execute } = useAsync();

  // ============================================================================
  // 🔄 초기화 - 인증 상태 확인
  // ============================================================================
  
  useEffect(() => {
    if (!isAuthenticated) {
      goToLogin();
    }
  }, [isAuthenticated, goToLogin]);

  // ============================================================================
  // 🚀 프로필 업데이트 - 단일 책임
  // ============================================================================
  
  const handleUpdateProfile = async (data: { full_name: string; email: string }) => {
    if (!token) return;

    await execute(
      async () => {
        const response = await updateProfile(data, token);
        
        if (response?.success && response?.data) {
          updateUser({
            ...user!,
            full_name: data.full_name,
            email: data.email
          });
        }
        
        return response;
      },
      { successMessage: '프로필이 성공적으로 업데이트되었습니다.' }
    );
  };

  // ============================================================================
  // 🔐 비밀번호 변경 - 단일 책임
  // ============================================================================
  
  const handleUpdatePassword = async (data: { current_password: string; new_password: string; confirm_password: string }) => {
    if (!token) return;

    await execute(
      async () => {
        const response = await changePassword(data, token);
        return response;
      },
      { successMessage: '비밀번호가 성공적으로 변경되었습니다.' }
    );
  };

  // ============================================================================
  // 🚪 로그아웃 - 단일 책임
  // ============================================================================
  
  const handleLogout = () => {
    logout();
    goToLogin();
  };

  // ============================================================================
  // 🎨 렌더링 - 조건부 렌더링
  // ============================================================================
  
  if (!isAuthenticated || !user) {
    return null; // 로그인 페이지로 리다이렉트 중
  }

  return (
    <div className="min-h-screen bg-[#0b0c0f] flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="bg-[#1e293b] rounded-lg shadow-lg p-6 border border-[#334155]">
          {/* 헤더 */}
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-white mb-2">프로필 관리</h1>
            <p className="text-[#cbd5e1]">사용자 정보를 관리하고 업데이트하세요</p>
          </div>

          {/* 사용자 정보 표시 */}
          <div className="mb-6 p-4 bg-[#334155] rounded-lg">
            <h2 className="text-lg font-semibold text-white mb-3">현재 정보</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[#cbd5e1]">
              <div>
                <span className="font-medium">이름:</span> {user.full_name}
              </div>
              <div>
                <span className="font-medium">이메일:</span> {user.email}
              </div>
              <div>
                <span className="font-medium">역할:</span> {user.role}
              </div>
              <div>
                <span className="font-medium">ID:</span> {user.id}
              </div>
            </div>
          </div>

          {/* 상태 메시지 */}
          {isLoading && (
            <div className="mb-4 text-center text-blue-500">처리 중...</div>
          )}
          {error && (
            <div className="mb-4 text-center text-red-500">{error}</div>
          )}
          {success && (
            <div className="mb-4 text-center text-green-500">{success}</div>
          )}

          {/* 프로필 폼 */}
          <ProfileForm
            user={user}
            onSubmit={handleUpdateProfile}
            isLoading={isLoading}
          />

          {/* 비밀번호 변경 폼 */}
          <div className="mt-8 pt-6 border-t border-[#475569]">
            <h3 className="text-lg font-semibold text-white mb-4">비밀번호 변경</h3>
            <ProfileForm
              onSubmit={handleUpdatePassword}
              isLoading={isLoading}
              isPasswordChange={true}
            />
          </div>

          {/* 로그아웃 버튼 */}
          <div className="mt-8 text-center">
            <Button
              onClick={handleLogout}
              variant="danger"
              className="px-6 py-2"
            >
              Logout
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
