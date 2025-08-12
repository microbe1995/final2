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
  created_at: string;
}

// Auth Service API 함수들
export const authApi = {
  // 회원가입
  async register(userData: RegisterData): Promise<AuthUser> {
    try {
      // 로컬 테스트용: 더미 데이터 반환
      console.log('auth.ts: 로컬 테스트 - 더미 데이터 반환');
      
      // 더미 사용자 데이터 반환
      const dummyUser: AuthUser = {
        id: 'local-user-' + Date.now(),
        email: userData.email,
        name: userData.name,
        created_at: new Date().toISOString()
      };
      
      return dummyUser;
    } catch (error) {
      console.error('auth.ts: 오류 발생:', error);
      throw error;
    }
  },

  // 로그인
  async login(credentials: LoginCredentials): Promise<{ success: boolean }> {
    try {
      // 로컬 테스트용: 성공 응답만 반환
      console.log('auth.ts: 로그인 성공 (테스트)');
      return { success: true };
    } catch (error) {
      throw error;
    }
  },

  // 현재 사용자 정보 조회
  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      // 로컬 테스트용: null 반환
      console.log('auth.ts: 사용자 정보 없음 (테스트)');
      return null;
    } catch (error) {
      return null;
    }
  },

  // 로그아웃
  logout(): void {
    // 로컬 테스트용: 아무것도 하지 않음
    console.log('auth.ts: 로그아웃 (테스트)');
  }
}; 