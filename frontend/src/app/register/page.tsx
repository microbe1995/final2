'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

// ============================================================================
// 🎯 회원가입 페이지 컴포넌트
// ============================================================================

export default function RegisterPage() {
  const router = useRouter();
  
  // ============================================================================
  // 📝 상태 관리
  // ============================================================================
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [validation, setValidation] = useState({
    fullName: { isValid: false, message: '' },
    email: { isValid: false, message: '', isChecking: false, isChecked: false },
    password: { isValid: false, message: '' },
    confirmPassword: { isValid: false, message: '' }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // ============================================================================
  // 🔍 이메일 중복 체크 (수동 버튼 클릭)
  // ============================================================================
  
  const checkEmailAvailability = useCallback(async () => {
    const email = formData.email;
    
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setValidation(prev => ({
        ...prev,
        email: { 
          ...prev.email, 
          isValid: false, 
          message: '올바른 이메일 형식을 입력해주세요', 
          isChecking: false,
          isChecked: false
        }
      }));
      return;
    }

    setValidation(prev => ({
      ...prev,
      email: { 
        ...prev.email, 
        isChecking: true, 
        message: '중복 확인 중...',
        isChecked: false
      }
    }));

    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/check/email/${encodeURIComponent(email)}`
      );

      if (response.data.available) {
        setValidation(prev => ({
          ...prev,
          email: { 
            isValid: true, 
            message: response.data.message, 
            isChecking: false,
            isChecked: true
          }
        }));
      } else {
        setValidation(prev => ({
          ...prev,
          email: { 
            isValid: false, 
            message: response.data.message, 
            isChecking: false,
            isChecked: true
          }
        }));
      }
    } catch (error: any) {
      console.error('이메일 중복 체크 오류:', error);
      setValidation(prev => ({
        ...prev,
        email: { 
          isValid: false, 
          message: '이메일 중복 체크 중 오류가 발생했습니다', 
          isChecking: false,
          isChecked: false
        }
      }));
    }
  }, [formData.email]);

  // ============================================================================
  // 📝 폼 입력 처리
  // ============================================================================
  
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');

    // 실시간 유효성 검사
    switch (field) {
      case 'fullName':
        const fullNameValid = value.length >= 2 && value.length <= 100;
        setValidation(prev => ({
          ...prev,
          fullName: {
            isValid: fullNameValid,
            message: fullNameValid ? '' : '이름은 2-100자 사이여야 합니다'
          }
        }));
        break;

      case 'email':
        const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        setValidation(prev => ({
          ...prev,
          email: {
            ...prev.email,
            isValid: emailValid,
            message: emailValid ? '' : '올바른 이메일 형식을 입력해주세요'
          }
        }));
        break;

      case 'password':
        const passwordValid = value.length >= 6;
        setValidation(prev => ({
          ...prev,
          password: {
            isValid: passwordValid,
            message: passwordValid ? '' : '비밀번호는 최소 6자 이상이어야 합니다'
          }
        }));
        break;

      case 'confirmPassword':
        const confirmValid = value === formData.password;
        setValidation(prev => ({
          ...prev,
          confirmPassword: {
            isValid: confirmValid,
            message: confirmValid ? '' : '비밀번호가 일치하지 않습니다'
          }
        }));
        break;
    }
  };

  // ============================================================================
  // 🚀 회원가입 제출
  // ============================================================================
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 이메일 중복체크 완료 여부 확인
    if (!validation.email.isChecked) {
      setError('이메일 중복체크를 먼저 진행해주세요');
      return;
    }
    
    // 전체 유효성 검사
    if (!validation.fullName.isValid || !validation.email.isValid || 
        !validation.password.isValid || !validation.confirmPassword.isValid) {
      setError('모든 필드를 올바르게 입력해주세요');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const requestData = {
        email: formData.email,
        full_name: formData.fullName,
        password: formData.password,
        confirm_password: formData.confirmPassword
      };

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/register`,
        requestData
      );

      if (response.data) {
        alert('회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.');
        router.push('/login');
      }
    } catch (error: any) {
      console.error('회원가입 오류:', error);
      setError(error.response?.data?.detail || '회원가입 중 오류가 발생했습니다');
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
            회원가입
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            CBAM Calculator 계정을 생성하고 서비스를 이용해보세요
          </p>
        </div>

        {/* 회원가입 폼 */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 이름 필드 */}
            <div className="form-field">
              <label htmlFor="fullName" className="form-label">
                이름 *
              </label>
              <input
                type="text"
                id="fullName"
                value={formData.fullName}
                onChange={(e) => handleInputChange('fullName', e.target.value)}
                placeholder="이름을 입력하세요"
                className={`form-input ${validation.fullName.isValid ? 'border-green-500' : validation.fullName.message ? 'border-red-500' : ''}`}
                required
              />
              {validation.fullName.message && (
                <div className="form-error">
                  {validation.fullName.message}
                </div>
              )}
            </div>

            {/* 이메일 필드 */}
            <div className="form-field">
              <label htmlFor="email" className="form-label">
                이메일 *
              </label>
              <div className="flex gap-2">
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="이메일을 입력하세요"
                  className={`form-input flex-1 ${validation.email.isValid ? 'border-green-500' : validation.email.message ? 'border-red-500' : ''}`}
                  required
                />
                <button
                  type="button"
                  onClick={() => checkEmailAvailability()}
                  disabled={!formData.email || validation.email.isChecking}
                  className="btn btn-secondary whitespace-nowrap px-4"
                >
                  {validation.email.isChecking ? '확인중...' : '중복체크'}
                </button>
              </div>
              {validation.email.message && (
                <div className={`form-error ${validation.email.isValid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
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
                placeholder="비밀번호를 입력하세요 (6자 이상)"
                className={`form-input ${validation.password.isValid ? 'border-green-500' : validation.password.message ? 'border-red-500' : ''}`}
                required
              />
              {validation.password.message && (
                <div className="form-error">
                  {validation.password.message}
                </div>
              )}
            </div>

            {/* 비밀번호 확인 필드 */}
            <div className="form-field">
              <label htmlFor="confirmPassword" className="form-label">
                비밀번호 확인 *
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                placeholder="비밀번호를 다시 입력하세요"
                className={`form-input ${validation.confirmPassword.isValid ? 'border-green-500' : validation.confirmPassword.message ? 'border-red-500' : ''}`}
                required
              />
              {validation.confirmPassword.message && (
                <div className="form-error">
                  {validation.confirmPassword.message}
                </div>
              )}
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="form-error text-center">
                {error}
              </div>
            )}

            {/* 제출 버튼 */}
            <button
              type="submit"
              disabled={isLoading || !Object.values(validation).every(v => v.isValid)}
              className="btn btn-primary w-full"
            >
              {isLoading ? '처리중...' : '회원가입 완료'}
            </button>
          </form>

          {/* 로그인 링크 */}
          <div className="text-center mt-6">
            <p className="text-gray-600 dark:text-gray-400">
              이미 계정이 있으신가요?{' '}
              <button
                onClick={() => router.push('/login')}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 font-medium"
              >
                SignIn
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 