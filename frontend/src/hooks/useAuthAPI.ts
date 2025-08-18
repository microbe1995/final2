'use client';

import { useCallback } from 'react';
import { apiMethods } from '@/api/apiClient';

interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  fullName?: string;
  confirmPassword?: string;
}

interface ProfileData {
  full_name: string;
  email: string;
}

interface PasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export const useAuthService = () => {
  // ============================================================================
  // 🔐 로그인 API 호출
  // ============================================================================
  
  const login = useCallback(async (data: LoginData) => {
    try {
      const response = await apiMethods.post('/api/v1/auth/login', data);
      
      if (response && response.user && response.token) {
        return {
          success: true,
          data: response,
          message: '로그인이 완료되었습니다!',
        };
      } else {
        throw new Error(response.message || '로그인에 실패했습니다');
      }
    } catch (error: any) {
      const errorMessage = error.message || '로그인에 실패했습니다';
      throw new Error(errorMessage);
    }
  }, []);

  // ============================================================================
  // 📝 회원가입 API 호출
  // ============================================================================
  
  const register = useCallback(async (data: RegisterData) => {
    try {
      // 백엔드 스키마(UserRegistrationRequest)는 snake_case를 기대합니다.
      const payload = {
        email: data.email,
        full_name: data.fullName,
        password: data.password,
        confirm_password: data.confirmPassword,
      };

      const response = await apiMethods.post('/api/v1/auth/register', payload);
      
      return {
        success: true,
        data: response,
        message: '회원가입이 완료되었습니다!',
      };
    } catch (error: any) {
      const errorMessage = error.message || '회원가입에 실패했습니다';
      throw new Error(errorMessage);
    }
  }, []);

  // ============================================================================
  // 👤 프로필 업데이트 API 호출
  // ============================================================================
  
  const updateProfile = useCallback(async (data: ProfileData, token: string) => {
    try {
      const response = await apiMethods.put(
        '/api/v1/auth/profile',
        data,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response) {
        return {
          success: true,
          data: response,
          message: '프로필이 성공적으로 업데이트되었습니다.',
        };
      } else {
        throw new Error('프로필 업데이트 응답이 없습니다.');
      }
    } catch (error: any) {
      const errorMessage = error.message || '프로필 업데이트 중 오류가 발생했습니다.';
      throw new Error(errorMessage);
    }
  }, []);

  // ============================================================================
  // 🔑 비밀번호 변경 API 호출
  // ============================================================================
  
  const changePassword = useCallback(async (data: PasswordData, token: string) => {
    try {
      const response = await apiMethods.put(
        '/api/v1/auth/password',
        {
          current_password: data.current_password,
          new_password: data.new_password,
          // 백엔드 스키마는 confirm_new_password를 요구
          confirm_new_password: data.confirm_password || data.new_password,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response) {
        return {
          success: true,
          data: response,
          message: '비밀번호가 성공적으로 변경되었습니다.',
        };
      } else {
        throw new Error('비밀번호 변경 응답이 없습니다.');
      }
    } catch (error: any) {
      const errorMessage = error.message || '비밀번호 변경 중 오류가 발생했습니다.';
      throw new Error(errorMessage);
    }
  }, []);

  return {
    login,
    register,
    updateProfile,
    changePassword,
  };
};
