'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import AuthForm from '@/organisms/AuthForm';
import axios from 'axios';

// ============================================================================
// 🔑 로그인 페이지 컴포넌트
// ============================================================================

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  
  // ============================================================================
  // 🚀 로그인 제출
  // ============================================================================
  
  const handleSubmit = async (data: { email: string; password: string }) => {
    try {
      console.log('🔍 로그인 요청 데이터:', data);
      console.log('🔍 API URL:', `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/login`);
      
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/login`,
        data
      );
      
      console.log('✅ 로그인 응답:', response.data);

      if (response.data && response.data.user && response.data.token) {
        // AuthContext를 통해 로그인 상태 업데이트
        login(response.data.user, response.data.token);
        
        alert('로그인이 완료되었습니다!');
        router.push('/profile'); // 프로필 페이지로 직접 이동
      } else {
        throw new Error(response.data.message || '로그인에 실패했습니다');
      }
    } catch (error: any) {
      console.error('❌ 로그인 오류:', error);
      alert(error.message || '로그인에 실패했습니다');
    }
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <AuthForm
          type="login"
          onSubmit={handleSubmit}
          className="w-full"
        />
      </div>
    </div>
  );
} 