import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// 환경변수 타입 안전성을 위한 헬퍼 함수
const getEnvVar = (key: string, defaultValue: string): string => {
  const value = process.env[key];
  console.log(`🔍 환경변수 ${key}:`, value || 'undefined');
  return value || defaultValue;
};

// 환경변수 기반 API 설정
const API_CONFIG = {
  baseURL: getEnvVar('NEXT_PUBLIC_API_URL', 'http://localhost:8080'),
  apiBaseURL: getEnvVar('NEXT_PUBLIC_API_BASE_URL', 'http://localhost:8080/api/v1')
};

// Railway 배포 환경 확인 (더 강화된 로직)
const isRailwayDeployed = (
  process.env.NEXT_PUBLIC_RAILWAY_API_URL && 
  process.env.NEXT_PUBLIC_RAILWAY_API_URL !== 'http://localhost:8080' &&
  process.env.NEXT_PUBLIC_RAILWAY_API_URL.includes('railway.app')
);

// 모든 환경변수 출력 (디버깅용)
console.log('🔍 모든 환경변수 확인:');
console.log('  - NODE_ENV:', process.env.NODE_ENV);
console.log('  - NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('  - NEXT_PUBLIC_RAILWAY_API_URL:', process.env.NEXT_PUBLIC_RAILWAY_API_URL);
console.log('  - NEXT_PUBLIC_RAILWAY_API_BASE_URL:', process.env.NEXT_PUBLIC_RAILWAY_API_BASE_URL);

// Railway 환경에서는 Railway URL 사용
if (isRailwayDeployed && process.env.NEXT_PUBLIC_RAILWAY_API_URL) {
  API_CONFIG.baseURL = process.env.NEXT_PUBLIC_RAILWAY_API_URL;
  API_CONFIG.apiBaseURL = process.env.NEXT_PUBLIC_RAILWAY_API_BASE_URL || 
                          `${process.env.NEXT_PUBLIC_RAILWAY_API_URL}/api/v1`;
  
  console.log('🚂 Railway 환경 감지됨 - Railway API 사용');
} else {
  console.log('🏠 로컬 개발 환경 - localhost API 사용');
  console.log('❌ Railway 환경 감지 실패 이유:');
  console.log('  - NEXT_PUBLIC_RAILWAY_API_URL 존재:', !!process.env.NEXT_PUBLIC_RAILWAY_API_URL);
  console.log('  - localhost가 아님:', process.env.NEXT_PUBLIC_RAILWAY_API_URL !== 'http://localhost:8080');
  console.log('  - railway.app 포함:', process.env.NEXT_PUBLIC_RAILWAY_API_URL?.includes('railway.app'));
}

console.log('🔧 API 설정:', API_CONFIG);
console.log('🚀 Railway 배포 여부:', isRailwayDeployed);
console.log('🌐 Railway API URL:', process.env.NEXT_PUBLIC_RAILWAY_API_URL);
console.log('🔗 API Base URL:', API_CONFIG.apiBaseURL);

// axios 인스턴스 생성
const createApiClient = (): AxiosInstance => {
  console.log('🔧 API 클라이언트 생성:', API_CONFIG);
  
  const apiClient = axios.create({
    baseURL: API_CONFIG.apiBaseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 요청 인터셉터
  apiClient.interceptors.request.use(
    (config) => {
      console.log(`🚀 API 요청: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
      if (config.data) {
        console.log('📤 요청 데이터:', config.data);
      }
      return config;
    },
    (error) => {
      console.error('❌ 요청 인터셉터 오류:', error);
      return Promise.reject(error);
    }
  );

  // 응답 인터셉터
  apiClient.interceptors.response.use(
    (response: AxiosResponse) => {
      console.log(`✅ API 응답: ${response.status} ${response.config.url}`);
      console.log('📥 응답 데이터:', response.data);
      return response;
    },
    (error) => {
      console.error('❌ 응답 인터셉터 오류:', error);
      if (error.response) {
        console.error('📊 오류 응답:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers,
          url: error.config?.url,
          baseURL: error.config?.baseURL,
        });
      } else if (error.request) {
        console.error('🌐 네트워크 오류:', {
          message: error.message,
          code: error.code,
        });
      }
      return Promise.reject(error);
    }
  );

  return apiClient;
};

// API 클라이언트 인스턴스
export const apiClient = createApiClient();

// API 응답 타입
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// API 오류 타입
export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

// API 클라이언트 래퍼 함수들
export const api = {
  // GET 요청
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then(response => response.data),

  // POST 요청
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then(response => response.data),

  // PUT 요청
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then(response => response.data),

  // PATCH 요청
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config).then(response => response.data),

  // DELETE 요청
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config).then(response => response.data),
};

export default apiClient; 