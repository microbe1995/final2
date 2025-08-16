'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

// ============================================================================
// 🎯 로그인 페이지 컴포넌트
// ============================================================================

export default function LoginPage() {
  const router = useRouter();
  
  // ============================================================================
  // 📝 상태 관리
  // ============================================================================
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  // ============================================================================
  // 🔧 API URL 설정
  // ============================================================================
  
  const getApiBaseUrl = () => {
    if (typeof window !== 'undefined') {
      return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1';
    }
    return 'http://localhost:8080/api/v1';
  };

  // ============================================================================
  // ✅ 폼 검증
  // ============================================================================
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.email.trim()) {
      newErrors.email = '이메일을 입력해주세요.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식을 입력해주세요.';
    }
    
    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ============================================================================
  // 🚀 로그인 제출
  // ============================================================================
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${getApiBaseUrl()}/auth/login`, formData);
      
      if (response.status === 200) {
        const { access_token, user } = response.data;
        
        // 토큰을 로컬 스토리지에 저장 (실제로는 더 안전한 방법 사용)
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        alert(`🎉 로그인 성공!\n\n환영합니다, ${user.username}님!`);
        router.push('/'); // 홈페이지로 이동
      }
    } catch (error: any) {
      console.error('로그인 오류:', error);
      
      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      } else if (error.response?.status === 401) {
        setErrors({ general: '이메일 또는 비밀번호가 올바르지 않습니다.' });
      } else {
        setErrors({ general: '로그인 중 오류가 발생했습니다. 다시 시도해주세요.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-200">
      <div className="max-w-md mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 transition-colors duration-200">
            로그인
          </h1>
          <p className="text-gray-600 dark:text-gray-300 transition-colors duration-200">
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
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder="이메일을 입력하세요"
              />
              {errors.email && <p className="form-error">{errors.email}</p>}
            </div>

            {/* 비밀번호 필드 */}
            <div className="form-field">
              <label htmlFor="password" className="form-label">
                비밀번호 *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="비밀번호를 입력하세요"
              />
              {errors.password && <p className="form-error">{errors.password}</p>}
            </div>

            {/* 일반 오류 메시지 */}
            {errors.general && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-800 dark:text-red-200 text-sm">{errors.general}</p>
              </div>
            )}

            {/* 제출 버튼 */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full py-3 text-lg font-medium"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  로그인 중...
                </div>
              ) : (
                '로그인'
              )}
            </button>
          </form>
        </div>

        {/* 추가 링크 */}
        <div className="text-center mt-6 space-y-3">
          <p className="text-gray-600 dark:text-gray-300 transition-colors duration-200">
            계정이 없으신가요?{' '}
            <a
              href="/register"
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors"
            >
              회원가입하기
            </a>
          </p>
          
          <p className="text-gray-600 dark:text-gray-300 transition-colors duration-200">
            <a
              href="/"
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 font-medium transition-colors"
            >
              ← 홈으로 돌아가기
            </a>
          </p>
        </div>
      </div>
    </div>
  );
} 