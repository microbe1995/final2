'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

// ============================================================================
// 👤 프로필 페이지 컴포넌트
// ============================================================================

export default function ProfilePage() {
  const router = useRouter();
  const { user, token, isAuthenticated, updateUser, logout } = useAuth();
  
  // ============================================================================
  // 📝 상태 관리
  // ============================================================================
  
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [validation, setValidation] = useState({
    full_name: { isValid: false, message: '' },
    email: { isValid: false, message: '' },
    current_password: { isValid: false, message: '' },
    new_password: { isValid: false, message: '' },
    confirm_password: { isValid: false, message: '' }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // ============================================================================
  // 🔄 초기화 (사용자 정보 로드)
  // ============================================================================
  
  useEffect(() => {
    // 로딩 중이면 대기
    if (isLoading) {
      return;
    }

    // 인증되지 않은 경우 로그인 페이지로 이동
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // 사용자 정보가 있으면 프로필 데이터 설정
    if (user) {
      setProfileData({
        full_name: user.full_name,
        email: user.email
      });
    }
  }, [isAuthenticated, user, router, isLoading]);

  // ============================================================================
  // 📝 폼 입력 처리
  // ============================================================================
  
  const handleProfileChange = (field: string, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
    setError('');
    setSuccess('');

    // 실시간 유효성 검사
    switch (field) {
      case 'full_name':
        const fullNameValid = value.length >= 2 && value.length <= 100;
        setValidation(prev => ({
          ...prev,
          full_name: {
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
            isValid: emailValid,
            message: emailValid ? '' : '올바른 이메일 형식을 입력해주세요'
          }
        }));
        break;
    }
  };

  const handlePasswordInputChange = (field: string, value: string) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
    setError('');
    setSuccess('');

    // 실시간 유효성 검사
    switch (field) {
      case 'current_password':
        const currentValid = value.length >= 1;
        setValidation(prev => ({
          ...prev,
          current_password: {
            isValid: currentValid,
            message: currentValid ? '' : '현재 비밀번호를 입력해주세요'
          }
        }));
        break;

      case 'new_password':
        const newValid = value.length >= 6;
        setValidation(prev => ({
          ...prev,
          new_password: {
            isValid: newValid,
            message: newValid ? '' : '새 비밀번호는 최소 6자 이상이어야 합니다'
          }
        }));
        break;

      case 'confirm_password':
        const confirmValid = value === passwordData.new_password;
        setValidation(prev => ({
          ...prev,
          confirm_password: {
            isValid: confirmValid,
            message: confirmValid ? '' : '비밀번호가 일치하지 않습니다'
          }
        }));
        break;
    }
  };

  // ============================================================================
  // ✏️ 프로필 정보 수정
  // ============================================================================
  
  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validation.full_name.isValid || !validation.email.isValid) {
      setError('모든 필드를 올바르게 입력해주세요');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.put(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/profile`,
        profileData,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data) {
        // AuthContext 업데이트
        updateUser({
          full_name: profileData.full_name,
          email: profileData.email
        });
        
        setSuccess('프로필 정보가 성공적으로 수정되었습니다!');
      }
    } catch (error: any) {
      console.error('프로필 수정 오류:', error);
      setError(error.response?.data?.detail || '프로필 수정 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🔐 비밀번호 변경
  // ============================================================================
  
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validation.current_password.isValid || !validation.new_password.isValid || !validation.confirm_password.isValid) {
      setError('모든 필드를 올바르게 입력해주세요');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.put(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/password`,
        passwordData,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data) {
        setSuccess('비밀번호가 성공적으로 변경되었습니다!');
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      }
    } catch (error: any) {
      console.error('비밀번호 변경 오류:', error);
      setError(error.response?.data?.detail || '비밀번호 변경 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🗑️ 회원탈퇴
  // ============================================================================
  
  const handleAccountDeletion = async () => {
    if (!confirm('정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.delete(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/profile`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data) {
        alert('계정이 성공적으로 삭제되었습니다.');
        logout();
        router.push('/');
      }
    } catch (error: any) {
      console.error('계정 삭제 오류:', error);
      setError(error.response?.data?.detail || '계정 삭제 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  // 로딩 중이면 로딩 화면 표시
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">인증 상태 확인 중...</p>
        </div>
      </div>
    );
  }

  // 인증되지 않은 경우 로그인 페이지로 리다이렉트
  if (!isAuthenticated) {
    return null; // 로그인 페이지로 리다이렉트 중
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            프로필 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            계정 정보를 관리하고 보안을 설정하세요
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 프로필 정보 수정 */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              프로필 정보 수정
            </h2>
            
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              {/* 이름 필드 */}
              <div className="form-field">
                <label htmlFor="full_name" className="form-label">
                  이름 *
                </label>
                <input
                  type="text"
                  id="full_name"
                  value={profileData.full_name}
                  onChange={(e) => handleProfileChange('full_name', e.target.value)}
                  className={`form-input ${validation.full_name.isValid ? 'border-green-500' : validation.full_name.message ? 'border-red-500' : ''}`}
                  required
                />
                {validation.full_name.message && (
                  <div className="form-error">
                    {validation.full_name.message}
                  </div>
                )}
              </div>

              {/* 이메일 필드 */}
              <div className="form-field">
                <label htmlFor="email" className="form-label">
                  이메일 *
                </label>
                <input
                  type="email"
                  id="email"
                  value={profileData.email}
                  onChange={(e) => handleProfileChange('email', e.target.value)}
                  className={`form-input ${validation.email.isValid ? 'border-green-500' : validation.email.message ? 'border-red-500' : ''}`}
                  required
                />
                {validation.email.message && (
                  <div className="form-error">
                    {validation.email.message}
                  </div>
                )}
              </div>

              {/* 프로필 수정 버튼 */}
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? '수정 중...' : '프로필 수정'}
              </button>
            </form>
          </div>

          {/* 비밀번호 변경 */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              비밀번호 변경
            </h2>
            
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              {/* 현재 비밀번호 */}
              <div className="form-field">
                <label htmlFor="current_password" className="form-label">
                  현재 비밀번호 *
                </label>
                <input
                  type="password"
                  id="current_password"
                  value={passwordData.current_password}
                  onChange={(e) => handlePasswordInputChange('current_password', e.target.value)}
                  className={`form-input ${validation.current_password.isValid ? 'border-green-500' : validation.current_password.message ? 'border-red-500' : ''}`}
                  required
                />
                {validation.current_password.message && (
                  <div className="form-error">
                    {validation.current_password.message}
                  </div>
                )}
              </div>

              {/* 새 비밀번호 */}
              <div className="form-field">
                <label htmlFor="new_password" className="form-label">
                  새 비밀번호 *
                </label>
                <input
                  type="password"
                  id="new_password"
                  value={passwordData.new_password}
                  onChange={(e) => handlePasswordInputChange('new_password', e.target.value)}
                  className={`form-input ${validation.new_password.isValid ? 'border-green-500' : validation.new_password.message ? 'border-red-500' : ''}`}
                  required
                />
                {validation.new_password.message && (
                  <div className="form-error">
                    {validation.new_password.message}
                  </div>
                )}
              </div>

              {/* 새 비밀번호 확인 */}
              <div className="form-field">
                <label htmlFor="confirm_password" className="form-label">
                  새 비밀번호 확인 *
                </label>
                <input
                  type="password"
                  id="confirm_password"
                  value={passwordData.confirm_password}
                  onChange={(e) => handlePasswordInputChange('confirm_password', e.target.value)}
                  className={`form-input ${validation.confirm_password.isValid ? 'border-green-500' : validation.confirm_password.message ? 'border-red-500' : ''}`}
                  required
                />
                {validation.confirm_password.message && (
                  <div className="form-error">
                    {validation.confirm_password.message}
                  </div>
                )}
              </div>

              {/* 비밀번호 변경 버튼 */}
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-secondary w-full"
              >
                {isLoading ? '변경 중...' : '비밀번호 변경'}
              </button>
            </form>
          </div>
        </div>

        {/* 회원탈퇴 */}
        <div className="card mt-8 border-red-200 dark:border-red-800">
          <h2 className="text-xl font-semibold text-red-700 dark:text-red-400 mb-4">
            🗑️ 회원탈퇴
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            계정을 삭제하면 모든 데이터가 영구적으로 삭제되며 복구할 수 없습니다.
          </p>
          <button
            onClick={handleAccountDeletion}
            disabled={isLoading}
            className="btn bg-red-600 hover:bg-red-700 text-white"
          >
            {isLoading ? '삭제 중...' : '계정 삭제'}
          </button>
        </div>

        {/* 메시지 표시 */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}
        
        {success && (
          <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p className="text-green-800 dark:text-green-200">{success}</p>
          </div>
        )}
      </div>
    </div>
  );
}
