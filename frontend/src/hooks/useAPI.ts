'use client';

import { useCallback } from 'react';
import axios, { AxiosInstance, AxiosResponse, AxiosError, AxiosRequestConfig } from 'axios';
import { useAsync } from './useAsync';

// ============================================================================
// 🔧 API 클라이언트 설정 (통합됨)
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

// 기본 API 클라이언트 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// 🔄 응답 인터셉터 - 에러 처리
// ============================================================================

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('✅ API 호출 성공:', response.config.url);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API 호출 실패:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

// ============================================================================
// 🎯 요청 인터셉터 - 로깅
// ============================================================================

apiClient.interceptors.request.use(
  (config) => {
    console.log('🔍 API 요청:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
    });
    return config;
  },
  (error) => {
    console.error('❌ API 요청 설정 오류:', error);
    return Promise.reject(error);
  }
);

// ============================================================================
// 🚀 공통 API 메서드 (내부 사용)
// ============================================================================

const apiMethods = {
  // GET 요청
  get: <T = any>(url: string, config?: any): Promise<T> => 
    apiClient.get(url, config).then(response => response.data),
  
  // POST 요청
  post: <T = any>(url: string, data?: any, config?: any): Promise<T> => 
    apiClient.post(url, data, config).then(response => response.data),
  
  // PUT 요청
  put: <T = any>(url: string, data?: any, config?: any): Promise<T> => 
    apiClient.put(url, data, config).then(response => response.data),
  
  // DELETE 요청
  delete: <T = any>(url: string, config?: any): Promise<T> => 
    apiClient.delete(url, config).then(response => response.data),
  
  // PATCH 요청
  patch: <T = any>(url: string, data?: any, config?: any): Promise<T> => 
    apiClient.patch(url, data, config).then(response => response.data),
};

// ============================================================================
// 🪝 useAPI 훅 - 상태 관리가 포함된 API 호출
// ============================================================================

export interface APIOptions {
  successMessage?: string;
  errorMessage?: string;
  onSuccess?: () => void;
  onError?: (error: any) => void;
  headers?: Record<string, string>;
  config?: AxiosRequestConfig;
}

export function useAPI(domain: string) {
  const { execute, isLoading, error, success } = useAsync();

  const createConfig = useCallback((options: APIOptions = {}): AxiosRequestConfig => {
    const { headers, config = {} } = options;
    return {
      ...config,
      headers: {
        ...(config.headers || {}),
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

// ============================================================================
// 🌐 외부 사용을 위한 직접 API 클라이언트 export (필요시)
// ============================================================================

export { apiClient };
export default useAPI;