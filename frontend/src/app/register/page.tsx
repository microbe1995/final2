'use client';

import { useRouter } from 'next/navigation';
import AuthForm from '@/organisms/AuthForm';
import axios from 'axios';

// ============================================================================
// 🎯 회원가입 페이지 컴포넌트
// ============================================================================

export default function RegisterPage() {
  const router = useRouter();
  
  // ============================================================================
  // 🚀 회원가입 제출
  // ============================================================================
  
  const handleSubmit = async (data: { email: string; password: string; fullName?: string; confirmPassword?: string }) => {
    try {
      console.log('🔍 회원가입 요청 데이터:', data);
      console.log('🔍 API URL:', `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/register`);
      
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/register`,
        data
      );
      
      console.log('✅ 회원가입 응답:', response.data);

      if (response.status === 200 || response.status === 201) {
        alert('회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.');
        router.push('/login');
      } else {
        throw new Error(response.data.message || '회원가입에 실패했습니다');
      }
    } catch (error: any) {
      console.error('❌ 회원가입 오류:', error);
      alert(error.message || '회원가입에 실패했습니다');
    }
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <AuthForm
          type="register"
          onSubmit={handleSubmit}
          className="w-full"
        />
      </div>
    </div>
  );
} 