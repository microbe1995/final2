// ============================================================================
// 🔍 CBAM 데이터 검색 API Hook
// ============================================================================

import { useCallback } from 'react';
import { useAPI } from './useAPI';

// ============================================================================
// 📋 검색 요청/응답 타입 정의
// ============================================================================

interface HSCodeSearchResponse {
  success: boolean;
  message: string;
  page: number;
  page_size: number;
  total_count: number;
  hscodes: HSCodeData[];
}

interface HSCodeData {
  hs_code: string;
  hs_name_ko: string;
  hs_name_en: string;
  category: string;
  subcategory?: string;
}

interface CountrySearchRequest {
  query: string;
  search_type?: 'name' | 'code' | 'all';
  page?: number;
  page_size?: number;
}

interface CountrySearchResponse {
  success: boolean;
  message: string;
  page: number;
  page_size: number;
  total_count: number;
  countries: CountryData[];
}

interface CountryData {
  id: string;
  korean_name: string;
  country_name: string;
  code: string;
  unlocode?: string;
}

interface FuelSearchResponse {
  success: boolean;
  message: string;
  page: number;
  page_size: number;
  total_count: number;
  fuels: FuelData[];
}

interface FuelData {
  fuel_id: string;
  fuel_name: string;
  fuel_type: string;
  emission_factor: number;
  calorific_value: number;
  unit: string;
}

interface MaterialSearchResponse {
  success: boolean;
  message: string;
  page: number;
  page_size: number;
  total_count: number;
  materials: MaterialData[];
}

interface MaterialData {
  material_id: string;
  material_name: string;
  category: string;
  emission_factor: number;
  unit: string;
}

interface PrecursorSearchResponse {
  success: boolean;
  message: string;
  page: number;
  page_size: number;
  total_count: number;
  precursors: PrecursorData[];
}

interface PrecursorData {
  precursor_id: string;
  precursor_name: string;
  category: string;
  emission_factor: number;
  carbon_content?: number;
  unit: string;
}

// ============================================================================
// 🔍 데이터 검색 API Hook
// ============================================================================

export const useDataSearchAPI = () => {
  const api = useAPI('/api/v1/boundary');

  // 📊 HS코드 검색
  const searchHSCode = useCallback(
    async (
      hsCode: string,
      page: number = 1,
      pageSize: number = 10
    ): Promise<HSCodeSearchResponse | null> => {
      try {
        return await api.get(`/data/hscode/search?hs=${hsCode}&page=${page}&page_size=${pageSize}`);
      } catch (error) {
        console.error('HS코드 검색 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 🌍 국가 검색
  const searchCountry = useCallback(
    async (params: CountrySearchRequest): Promise<CountrySearchResponse | null> => {
      try {
        return await api.post('/data/country/search', params);
      } catch (error) {
        console.error('국가 검색 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 🔥 연료 검색
  const searchFuels = useCallback(
    async (
      query?: string,
      fuelType?: string,
      page: number = 1,
      pageSize: number = 10
    ): Promise<FuelSearchResponse | null> => {
      try {
        const params = new URLSearchParams();
        if (query) params.append('query', query);
        if (fuelType) params.append('fuel_type', fuelType);
        params.append('page', page.toString());
        params.append('page_size', pageSize.toString());

        return await api.get(`/data/fuels/search?${params.toString()}`);
      } catch (error) {
        console.error('연료 검색 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 🏭 원료 검색
  const searchMaterials = useCallback(
    async (
      query?: string,
      category?: string,
      page: number = 1,
      pageSize: number = 10
    ): Promise<MaterialSearchResponse | null> => {
      try {
        const params = new URLSearchParams();
        if (query) params.append('query', query);
        if (category) params.append('category', category);
        params.append('page', page.toString());
        params.append('page_size', pageSize.toString());

        return await api.get(`/data/materials/search?${params.toString()}`);
      } catch (error) {
        console.error('원료 검색 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 🔗 전구물질 검색
  const searchPrecursors = useCallback(
    async (
      query?: string,
      category?: string,
      page: number = 1,
      pageSize: number = 10
    ): Promise<PrecursorSearchResponse | null> => {
      try {
        const params = new URLSearchParams();
        if (query) params.append('query', query);
        if (category) params.append('category', category);
        params.append('page', page.toString());
        params.append('page_size', pageSize.toString());

        return await api.get(`/data/precursors/search?${params.toString()}`);
      } catch (error) {
        console.error('전구물질 검색 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 📊 검색 통계 조회
  const getSearchStats = useCallback(
    async (): Promise<any | null> => {
      try {
        return await api.get('/data/stats');
      } catch (error) {
        console.error('검색 통계 조회 실패:', error);
        return null;
      }
    },
    [api]
  );

  return {
    searchHSCode,
    searchCountry,
    searchFuels,
    searchMaterials,
    searchPrecursors,
    getSearchStats,
  };
};

export type {
  HSCodeSearchResponse,
  HSCodeData,
  CountrySearchRequest,
  CountrySearchResponse,
  CountryData,
  FuelSearchResponse,
  FuelData,
  MaterialSearchResponse,
  MaterialData,
  PrecursorSearchResponse,
  PrecursorData,
};
