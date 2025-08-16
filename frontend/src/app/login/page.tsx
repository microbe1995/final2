'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import axios from 'axios';

// ============================================================================
// 🔑 로그인 페이지 컴포넌트
// ============================================================================

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  
  // ============================================================================
  // 📝 상태 관리
  // ============================================================================
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  
  const [validation, setValidation] = useState({
    email: { isValid: false, message: '' },
    password: { isValid: false, message: '' }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // ============================================================================
  // 📝 폼 입력 처리
  // ============================================================================
  
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');

    // 실시간 유효성 검사
    switch (field) {
      case 'email':
        const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        setValidation(prev => ({
          ...prev,
          email: {
            isValid: emailValid,
            message: emailValid ? '' : '올바른 이메일 형식을 입력해주세요'
          }
        }));
        break;

      case 'password':
        const passwordValid = value.length >= 1;
        setValidation(prev => ({
          ...prev,
          password: {
            isValid: passwordValid,
            message: passwordValid ? '' : '비밀번호를 입력해주세요'
          }
        }));
        break;
    }
  };

  // ============================================================================
  // 🚀 로그인 제출
  // ============================================================================
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 전체 유효성 검사
    if (!validation.email.isValid || !validation.password.isValid) {
      setError('모든 필드를 올바르게 입력해주세요');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('🔍 로그인 요청 데이터:', formData);
      console.log('🔍 API URL:', `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/login`);
      
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/login`,
        formData
      );
      
      console.log('✅ 로그인 응답:', response.data);

      if (response.data && response.data.user && response.data.token) {
        // AuthContext를 통해 로그인 상태 업데이트
        login(response.data.user, response.data.token);
        
        alert('로그인이 완료되었습니다!');
        router.push('/profile'); // 프로필 페이지로 직접 이동
      }
    } catch (error: any) {
      console.error('❌ 로그인 오류:', error);
      console.error('❌ 에러 응답:', error.response);
      console.error('❌ 에러 상태:', error.response?.status);
      console.error('❌ 에러 데이터:', error.response?.data);
      
      let errorMessage = '로그인 중 오류가 발생했습니다';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 401) {
        errorMessage = '이메일 또는 비밀번호가 올바르지 않습니다.';
      } else if (error.response?.status === 400) {
        errorMessage = '잘못된 요청 데이터입니다. 입력값을 확인해주세요.';
      } else if (error.response?.status === 500) {
        errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            로그인
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            CBAM Calculator 계정으로 로그인하세요
          </p>
        </div>

        {/* 로그인 폼 */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 이메일 필드 */}
            <div className="form-field">
              <label htmlFor="email" className="form-label">
                이메일 *
              </label>
              <input
                type="email"
                id="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="이메일을 입력하세요"
                className={`form-input ${validation.email.isValid ? 'border-green-500' : validation.email.message ? 'border-red-500' : ''}`}
                required
              />
              {validation.email.message && (
                <div className="form-error">
                  {validation.email.message}
                </div>
              )}
            </div>

            {/* 비밀번호 필드 */}
            <div className="form-field">
              <label htmlFor="password" className="form-label">
                비밀번호 *
              </label>
              <input
                type="password"
                id="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                placeholder="비밀번호를 입력하세요"
                className={`form-input ${validation.password.isValid ? 'border-green-500' : validation.password.message ? 'border-red-500' : ''}`}
                required
              />
              {validation.password.message && (
                <div className="form-error">
                  {validation.password.message}
                </div>
              )}
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="form-error">
                {error}
              </div>
            )}

            {/* 로그인 버튼 */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </button>

            {/* 회원가입 링크 */}
            <div className="text-center">
              <p className="text-gray-600 dark:text-gray-400">
                계정이 없으신가요?{' '}
                <a
                  href="/register"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 font-medium transition-colors duration-200"
                >
                  SignUp
                </a>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 