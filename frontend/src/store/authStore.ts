import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthUser {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
  message?: string;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => void;
  setUser: (user: AuthUser) => void;
  clearAuth: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      error: null,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          // Gateway로 직접 요청
          const response = await fetch('https://gateway-production-1104.up.railway.app/api/v1/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials)
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '로그인에 실패했습니다.');
          }

          const result = await response.json();
          
          if (result.user) {
            set({
              user: result.user,
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({ 
              isLoading: false, 
              error: result.message || '로그인에 실패했습니다.' 
            });
            return false;
          }
        } catch (error: any) {
          const errorMessage = error.message || '로그인 중 오류가 발생했습니다.';
          set({ 
            isLoading: false, 
            error: errorMessage 
          });
          console.error('Login error:', error);
          return false;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          // Gateway로 직접 요청
          const response = await fetch('https://gateway-production-1104.up.railway.app/api/v1/auth/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '회원가입에 실패했습니다.');
          }

          const user = await response.json();
          
          set({
            user,
            isLoading: false,
            error: null,
          });
          return true;
        } catch (error: any) {
          const errorMessage = error.message || '회원가입 중 오류가 발생했습니다.';
          set({ 
            isLoading: false, 
            error: errorMessage 
          });
          console.error('Register error:', error);
          return false;
        }
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-user');
          localStorage.removeItem('auth-token');
        }
        set({
          user: null,
          isLoading: false,
          error: null,
        });
      },

      setUser: (user: AuthUser) => {
        set({ user, error: null });
      },

      clearAuth: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-user');
          localStorage.removeItem('auth-token');
        }
        set({
          user: null,
          isLoading: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
      }),
    }
  )
); 