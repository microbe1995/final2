import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, AuthUser, LoginCredentials, RegisterData } from '@/lib/auth';

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
          const response = await authApi.login(credentials);
          
          if (response.success && response.user) {
            // 사용자 정보 저장
            authApi.saveUser(response.user);
            
            set({
              user: response.user,
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({ 
              isLoading: false, 
              error: response.message || '로그인에 실패했습니다.' 
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
          const user = await authApi.register(data);
          
          // 사용자 정보 저장
          authApi.saveUser(user);
          
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
        authApi.logout();
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
        authApi.logout();
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