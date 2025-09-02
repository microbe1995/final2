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
  // 상대 경로나 전체 URL 모두 처리
  const path = url.startsWith('http') ? new URL(url).pathname : url;
  return path.startsWith('/api/') || path.startsWith('/health');
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
  // 🔴 수정: 환경변수 기반 Gateway URL 사용 (상대 경로 대신)
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  // 🔴 수정: withCredentials 제거 (쿠키 미사용)
  withCredentials: false,
});

// 🔴 추가: 환경변수 검증 및 경고
if (typeof window !== 'undefined') {
  const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!baseURL) {
    console.warn('[AXIOS] NEXT_PUBLIC_API_BASE_URL 환경변수가 설정되지 않았습니다.');
  } else if (!baseURL.startsWith('https://')) {
    console.warn('[AXIOS] NEXT_PUBLIC_API_BASE_URL이 https로 시작하지 않습니다:', baseURL);
  } else if (!baseURL.includes('gateway-production-22ef.up.railway.app')) {
    console.warn('[AXIOS] NEXT_PUBLIC_API_BASE_URL이 올바른 Gateway URL이 아닙니다:', baseURL);
  } else {
    console.log('[AXIOS] Gateway URL 확인됨:', baseURL);
  }
}

// 요청 인터셉터
axiosClient.interceptors.request.use(
  config => {
    // 🔴 수정: 개발 환경에서만 로깅 (더 엄격한 조건)
    if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
      console.log('🚀 API 요청:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        fullURL: config.baseURL && config.url ? config.baseURL + config.url : 'N/A'
      });
    }
    
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

    // 🔴 수정: API 요청 검증 완화 (CORS 문제 해결을 위해)
    // if (config.url && !isAPIRequest(config.url)) {
    //   throw new Error(
    //     'Direct service access is not allowed. Use API routes only.'
    //   );
    // }

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
    // 🔴 수정: 개발 환경에서만 로깅 (더 엄격한 조건)
    if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
      console.log('✅ API 응답 성공:', {
        method: response.config.method?.toUpperCase(),
        url: response.config.url,
        status: response.status,
        statusText: response.statusText,
        dataLength: response.data?.length || 0
      });
    }
    
    // 요청 완료 시 pending requests에서 제거
    const requestKey = generateRequestKey(response.config);
    pendingRequests.delete(requestKey);
    return response;
  },
  async error => {
    // 🔴 수정: 개발 환경에서만 로깅 (더 엄격한 조건)
    if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
      console.error('❌ API 응답 에러:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          method: error.config?.method?.toUpperCase(),
          url: error.config?.url,
          fullURL: error.config?.baseURL && error.config?.url ? error.config?.baseURL + error.config?.url : 'N/A'
        }
      });
    }
    
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
      // Gateway: /api/v1/cbam/install/{path} → CBAM: /install/{path}
      create: '/api/v1/cbam/install',
      list: '/api/v1/cbam/install',
      names: '/api/v1/cbam/install/names',
      get: (id: number) => `/api/v1/cbam/install/${id}`,
      update: (id: number) => `/api/v1/cbam/install/${id}`,
      delete: (id: number) => `/api/v1/cbam/install/${id}`
    },
    product: {
      // Gateway: /api/v1/cbam/product/{path} → CBAM: /product/{path}
      create: '/api/v1/cbam/product',
      list: '/api/v1/cbam/product',
      names: '/api/v1/cbam/product/names',
      get: (id: number) => `/api/v1/cbam/product/${id}`,
      update: (id: number) => `/api/v1/cbam/product/${id}`,
      delete: (id: number) => `/api/v1/cbam/product/${id}`
    },
    process: {
      // Gateway: /api/v1/cbam/process/{path} → CBAM: /process/{path}
      create: '/api/v1/cbam/process',
      list: '/api/v1/cbam/process',
      get: (id: number) => `/api/v1/cbam/process/${id}`,
      update: (id: number) => `/api/v1/cbam/process/${id}`,
      delete: (id: number) => `/api/v1/cbam/process/${id}`
    },
    // HS-CN 매핑 API
    mapping: {
      // Gateway: /api/v1/cbam/mapping/{path} → CBAM: /mapping/{path}
      lookup: (hs_code: string) => `/api/v1/cbam/mapping/cncode/lookup/${hs_code}`,
      list: '/api/v1/cbam/mapping',
      get: (id: number) => `/api/v1/cbam/mapping/${id}`,
      create: '/api/v1/cbam/mapping',
      update: (id: number) => `/api/v1/cbam/mapping/${id}`,
      delete: (id: number) => `/api/v1/cbam/mapping/${id}`,
      search: {
        hs: (hs_code: string) => `/api/v1/cbam/mapping/search/hs/${hs_code}`,
        cn: (cn_code: string) => `/api/v1/cbam/mapping/search/cn/${cn_code}`,
        goods: (goods_name: string) => `/api/v1/cbam/mapping/search/goods/${goods_name}`
      },
      stats: '/api/v1/cbam/mapping/stats',
      batch: '/api/v1/cbam/mapping/batch'
    },
    // CBAM 계산 API
    cbam: '/api/v1/cbam/calculation/emission/process/calculate',
    
    // Dummy 데이터 API
    dummy: {
      // Gateway: /api/v1/cbam/dummy/{path} → CBAM: /dummy/{path}
      create: '/api/v1/cbam/dummy',
      list: '/api/v1/cbam/dummy',
      get: (id: number) => `/api/v1/cbam/dummy/${id}`,
      update: (id: number) => `/api/v1/cbam/dummy/${id}`,
      delete: (id: number) => `/api/v1/cbam/dummy/${id}`,
      search: '/api/v1/cbam/dummy',
      byProcess: (process_name: string) => `/api/v1/cbam/dummy/search/process/${process_name}`,
      byProduct: (product_name: string) => `/api/v1/cbam/dummy/search/product/${product_name}`,
      count: '/api/v1/cbam/dummy/stats/count',
      health: '/api/v1/cbam/dummy/health',
          // 제품명 관련 API
    productNames: '/api/v1/cbam/dummy/products/names',  // 고유 제품명 목록
    productNamesByPeriod: '/api/v1/cbam/dummy/products/names/by-period',  // 기간별 제품명 목록
    
    // 공정명 관련 API (제품명과 동일한 패턴)
    processNames: '/api/v1/cbam/dummy/processes/names',  // 고유 공정명 목록
    processNamesByPeriod: '/api/v1/cbam/dummy/processes/names/by-period'  // 기간별 공정명 목록
    },
    
    // Process Chain 관련 API
    edge: {
      // Gateway: /api/v1/cbam/edge/{path} → CBAM: /edge/{path}
      create: '/api/v1/cbam/edge',
      list: '/api/v1/cbam/edge',
      get: (id: number) => `/api/v1/cbam/edge/${id}`,
      delete: (id: number) => `/api/v1/cbam/edge/${id}`
    },
    
    matdir: {
      // Gateway: /api/v1/cbam/matdir/{path} → CBAM: /matdir/{path}
      create: '/api/v1/cbam/matdir/create',
      list: '/api/v1/cbam/matdir/list',
      get: (id: number) => `/api/v1/cbam/matdir/${id}`,
      update: (id: number) => `/api/v1/cbam/matdir/${id}`,
      delete: (id: number) => `/api/v1/cbam/matdir/${id}`,
      byProcess: (process_id: number) => `/api/v1/cbam/matdir/process/${process_id}`,
      calculate: '/api/v1/cbam/matdir/calculate',
      totalByProcess: (process_id: number) => `/api/v1/cbam/matdir/process/${process_id}/total`
    },
    
    fueldir: {
      // Gateway: /api/v1/cbam/fueldir/{path} → CBAM: /fueldir/{path}
      create: '/api/v1/cbam/fueldir/create',
      list: '/api/v1/cbam/fueldir/list',
      get: (id: number) => `/api/v1/cbam/fueldir/${id}`,
      update: (id: number) => `/api/v1/cbam/fueldir/${id}`,
      delete: (id: number) => `/api/v1/cbam/fueldir/${id}`,
      byProcess: (process_id: number) => `/api/v1/cbam/fueldir/process/${process_id}`,
      calculate: '/api/v1/cbam/fueldir/calculate',
      totalByProcess: (process_id: number) => `/api/v1/cbam/fueldir/process/${process_id}/total`
    },
    
    // Fuel Master API
    fuelMaster: {
      // Gateway: /api/v1/cbam/fueldir/fuel-master/{path} → CBAM: /fueldir/fuel-master/{path}
      list: '/api/v1/cbam/fueldir/fuel-master',
      search: (fuel_name: string) => `/api/v1/cbam/fueldir/fuel-master/search/${fuel_name}`,
      getFactor: (fuel_name: string) => `/api/v1/cbam/fueldir/fuel-master/factor/${fuel_name}`,
      autoFactor: '/api/v1/cbam/fueldir/auto-factor'
    },
    
    // Product-Process 관계 API
    productProcess: {
      // Gateway: /api/v1/cbam/productprocess/{path} → CBAM: /productprocess/{path}
      create: '/api/v1/cbam/productprocess',
      list: '/api/v1/cbam/productprocess',
      get: (id: number) => `/api/v1/cbam/productprocess/${id}`,
      update: (id: number) => `/api/v1/cbam/productprocess/${id}`,
      delete: (id: number) => `/api/v1/cbam/productprocess/${id}`,
      byProduct: (product_id: number) => `/api/v1/cbam/productprocess/product/${product_id}`,
      byProcess: (process_id: number) => `/api/v1/cbam/productprocess/process/${process_id}`,
      stats: '/api/v1/cbam/productprocess/stats'
    },
    
    // Calculation 관련 API
    calculation: {
      // Process 배출량 계산 API (직접귀속배출량)
      process: {
        calculate: '/api/v1/cbam/calculation/emission/process/calculate',
        attrdir: (process_id: number) => `/api/v1/cbam/calculation/emission/process/${process_id}/attrdir`,
        attrdirAll: '/api/v1/cbam/calculation/emission/process/attrdir/all'
      },
      // Product 배출량 계산 API
      product: {
        calculate: '/api/v1/cbam/calculation/emission/product/calculate'
      }
    }
  },
  // Material Master API (CBAM 통합 서비스 사용) - 경로 패턴 통일
  materialMaster: {
      // Gateway: /api/v1/cbam/matdir/material-master/{path} → CBAM: /matdir/material-master/{path}
      list: '/api/v1/cbam/matdir/material-master',
      search: (mat_name: string) => `/api/v1/cbam/matdir/material-master/search/${mat_name}`,
      getFactor: (mat_name: string) => `/api/v1/cbam/matdir/material-master/factor/${mat_name}`,
      autoFactor: '/api/v1/cbam/matdir/material-master/auto-factor'
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
