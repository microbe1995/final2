'use client';

import { useAuthStore } from '@/zustand/authStore';
import { useAuthAPI } from '@/hooks/useAuthAPI';
import { useNavigation } from '@/hooks/useNavigation';
import { useAsyncOperation } from '@/hooks/useAsyncOperation';
import AuthForm from '@/organisms/AuthForm';

// ============================================================================
// 🔑 로그인 페이지 컴포넌트
// ============================================================================

export default function LoginPage() {
  const { login } = useAuthStore();
  const { login: loginAPI } = useAuthAPI();
  const { goToProfile } = useNavigation();
  const { isLoading, error, success, executeAsync } = useAsyncOperation();
  
  // ============================================================================
  // 🚀 로그인 제출
  // ============================================================================
  
  const handleSubmit = async (data: { email: string; password: string }) => {
    const result = await executeAsync(
      async () => {
        const response = await loginAPI(data);
        
        if (response.success && response.data) {
          // AuthStore를 통해 로그인 상태 업데이트
          login(response.data.user, response.data.token);
          alert(response.message);
          goToProfile(); // 프로필 페이지로 이동
        }
        
        return response;
      },
      '로그인이 완료되었습니다!'
    );
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-[#0b0c0f] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <AuthForm
          type="login"
          onSubmit={handleSubmit}
          className="w-full"
        />
        
        {/* 상태 메시지 표시 */}
        {isLoading && (
          <div className="mt-4 text-center text-blue-500">Login...</div>
        )}
        {error && (
          <div className="mt-4 text-center text-red-500">{error}</div>
        )}
        {success && (
          <div className="mt-4 text-center text-green-500">{success}</div>
        )}
      </div>
    </div>
  );
} 