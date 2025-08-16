'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

// ============================================================================
// 🎯 회원가입 페이지 컴포넌트
// ============================================================================

export default function RegisterPage() {
  const router = useRouter();
  
  // ============================================================================
  // 📝 상태 관리
  // ============================================================================
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirm_password: ''
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [duplicateChecks, setDuplicateChecks] = useState({
    username: { checked: false, available: false },
    email: { checked: false, available: false }
  });

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
  // ✅ 중복 체크 함수
  // ============================================================================
  
  const checkDuplicate = async (type: 'username' | 'email', value: string) => {
    if (!value.trim()) return;
    
    try {
      const response = await axios.get(`${getApiBaseUrl()}/auth/check/${type}/${encodeURIComponent(value)}`);
      const { available } = response.data;
      
      setDuplicateChecks(prev => ({
        ...prev,
        [type]: { checked: true, available }
      }));
      
      if (!available) {
        setErrors(prev => ({
          ...prev,
          [type]: `${type === 'username' ? '사용자명' : '이메일'}이 이미 사용 중입니다.`
        }));
      } else {
        setErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors[type];
          return newErrors;
        });
      }
    } catch (error) {
      console.error(`${type} 중복 체크 오류:`, error);
      setErrors(prev => ({
        ...prev,
        [type]: `${type === 'username' ? '사용자명' : '이메일'} 중복 체크 중 오류가 발생했습니다.`
      }));
    }
  };

  // ============================================================================
  // 🔍 실시간 중복 체크 (디바운스)
  // ============================================================================
  
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // 중복 체크 상태 초기화
    if (field === 'username' || field === 'email') {
      setDuplicateChecks(prev => ({
        ...prev,
        [field]: { checked: false, available: false }
      }));
    }
    
    // 에러 메시지 제거
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // ============================================================================
  // ✅ 폼 검증
  // ============================================================================
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.username.trim()) {
      newErrors.username = '사용자명을 입력해주세요.';
    } else if (formData.username.length < 2) {
      newErrors.username = '사용자명은 2자 이상이어야 합니다.';
    } else if (!/^[가-힣a-zA-Z0-9_]+$/.test(formData.username)) {
      newErrors.username = '사용자명은 한글, 영문, 숫자, 언더스코어만 사용 가능합니다.';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = '이메일을 입력해주세요.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식을 입력해주세요.';
    }
    
    if (!formData.full_name.trim()) {
      newErrors.full_name = '이름을 입력해주세요.';
    }
    
    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
    } else if (formData.password.length < 6) {
      newErrors.password = '비밀번호는 6자 이상이어야 합니다.';
    }
    
    if (!formData.confirm_password) {
      newErrors.confirm_password = '비밀번호 확인을 입력해주세요.';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = '비밀번호가 일치하지 않습니다.';
    }
    
    // 중복 체크 확인
    if (!duplicateChecks.username.checked) {
      newErrors.username = '사용자명 중복 체크를 해주세요.';
    } else if (!duplicateChecks.username.available) {
      newErrors.username = '사용자명이 이미 사용 중입니다.';
    }
    
    if (!duplicateChecks.email.checked) {
      newErrors.email = '이메일 중복 체크를 해주세요.';
    } else if (!duplicateChecks.email.available) {
      newErrors.email = '이메일이 이미 사용 중입니다.';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ============================================================================
  // 🚀 회원가입 제출
  // ============================================================================
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${getApiBaseUrl()}/auth/register`, formData);
      
      if (response.status === 201) {
        alert('회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.');
        router.push('/login');
      }
    } catch (error: any) {
      console.error('회원가입 오류:', error);
      
      if (error.response?.data?.detail) {
        alert(`회원가입 실패: ${error.response.data.detail}`);
      } else {
        alert('회원가입 중 오류가 발생했습니다. 다시 시도해주세요.');
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
            회원가입
          </h1>
          <p className="text-gray-600 dark:text-gray-300 transition-colors duration-200">
            CBAM Calculator 계정을 생성하고 서비스를 이용해보세요
          </p>
        </div>

        {/* 회원가입 폼 */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 사용자명 필드 */}
            <div className="form-field">
              <label htmlFor="username" className="form-label">
                사용자명 *
              </label>
              <div className="flex gap-2">
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className={`form-input flex-1 ${errors.username ? 'error' : ''}`}
                  placeholder="사용자명을 입력하세요"
                />
                <button
                  type="button"
                  onClick={() => checkDuplicate('username', formData.username)}
                  disabled={!formData.username.trim() || duplicateChecks.username.checked}
                  className="btn btn-secondary px-4 py-2 text-sm whitespace-nowrap"
                >
                  {duplicateChecks.username.checked 
                    ? (duplicateChecks.username.available ? '✅' : '❌')
                    : '중복체크'
                  }
                </button>
              </div>
              {errors.username && <p className="form-error">{errors.username}</p>}
              {duplicateChecks.username.checked && (
                <p className={`text-sm ${duplicateChecks.username.available ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {duplicateChecks.username.available ? '사용 가능한 사용자명입니다.' : '이미 사용 중인 사용자명입니다.'}
                </p>
              )}
            </div>

            {/* 이메일 필드 */}
            <div className="form-field">
              <label htmlFor="email" className="form-label">
                이메일 *
              </label>
              <div className="flex gap-2">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className={`form-input flex-1 ${errors.email ? 'error' : ''}`}
                  placeholder="이메일을 입력하세요"
                />
                <button
                  type="button"
                  onClick={() => checkDuplicate('email', formData.email)}
                  disabled={!formData.email.trim() || duplicateChecks.email.checked}
                  className="btn btn-secondary px-4 py-2 text-sm whitespace-nowrap"
                >
                  {duplicateChecks.email.checked 
                    ? (duplicateChecks.email.available ? '✅' : '❌')
                    : '중복체크'
                  }
                </button>
              </div>
              {errors.email && <p className="form-error">{errors.email}</p>}
              {duplicateChecks.email.checked && (
                <p className={`text-sm ${duplicateChecks.email.available ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {duplicateChecks.email.available ? '사용 가능한 이메일입니다.' : '이미 사용 중인 이메일입니다.'}
                </p>
              )}
            </div>

            {/* 이름 필드 */}
            <div className="form-field">
              <label htmlFor="full_name" className="form-label">
                이름 *
              </label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                autoComplete="name"
                required
                value={formData.full_name}
                onChange={(e) => handleInputChange('full_name', e.target.value)}
                className={`form-input ${errors.full_name ? 'error' : ''}`}
                placeholder="이름을 입력하세요"
              />
              {errors.full_name && <p className="form-error">{errors.full_name}</p>}
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
                autoComplete="new-password"
                required
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="비밀번호를 입력하세요 (6자 이상)"
              />
              {errors.password && <p className="form-error">{errors.password}</p>}
            </div>

            {/* 비밀번호 확인 필드 */}
            <div className="form-field">
              <label htmlFor="confirm_password" className="form-label">
                비밀번호 확인 *
              </label>
              <input
                id="confirm_password"
                name="confirm_password"
                type="password"
                autoComplete="new-password"
                required
                value={formData.confirm_password}
                onChange={(e) => handleInputChange('confirm_password', e.target.value)}
                className={`form-input ${errors.confirm_password ? 'error' : ''}`}
                placeholder="비밀번호를 다시 입력하세요"
              />
              {errors.confirm_password && <p className="form-error">{errors.confirm_password}</p>}
            </div>

            {/* 제출 버튼 */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full py-3 text-lg font-medium"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  회원가입 중...
                </div>
              ) : (
                '회원가입 완료'
              )}
            </button>
          </form>
        </div>

        {/* 로그인 링크 */}
        <div className="text-center mt-6">
          <p className="text-gray-600 dark:text-gray-300 transition-colors duration-200">
            이미 계정이 있으신가요?{' '}
            <a
              href="/login"
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors"
            >
              로그인하기
            </a>
          </p>
        </div>
      </div>
    </div>
  );
} 