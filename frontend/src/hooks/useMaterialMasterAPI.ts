import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

// ============================================================================
// 📝 MatDir 스키마 기반 타입 정의
// ============================================================================

export interface MaterialMapping {
  mat_name: string;
  mat_factor: number;
  carbon_content?: number;
  mat_engname?: string;
}

export interface MaterialMappingFull {
  id: number;
  mat_name: string;
  mat_factor: number;
  carbon_content?: number;
  mat_engname?: string;
}

export interface MaterialNameLookupResponse {
  success: boolean;
  data: MaterialMapping[];
  count: number;
  message?: string;
}

// ============================================================================
// 🔍 원료 마스터 API 훅
// ============================================================================

export const useMaterialMasterAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 원료 마스터 목록 조회
  const getMaterialMasterList = useCallback(async (skip = 0, limit = 100): Promise<MaterialMappingFull[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.calculation.materialMaster.list, {
        params: { skip, limit }
      });
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '알 수 없는 오류가 발생했습니다';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 원료명으로 검색
  const searchMaterialByName = useCallback(async (matName: string): Promise<MaterialNameLookupResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.calculation.materialMaster.search(matName));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '알 수 없는 오류가 발생했습니다';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 원료명으로 배출계수 조회
  const getMaterialFactor = useCallback(async (matName: string): Promise<MaterialNameLookupResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.calculation.materialMaster.getFactor(matName));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '알 수 없는 오류가 발생했습니다';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 원료명 자동 완성 (검색 결과에서 원료명만 추출)
  const getMaterialNameSuggestions = useCallback(async (query: string): Promise<string[]> => {
    if (!query.trim()) return [];
    
    try {
      const result = await searchMaterialByName(query);
      return result.data.map((item: MaterialMapping) => item.mat_name);
    } catch (err) {
      return [];
    }
  }, [searchMaterialByName]);

  // 배출계수 자동 매핑 (원료명으로 배출계수 자동 찾기)
  const autoMapMaterialFactor = useCallback(async (matName: string): Promise<number | null> => {
    try {
      const result = await getMaterialFactor(matName);
      if (result.success && result.data.length > 0) {
        // 첫 번째 결과의 배출계수 반환
        return result.data[0].mat_factor;
      }
      return null;
    } catch (err) {
      return null;
    }
  }, [getMaterialFactor]);

  return {
    loading,
    error,
    getMaterialMasterList,
    searchMaterialByName,
    getMaterialFactor,
    getMaterialNameSuggestions,
    autoMapMaterialFactor,
  };
};
