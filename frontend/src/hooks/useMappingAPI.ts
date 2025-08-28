import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

// ============================================================================
// 📋 HS-CN 매핑 API 훅
// ============================================================================

export interface HSCNMappingResponse {
  cncode_total: string;
  goods_name?: string;
  goods_engname?: string;
  aggregoods_name?: string;
  aggregoods_engname?: string;
}

export interface HSCNMappingFullResponse extends HSCNMappingResponse {
  id: number;
  hscode: string;
  created_at?: string;
  updated_at?: string;
}

export interface MappingStatsResponse {
  total_mappings: number;
  unique_hscodes: number;
  unique_cncodes: number;
  last_updated?: string;
}

export interface HSCodeLookupResponse {
  success: boolean;
  data: HSCNMappingResponse[];
  count: number;
  message?: string;
}

export const useMappingAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ============================================================================
  // 🔍 HS 코드 조회 (메인 기능)
  // ============================================================================

  const lookupByHSCode = useCallback(async (hs_code_10: string): Promise<HSCNMappingResponse[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.lookup(hs_code_10));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'HS 코드 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================================
  // 📋 기본 CRUD 작업
  // ============================================================================

  const getAllMappings = useCallback(async (skip = 0, limit = 100): Promise<HSCNMappingFullResponse[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.list, {
        params: { skip, limit }
      });
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 목록 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const getMappingById = useCallback(async (id: number): Promise<HSCNMappingFullResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.get(id));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const createMapping = useCallback(async (mappingData: {
    hscode: string;
    aggregoods_name?: string;
    aggregoods_engname?: string;
    cncode_total: string;
    goods_name?: string;
    goods_engname?: string;
  }): Promise<HSCNMappingFullResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.mapping.create, mappingData);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 생성 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateMapping = useCallback(async (id: number, mappingData: Partial<{
    hscode: string;
    aggregoods_name: string;
    aggregoods_engname: string;
    cncode_total: string;
    goods_name: string;
    goods_engname: string;
  }>): Promise<HSCNMappingFullResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.put(apiEndpoints.cbam.mapping.update(id), mappingData);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 수정 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteMapping = useCallback(async (id: number): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      await axiosClient.delete(apiEndpoints.cbam.mapping.delete(id));
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 삭제 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================================
  // 🔍 검색 기능
  // ============================================================================

  const searchByHSCode = useCallback(async (hs_code: string): Promise<HSCNMappingFullResponse[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.search.hs(hs_code));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'HS 코드 검색 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const searchByCNCode = useCallback(async (cn_code: string): Promise<HSCNMappingFullResponse[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.search.cn(cn_code));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'CN 코드 검색 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const searchByGoodsName = useCallback(async (goods_name: string): Promise<HSCNMappingFullResponse[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.search.goods(goods_name));
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '품목명 검색 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================================
  // 📊 통계
  // ============================================================================

  const getMappingStats = useCallback(async (): Promise<MappingStatsResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.mapping.stats);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 통계 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================================
  // 📦 일괄 처리
  // ============================================================================

  const createMappingsBatch = useCallback(async (mappings: Array<{
    hscode: string;
    aggregoods_name?: string;
    aggregoods_engname?: string;
    cncode_total: string;
    goods_name?: string;
    goods_engname?: string;
  }>): Promise<{
    success: boolean;
    created_count: number;
    failed_count: number;
    errors: string[];
  }> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.mapping.batch, {
        mappings
      });
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '매핑 일괄 생성 중 오류가 발생했습니다.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================================
  // 🔧 유틸리티
  // ============================================================================

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // 상태
    loading,
    error,
    
    // 메인 기능
    lookupByHSCode,
    
    // CRUD
    getAllMappings,
    getMappingById,
    createMapping,
    updateMapping,
    deleteMapping,
    
    // 검색
    searchByHSCode,
    searchByCNCode,
    searchByGoodsName,
    
    // 통계
    getMappingStats,
    
    // 일괄 처리
    createMappingsBatch,
    
    // 유틸리티
    clearError
  };
};
