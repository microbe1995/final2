import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// 하드코딩된 API 설정
const API_CONFIG = {
  baseURL: 'http://localhost:8080',
  apiBaseURL: 'http://localhost:8080/api/v1'
};

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