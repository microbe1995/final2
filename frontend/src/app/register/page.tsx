'use client';

import { useAuthAPI } from '@/hooks/useAuthAPI';
import { useNavigation } from '@/hooks/useNavigation';
import { useAsyncOperation } from '@/hooks/useAsyncOperation';
import AuthForm from '@/organisms/AuthForm';

// ============================================================================
// 🎯 회원가입 페이지 컴포넌트
// ============================================================================

export default function RegisterPage() {
  const { register } = useAuthAPI();
  const { goToLogin } = useNavigation();
  const { isLoading, error, success, executeAsync } = useAsyncOperation();
  
  // ============================================================================
  // 🚀 회원가입 제출
  // ============================================================================
  
  const handleSubmit = async (data: { email: string; password: string; fullName?: string; confirmPassword?: string }) => {
    const result = await executeAsync(
      async () => {
        const response = await register(data);
        
        if (response.success) {
          alert(response.message);
          goToLogin(); // 로그인 페이지로 이동
        }
        
        return response;
      },
      '회원가입이 완료되었습니다!'
    );
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-[#0b0c0f] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <AuthForm
          type="register"
          onSubmit={handleSubmit}
          className="w-full"
        />
        
        {/* 상태 메시지 표시 */}
        {isLoading && (
          <div className="mt-4 text-center text-blue-500">회원가입 중...</div>
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