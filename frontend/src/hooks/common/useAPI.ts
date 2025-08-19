'use client';

import { useCallback } from 'react';
import { apiMethods } from '@/api';
import { useAsync } from './useAsync';
import type { AxiosRequestConfig } from 'axios';

export interface APIOptions {
  successMessage?: string;
  errorMessage?: string;
  onSuccess?: () => void;
  onError?: (error: any) => void;
  headers?: Record<string, string>;
  config?: AxiosRequestConfig;  // Omit 제거
}

export function useAPI(domain: string) {
  const { execute, isLoading, error, success } = useAsync();

  const createConfig = useCallback((options: APIOptions = {}): AxiosRequestConfig => {
    const { headers, config = {} } = options;
    return {
      ...config,
      headers: {
        ...(config.headers || {}),  // config.headers가 undefined일 수 있으므로 기본값 설정
        ...headers,
      },
    };
  }, []);

  const get = useCallback(<T = any>(
    endpoint: string,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.get(`${domain}${endpoint}`, createConfig(options)),
      asyncOptions
    );
  }, [domain, execute, createConfig]);

  const post = useCallback(<T = any>(
    endpoint: string,
    data?: any,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.post(`${domain}${endpoint}`, data, createConfig(options)),
      asyncOptions
    );
  }, [domain, execute, createConfig]);

  const put = useCallback(<T = any>(
    endpoint: string,
    data?: any,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.put(`${domain}${endpoint}`, data, createConfig(options)),
      asyncOptions
    );
  }, [domain, execute, createConfig]);

  const del = useCallback(<T = any>(
    endpoint: string,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.delete(`${domain}${endpoint}`, createConfig(options)),
      asyncOptions
    );
  }, [domain, execute, createConfig]);

  const patch = useCallback(<T = any>(
    endpoint: string,
    data?: any,
    options: APIOptions = {}
  ) => {
    const { headers, config, ...asyncOptions } = options;
    return execute<T>(
      () => apiMethods.patch(`${domain}${endpoint}`, data, createConfig(options)),
      asyncOptions
    );
  }, [domain, execute, createConfig]);

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