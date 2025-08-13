import { api } from './api';

// 하드코딩된 API 엔드포인트
const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout'
  },
  USER: {
    PROFILE: '/user/profile',
    UPDATE: '/user/update'
  }
};

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
  message?: string;
}

export interface LoginResponse {
  user: AuthUser;
  message: string;
}

// Auth Service API 함수들
export const authApi = {
  // 회원가입
  async register(userData: RegisterData): Promise<AuthUser> {
    try {
      console.log('🚀 회원가입 API 호출:', userData);
      
      const response = await api.post<AuthUser>(API_ENDPOINTS.AUTH.REGISTER, userData);
      
      console.log('✅ 회원가입 성공:', response);
      return response;
    } catch (error: any) {
      console.error('❌ 회원가입 API 오류:', error);
      
      // API 오류 메시지 추출
      let errorMessage = '회원가입 중 오류가 발생했습니다.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    }
  },

  // 로그인
  async login(credentials: LoginCredentials): Promise<{ success: boolean; user?: AuthUser; message?: string }> {
    try {
      console.log('🚀 로그인 API 호출:', credentials);
      
      // API 엔드포인트 확인
      const loginEndpoint = API_ENDPOINTS.AUTH.LOGIN;
      console.log('🔗 로그인 엔드포인트:', loginEndpoint);
      console.log('🌐 전체 URL:', `${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://gateway-production-22ef.up.railway.app/api/v1'}${loginEndpoint}`);
      
      const response = await api.post<LoginResponse>(loginEndpoint, credentials);
      
      console.log('✅ 로그인 성공:', response);
      return { 
        success: true, 
        user: response.user, 
        message: response.message 
      };
    } catch (error: any) {
      console.error('❌ 로그인 API 오류:', error);
      
      // API 오류 메시지 추출
      let errorMessage = '로그인 중 오류가 발생했습니다.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    }
  },

  // 현재 사용자 정보 조회
  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      // 현재는 로컬 스토리지에서 사용자 정보를 가져옴
      if (typeof window !== 'undefined') {
        const userStr = localStorage.getItem('auth-user');
        if (userStr) {
          return JSON.parse(userStr);
        }
      }
      return null;
    } catch (error) {
      console.error('사용자 정보 조회 오류:', error);
      return null;
    }
  },

  // 로그아웃
  logout(): void {
    console.log('🚪 로그아웃');
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-user');
      localStorage.removeItem('auth-token');
    }
  },

  // 사용자 정보 저장
  saveUser(user: AuthUser): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth-user', JSON.stringify(user));
    }
  },

  // 토큰 저장
  saveToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth-token', token);
    }
  },

  // 토큰 가져오기
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth-token');
    }
    return null;
  }
}; 