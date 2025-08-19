'use client';

import { useCallback } from 'react';
import { useAPI } from './useAPI';

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

export const useAuthAPI = () => {
  const api = useAPI('/api/v1/auth');

  const login = useCallback(async (data: LoginData) => {
    return api.post('/login', data, {
      successMessage: '로그인이 완료되었습니다!',
      errorMessage: '로그인에 실패했습니다'
    });
  }, [api]);

  const register = useCallback(async (data: RegisterData) => {
    const payload = {
      email: data.email,
      full_name: data.fullName,
      password: data.password,
      confirm_password: data.confirmPassword,
    };

    return api.post('/register', payload, {
      successMessage: '회원가입이 완료되었습니다!',
      errorMessage: '회원가입에 실패했습니다'
    });
  }, [api]);

  const updateProfile = useCallback(async (data: ProfileData, token: string) => {
    return api.put('/profile', data, {
      successMessage: '프로필이 성공적으로 업데이트되었습니다.',
      errorMessage: '프로필 업데이트 중 오류가 발생했습니다.',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }, [api]);

  const changePassword = useCallback(async (data: PasswordData, token: string) => {
    const payload = {
      current_password: data.current_password,
      new_password: data.new_password,
      confirm_new_password: data.confirm_password || data.new_password,
    };

    return api.put('/password', payload, {
      successMessage: '비밀번호가 성공적으로 변경되었습니다.',
      errorMessage: '비밀번호 변경 중 오류가 발생했습니다.',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }, [api]);

  return {
    login,
    register,
    updateProfile,
    changePassword,
  };
};