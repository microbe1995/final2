'use client';

import { useAuthAPI, RegisterData } from '@/hooks/useAuthAPI';
import { useAppNavigation } from '@/hooks/useNavigation';
import { useAsyncOperationHelper } from '@/hooks/useAsyncOperation';
import LoginSignupCard from '@/organisms/LoginSignupCard';

// ============================================================================
// 🎯 회원가입 페이지 컴포넌트
// ============================================================================

export default function RegisterPage() {
  const { register } = useAuthAPI();
  const { goToLogin } = useAppNavigation();
  const { isLoading, error, success, executeAsync } = useAsyncOperationHelper();
  
  // ============================================================================
  // 🚀 회원가입 제출
  // ============================================================================
  
  const handleSubmit = async (data: RegisterData) => {
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
        <LoginSignupCard
          type="register"
          onSubmit={handleSubmit}
          className="w-full"
        />
        
        {/* 상태 메시지 표시 */}
        {isLoading && (
          <div className="mt-4 text-center text-blue-500">Signup...</div>
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