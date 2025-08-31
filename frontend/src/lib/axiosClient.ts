import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from 'axios';

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
  // Gateway 엔드포인트 (실제 사용되는 것만)
  gateway: {
    health: '/health',
    status: '/status',
    routing: '/routing',
    architecture: '/architecture',
  },
  // Auth Service (Gateway를 통해)
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
    refresh: '/api/auth/refresh',
  },
  // CBAM Service (Gateway를 통해)
  cbam: {
    install: {
      // 🔴 수정: 중복 경로 제거 (Gateway: /api/v1/install → CBAM: /install)
      create: '/api/v1/install',
      list: '/api/v1/install',
      names: '/api/v1/install/names',
      get: (id: number) => `/api/v1/install/${id}`,
      update: (id: number) => `/api/v1/install/${id}`,
      delete: (id: number) => `/api/v1/install/${id}`
    },
    product: {
      create: '/api/v1/product',
      list: '/api/v1/product',
      names: '/api/v1/product/names',
      get: (id: number) => `/api/v1/product/${id}`,
      update: (id: number) => `/api/v1/product/${id}`,
      delete: (id: number) => `/api/v1/product/${id}`
    },
    process: {
      create: '/api/v1/process',
      list: '/api/v1/process',
      get: (id: number) => `/api/v1/process/${id}`,
      update: (id: number) => `/api/v1/process/${id}`,
      delete: (id: number) => `/api/v1/process/${id}`
    },
    // HS-CN 매핑 API
    mapping: {
      lookup: (hs_code: string) => `/api/v1/mapping/cncode/lookup/${hs_code}`,
      list: '/api/v1/mapping',
      get: (id: number) => `/api/v1/mapping/${id}`,
      create: '/api/v1/mapping',
      update: (id: number) => `/api/v1/mapping/${id}`,
      delete: (id: number) => `/api/v1/mapping/${id}`,
      search: {
        hs: (hs_code: string) => `/api/v1/mapping/search/hs/${hs_code}`,
        cn: (cn_code: string) => `/api/v1/mapping/search/cn/${cn_code}`,
        goods: (goods_name: string) => `/api/v1/mapping/search/goods/${goods_name}`
      },
      stats: '/api/v1/mapping/stats',
      batch: '/api/v1/mapping/batch'
    }
  },
  // Calculation Service (Gateway를 통해 직접 서비스로)
  calculation: {
    process: {
      calculate: '/api/v1/calculation/emission/process/calculate'
    },
    
    // Process Chain 관련 API
    processchain: {
        list: '/api/v1/processchain/chain',
        create: '/api/v1/processchain/chain',
        get: (id: number) => `/api/v1/processchain/chain/${id}`,
        delete: (id: number) => `/api/v1/processchain/chain/${id}`,
        chain: '/api/v1/processchain/chain',
        test: '/api/v1/processchain/test'
    },
    edge: {
        create: '/api/v1/edge',
        list: '/api/v1/edge',
        get: (id: number) => `/api/v1/edge/${id}`,
        delete: (id: number) => `/api/v1/edge/${id}`
    },
    matdir: {
        create: '/api/v1/matdir',
        list: '/api/v1/matdir',
        get: (id: number) => `/api/v1/matdir/${id}`,
        update: (id: number) => `/api/v1/matdir/${id}`,
        delete: (id: number) => `/api/v1/matdir/${id}`,
        byProcess: (process_id: number) => `/api/v1/matdir/process/${process_id}`,
        calculate: '/api/v1/matdir/calculate',
        totalByProcess: (process_id: number) => `/api/v1/matdir/process/${process_id}/total`
    },
    fueldir: {
        create: '/api/v1/fueldir',
        list: '/api/v1/fueldir',
        get: (id: number) => `/api/v1/fueldir/${id}`,
        update: (id: number) => `/api/v1/fueldir/${id}`,
        delete: (id: number) => `/api/v1/fueldir/${id}`,
        byProcess: (process_id: number) => `/api/v1/fueldir/process/${process_id}`,
        calculate: '/api/v1/fueldir/calculate',
        totalByProcess: (process_id: number) => `/api/v1/fueldir/process/${process_id}/total`
    },
    // Fuel Master API
    fuelMaster: {
        list: '/api/v1/fueldir/fuel-master',
        search: (fuel_name: string) => `/api/v1/fueldir/fuel-master/search/${fuel_name}`,
        getFactor: (fuel_name: string) => `/api/v1/fueldir/fuel-master/factor/${fuel_name}`,
        autoFactor: '/api/v1/fueldir/auto-factor'
    },
    // Product-Process 관계 API
    productProcess: {
        create: '/api/v1/productprocess',
        list: '/api/v1/productprocess',
        get: (id: number) => `/api/v1/productprocess/${id}`,
        update: (id: number) => `/api/v1/productprocess/${id}`,
        delete: (id: number) => `/api/v1/productprocess/${id}`,
        byProduct: (product_id: number) => `/api/v1/productprocess/product/${product_id}`,
        byProcess: (process_id: number) => `/api/v1/productprocess/process/${process_id}`,
        stats: '/api/v1/productprocess/stats'
    },
    // Material 계산 API
    material: '/api/v1/calculation/emission/process/attrdir',
    // Precursor 관련 API
    precursors: '/api/v1/calculation/emission/process/attrdir/all',
    precursorsBatch: '/api/v1/calculation/emission/process/attrdir/batch',
    precursor: '/api/v1/calculation/emission/process/attrdir',
    // CBAM 계산 API
    cbam: '/api/v1/calculation/emission/process/calculate',
    // Electricity 계산 API
    electricity: '/api/v1/calculation/emission/process/calculate',
    // 통계 및 이력 API
    stats: '/api/v1/calculation/emission/process/attrdir/all',
    history: '/api/v1/calculation/emission/process/attrdir/all'
  },
  // Material Master API (matdir 서비스 사용) - 경로 패턴 통일
  materialMaster: {
      list: '/api/v1/matdir',
      search: (mat_name: string) => `/api/v1/matdir/search/${mat_name}`,
      getFactor: (mat_name: string) => `/api/v1/matdir/factor/${mat_name}`,
      autoFactor: '/api/v1/matdir/auto-factor'
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
