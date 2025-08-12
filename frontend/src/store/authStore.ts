import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, AuthUser, LoginCredentials, RegisterData } from '@/lib/auth';

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
}

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => void;
  setUser: (user: AuthUser) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true });
        try {
          const response = await authApi.login(credentials);
          
          set({
            user: null,
            isLoading: false,
          });
          return response.success;
        } catch (error) {
          set({ isLoading: false });
          console.error('Login error:', error);
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          const user = await authApi.register(data);
          
          set({
            user,
            isLoading: false,
          });
          return true;
        } catch (error) {
          set({ isLoading: false });
          console.error('Register error:', error);
          throw error;
        }
      },

      logout: () => {
        authApi.logout();
        set({
          user: null,
          isLoading: false,
        });
      },

      setUser: (user: AuthUser) => {
        set({ user });
      },

      clearAuth: () => {
        authApi.logout();
        set({
          user: null,
          isLoading: false,
        });
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