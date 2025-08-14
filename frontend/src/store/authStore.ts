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

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthStore extends AuthState {
  setUser: (user: AuthUser) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  clearAuth: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      error: null,

      setUser: (user: AuthUser) => {
        set({ user, error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        
        try {
          // 로컬 개발 환경용 API URL
          const apiUrl = '/api/v1/auth/login';
          
          const response = await fetch(apiUrl, {
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
            set({ user: result.user, error: null });
          } else {
            throw new Error(result.message || '로그인에 실패했습니다.');
          }
          
        } catch (error: any) {
          set({ error: error.message || '로그인 중 오류가 발생했습니다.' });
          throw error;
        } finally {
          set({ isLoading: false });
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