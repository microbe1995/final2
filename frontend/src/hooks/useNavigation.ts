'use client';

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

export const useAppNavigation = () => {
  const router = useRouter();

  // 로그인 페이지로 이동
  const goToLogin = useCallback(() => {
    router.push('/login');
  }, [router]);

  // 회원가입 페이지로 이동
  const goToRegister = useCallback(() => {
    router.push('/register');
  }, [router]);

  // 프로필 페이지로 이동
  const goToProfile = useCallback(() => {
    router.push('/profile');
  }, [router]);

  // 홈 페이지로 이동
  const goToHome = useCallback(() => {
    router.push('/');
  }, [router]);

  // 공정도 페이지로 이동
  const goToProcessFlow = useCallback(() => {
    router.push('/process-flow');
  }, [router]);

  // 뒤로 가기
  const goBack = useCallback(() => {
    router.back();
  }, [router]);

  // 새로고침
  const refresh = useCallback(() => {
    router.refresh();
  }, [router]);

  return {
    goToLogin,
    goToRegister,
    goToProfile,
    goToHome,
    goToProcessFlow,
    goBack,
    refresh,
  };
};
