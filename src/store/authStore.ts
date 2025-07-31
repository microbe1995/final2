import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthState, User, LoginCredentials, RegisterData } from '@/types';
import { apiClient } from '@/lib/api';

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  clearAuth: () => void;
  checkAuth: () => Promise<boolean>;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.post<{ user: User; token: string }>('/auth/login', credentials);
          
          if (response.success && response.data) {
            const { user, token } = response.data;
            apiClient.setAuthToken(token);
            
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
            });
            return true;
          }
          return false;
        } catch (error) {
          set({ isLoading: false });
          console.error('Login error:', error);
          return false;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.post<{ user: User; token: string }>('/auth/register', data);
          
          if (response.success && response.data) {
            const { user, token } = response.data;
            apiClient.setAuthToken(token);
            
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
            });
            return true;
          }
          return false;
        } catch (error) {
          set({ isLoading: false });
          console.error('Register error:', error);
          return false;
        }
      },

      logout: () => {
        apiClient.clearAuthToken();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setToken: (token: string) => {
        apiClient.setAuthToken(token);
        set({ token, isAuthenticated: true });
      },

      clearAuth: () => {
        apiClient.clearAuthToken();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) return false;

        try {
          const response = await apiClient.get<User>('/auth/me');
          if (response.success && response.data) {
            set({ user: response.data, isAuthenticated: true });
            return true;
          }
          return false;
        } catch (error) {
          get().clearAuth();
          return false;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
); 