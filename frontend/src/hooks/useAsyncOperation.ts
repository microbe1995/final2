'use client';

import { useState, useCallback } from 'react';

export const useAsyncOperationHelper = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 상태 초기화
  const resetState = useCallback(() => {
    setError('');
    setSuccess('');
  }, []);

  // 에러 설정
  const setErrorState = useCallback((errorMessage: string) => {
    setError(errorMessage);
    setSuccess('');
  }, []);

  // 성공 설정
  const setSuccessState = useCallback((successMessage: string) => {
    setSuccess(successMessage);
    setError('');
  }, []);

  // 비동기 작업 실행
  const executeAsync = useCallback(async <T>(
    operation: () => Promise<T>,
    successMessage?: string
  ): Promise<T | null> => {
    setIsLoading(true);
    resetState();

    try {
      const result = await operation();
      
      if (successMessage) {
        setSuccessState(successMessage);
      }
      
      return result;
    } catch (error: any) {
      const errorMessage = error.message || '작업 중 오류가 발생했습니다.';
      setErrorState(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [resetState, setErrorState, setSuccessState]);

  return {
    // 상태
    isLoading,
    error,
    success,
    
    // 액션
    resetState,
    setErrorState,
    setSuccessState,
    executeAsync,
  };
};
