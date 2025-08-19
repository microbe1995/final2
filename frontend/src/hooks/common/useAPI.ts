'use client';

import { useCallback } from 'react';
import { apiMethods } from '@/api';
import { useAsync } from './useAsync';

export interface APIOptions {
  successMessage?: string;
  errorMessage?: string;
  onSuccess?: () => void;
  onError?: (error: any) => void;
  headers?: Record<string, string>;  // headers 옵션 추가
  config?: any;  // 추가적인 axios 설정을 위한 옵션
}

export function useAPI(domain: string) {
  const { execute, isLoading, error, success } = useAsync();

  const get = useCallback(<T = any>(
    endpoint: string,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.get(`${domain}${endpoint}`, { headers, ...config }),
      asyncOptions
    );
  }, [domain, execute]);

  const post = useCallback(<T = any>(
    endpoint: string,
    data?: any,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.post(`${domain}${endpoint}`, data, { headers, ...config }),
      asyncOptions
    );
  }, [domain, execute]);

  const put = useCallback(<T = any>(
    endpoint: string,
    data?: any,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.put(`${domain}${endpoint}`, data, { headers, ...config }),
      asyncOptions
    );
  }, [domain, execute]);

  const del = useCallback(<T = any>(
    endpoint: string,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.delete(`${domain}${endpoint}`, { headers, ...config }),
      asyncOptions
    );
  }, [domain, execute]);

  const patch = useCallback(<T = any>(
    endpoint: string,
    data?: any,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.patch(`${domain}${endpoint}`, data, { headers, ...config }),
      asyncOptions
    );
  }, [domain, execute]);

  return {
    isLoading,
    error,
    success,
    get,
    post,
    put,
    delete: del,
    patch,
  };
}