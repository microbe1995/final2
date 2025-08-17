import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// ============================================================================
// 🔧 API 클라이언트 설정
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

// 기본 API 클라이언트 생성
export const apiClient: AxiosInstance = axios.create({
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
// 🚀 공통 API 메서드
// ============================================================================

export const apiMethods = {
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

export default apiClient;
