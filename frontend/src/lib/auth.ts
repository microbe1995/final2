import { apiClient } from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  name: string;
  password: string;
}

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Auth Service API 함수들
export const authApi = {
  // 회원가입
  async register(userData: RegisterData): Promise<AuthUser> {
    try {
      const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const response = await fetch(`${GATEWAY_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '회원가입에 실패했습니다.');
      }
      
      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  // 로그인
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    try {
      const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const response = await fetch(`${GATEWAY_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '로그인에 실패했습니다.');
      }
      
      const tokenData = await response.json();
      
      // 토큰을 localStorage에 저장
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', tokenData.access_token);
      }
      
      return tokenData;
    } catch (error) {
      throw error;
    }
  },

  // 현재 사용자 정보 조회
  async getCurrentUser(): Promise<AuthUser> {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      
      if (!token) {
        throw new Error('토큰이 없습니다.');
      }
      
      const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const response = await fetch(`${GATEWAY_URL}/api/v1/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          this.logout();
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || '사용자 정보를 가져올 수 없습니다.');
      }
      
      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  // 토큰 검증
  async verifyToken(): Promise<boolean> {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      
      if (!token) {
        return false;
      }
      
      const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const response = await fetch(`${GATEWAY_URL}/api/v1/auth/verify-token`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      return response.ok;
    } catch (error) {
      return false;
    }
  },

  // 로그아웃
  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  },

  // 토큰 존재 여부 확인
  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      return !!token;
    }
    return false;
  },

  // 토큰 가져오기
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }
}; 