import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      
      login: (user, token) => set({
        user,
        token,
        isAuthenticated: true,
      }),
      
      logout: () => {
        console.log('🔄 AuthStore - 로그아웃 실행');
        
        // 로컬 스토리지 정리
        localStorage.removeItem('auth-storage');
        sessionStorage.clear();
        
        // 상태 초기화
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
        
        console.log('✅ AuthStore - 로그아웃 완료, 상태 초기화됨');
      },
      
      updateUser: (updates) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
