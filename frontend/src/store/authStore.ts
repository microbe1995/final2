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

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthStore extends AuthState {
  setUser: (user: AuthUser) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
  clearAuth: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
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