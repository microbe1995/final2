import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from 'axios';
import { env } from './env';

// 요청 중복 방지를 위한 pending requests 관리
const pendingRequests = new Map<string, AbortController>();

// 요청 키 생성 함수
const generateRequestKey = (config: AxiosRequestConfig): string => {
  const { method, url, data, params } = config;
  return `${method?.toUpperCase() || 'GET'}:${url}:${JSON.stringify(data || {})}:${JSON.stringify(params || {})}`;
};

// API 요청인지 확인하는 함수
const isAPIRequest = (url: string): boolean => {
  return url.startsWith('/api/') || url.startsWith('/health');
};

// CSRF 토큰 가져오기
const getCSRFToken = (): string | null => {
  if (typeof document !== 'undefined') {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta?.getAttribute('content') || null;
  }
  return null;
};

// 재시도 로직
const retryRequest = async (
  axiosInstance: AxiosInstance,
  config: AxiosRequestConfig,
  retries: number = 3
): Promise<AxiosResponse> => {
  try {
    return await axiosInstance(config);
  } catch (error: unknown) {
    const axiosError = error as AxiosError;
    if (
      retries > 0 &&
      ((axiosError.response?.status && axiosError.response.status >= 500) ||
        !axiosError.response)
    ) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (4 - retries)));
      return retryRequest(axiosInstance, config, retries - 1);
    }
    throw error;
  }
};

// axios 인스턴스 생성
const axiosClient: AxiosInstance = axios.create({
  baseURL: '', // 상대 경로 사용 (Next.js rewrites 활용)
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
axiosClient.interceptors.request.use(
  config => {
    // 요청 키 생성
    const requestKey = generateRequestKey(config);

    // 이미 진행 중인 동일한 요청이 있으면 취소
    if (pendingRequests.has(requestKey)) {
      const controller = pendingRequests.get(requestKey);
      if (controller) {
        controller.abort();
      }
    }

    // 새로운 AbortController 생성
    const controller = new AbortController();
    config.signal = controller.signal;
    pendingRequests.set(requestKey, controller);

    // API 요청 검증
    if (config.url && !isAPIRequest(config.baseURL + config.url)) {
      throw new Error(
        'Direct service access is not allowed. Use API routes only.'
      );
    }

    // CSRF 토큰 추가
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }

    // 인증 토큰 추가
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
axiosClient.interceptors.response.use(
  response => {
    // 요청 완료 시 pending requests에서 제거
    const requestKey = generateRequestKey(response.config);
    pendingRequests.delete(requestKey);
    return response;
  },
  async error => {
    // 요청 완료 시 pending requests에서 제거
    if (error.config) {
      const requestKey = generateRequestKey(error.config);
      pendingRequests.delete(requestKey);
    }

    // 5xx 오류나 네트워크 오류 시 재시도
    if (error.response?.status >= 500 || !error.response) {
      const config = error.config;
      if (config && !config._retry) {
        config._retry = true;
        return retryRequest(axiosClient, config);
      }
    }

    // 401 오류 시 토큰 제거
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
        window.location.href = '/';
      }
    }

    return Promise.reject(error);
  }
);

// API 엔드포인트 헬퍼 (Gateway를 통한 라우팅)
export const apiEndpoints = {
  // Gateway 엔드포인트
  gateway: {
    health: '/health',
    status: '/status',
    routing: '/routing',
    architecture: '/architecture',
    templates: '/api/cbam/templates',
  },
  // Auth Service (Gateway를 통해)
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
    refresh: '/api/auth/refresh',
  },
  // Countries API (Gateway를 통해)
  countries: {
    search: '/api/v1/countries/search',
    all: '/api/v1/countries',
    byCode: '/api/v1/countries/code',
    byUnlocode: '/api/v1/countries/unlocode',
  },
  // LCA Service (Gateway를 통해)
  lca: {
    projects: '/api/lci/projects',
    calculations: '/api/lci/calculations',
    templates: '/api/lci/templates',
  },
  // CBAM Service (Gateway를 통해)
  cbam: {
    reports: '/api/cbam/reports',
    calculations: '/api/cbam/calculations',
    templates: '/api/cbam/templates',
  },
  // Calculation Service (Gateway를 통해 boundary 서비스로)
  calculation: {
    fuel: '/api/v1/boundary/calc/fuel/calculate',
    material: '/api/v1/boundary/calc/material/calculate',
    precursor: '/api/v1/boundary/calc/precursor/calculate',
    electricity: '/api/v1/boundary/calc/electricity/calculate',
    process: '/api/v1/boundary/calc/process/calculate',
    cbam: '/api/v1/boundary/calc/cbam',
    precursors: '/api/v1/boundary/calc/precursor/user',
    precursorsBatch: '/api/v1/boundary/calc/precursor/save-batch',
    stats: '/api/v1/boundary/calc/stats',
    history: '/api/v1/boundary/calc/history',
    
    // 새로운 테이블 API 엔드포인트들 (단수형으로 통일)
    boundary: {
        create: '/api/v1/boundary/boundary',
        list: '/api/v1/boundary/boundary'
    },
    product: {
        create: '/api/v1/boundary/product',
        list: '/api/v1/boundary/product',
        get: (id: number) => `/api/v1/boundary/product/${id}`,
        update: (id: number) => `/api/v1/boundary/product/${id}`,
        delete: (id: number) => `/api/v1/boundary/product/${id}`
    },
    operation: {
        create: '/api/v1/boundary/operation',
        list: '/api/v1/boundary/operation'
    },
    node: {
        create: '/api/v1/boundary/node',
        list: '/api/v1/boundary/node'
    },
    edge: {
        create: '/api/v1/boundary/edge',
        list: '/api/v1/boundary/edge'
    },
    productionEmission: {
        create: '/api/v1/boundary/production-emission',
        list: '/api/v1/boundary/production-emission'
    }
},
  // Data Upload (Gateway를 통해)
  upload: {
    data: '/api/datagather/upload',
    validate: '/api/datagather/validate',
  },
  // Dashboard (Gateway를 통해)
  dashboard: {
    overview: '/api/dashboard/overview',
    stats: '/api/dashboard/stats',
  },
  // Settings (Gateway를 통해)
  settings: {
    profile: '/api/settings/profile',
    organization: '/api/settings/organization',
    users: '/api/settings/users',
    apiKeys: '/api/settings/api-keys',
  },
} as const;

// 인증 관련 유틸리티 함수들
export const authUtils = {
  // 로그인 상태 확인
  isAuthenticated: (): boolean => {
    if (typeof window === 'undefined') return false;
    const token = localStorage.getItem('auth_token');
    return !!token;
  },

  // 사용자 이메일 가져오기
  getUserEmail: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('user_email');
  },

  // 로그아웃
  logout: async (): Promise<void> => {
    try {
      // 서버에 로그아웃 요청
      await axiosClient.post(apiEndpoints.auth.logout);
    } catch (error) {
      // 로그아웃 요청 실패 시에도 로컬 스토리지는 정리
    } finally {
      // 로컬 스토리지 정리
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
        window.location.href = '/';
      }
    }
  },

  // 토큰 갱신
  refreshToken: async (): Promise<boolean> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return false;

      const response = await axiosClient.post(apiEndpoints.auth.refresh, {
        refresh_token: refreshToken,
      });

      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        return true;
      }
      return false;
    } catch (error) {
      // 토큰 갱신 실패 시 로그아웃
      authUtils.logout();
      return false;
    }
  },
};

export default axiosClient;
