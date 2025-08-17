'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/zustand/authStore';
import axios from 'axios';
import ProfileForm from '@/organisms/ProfileForm';
import Button from '@/atoms/Button';

// ============================================================================
// 👤 프로필 페이지 컴포넌트
// ============================================================================

export default function ProfilePage() {
  const router = useRouter();
  const { user, token, isAuthenticated, updateUser, logout } = useAuthStore();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // ============================================================================
  // 🔄 초기화 (사용자 정보 로드)
  // ============================================================================
  
  useEffect(() => {
    // 인증되지 않은 경우 로그인 페이지로 이동
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
  }, [isAuthenticated, router]);

  // ============================================================================
  // 🚀 프로필 업데이트
  // ============================================================================
  
  const handleUpdateProfile = async (data: { full_name: string; email: string }) => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.put(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080'}/api/v1/auth/profile`,
        data,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data) {
        // AuthStore의 사용자 정보 업데이트
        updateUser({
          ...user!,
          full_name: data.full_name,
          email: data.email
        });
        
        setSuccess('프로필이 성공적으로 업데이트되었습니다.');
      }
    } catch (error: any) {
      console.error('프로필 업데이트 오류:', error);
      setError(error.response?.data?.detail || '프로필 업데이트 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🔐 비밀번호 변경
  // ============================================================================
  
  const handleUpdatePassword = async (data: { current_password: string; new_password: string; confirm_password: string }) => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.put(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080'}/api/v1/auth/password`,
        {
          current_password: data.current_password,
          new_password: data.new_password
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data) {
        setSuccess('비밀번호가 성공적으로 변경되었습니다.');
      }
    } catch (error: any) {
      console.error('비밀번호 변경 오류:', error);
      setError(error.response?.data?.detail || '비밀번호 변경 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🚪 로그아웃
  // ============================================================================
  
  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  if (!user) {
    return (
      <div className="min-h-screen bg-[#0b0c0f] flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-gray-600 mb-4">사용자 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0c0f]">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            프로필 관리
          </h1>
          <p className="text-[#cbd5e1]">
            개인정보와 비밀번호를 안전하게 관리하세요
          </p>
        </div>

        {/* 프로필 폼 */}
        <ProfileForm
          user={user}
          onUpdateProfile={handleUpdateProfile}
          onUpdatePassword={handleUpdatePassword}
          isLoading={isLoading}
          error={error}
          success={success}
        />

        {/* 로그아웃 버튼 */}
        <div className="mt-8 text-center">
          <Button
            onClick={handleLogout}
            variant="danger"
            className="px-8 py-3"
          >
            로그아웃
          </Button>
        </div>
      </div>
    </div>
  );
}
