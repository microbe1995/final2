'use client';

import { useState, useCallback } from 'react';

export interface AsyncState {
  isLoading: boolean;
  error: string | null;
  success: string | null;
}

export interface AsyncOperationOptions {
  successMessage?: string;
  errorMessage?: string;
  onSuccess?: () => void;
  onError?: (error: any) => void;
}

export function useAsync() {
  const [state, setState] = useState<AsyncState>({
    isLoading: false,
    error: null,
    success: null,
  });

  const resetState = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      success: null,
    });
  }, []);

  const execute = useCallback(async <T>(
    operation: () => Promise<T>,
    options: AsyncOperationOptions = {}
  ): Promise<T | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null, success: null }));

    try {
      const result = await operation();
      
      if (options.successMessage) {
        setState(prev => ({ ...prev, success: options.successMessage }));
      }
      
      options.onSuccess?.();
      return result;
    } catch (error: any) {
      const errorMessage = options.errorMessage || error.message || '작업 중 오류가 발생했습니다.';
      setState(prev => ({ ...prev, error: errorMessage }));
      options.onError?.(error);
      return null;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  return {
    ...state,
    execute,
    resetState,
  };
}
