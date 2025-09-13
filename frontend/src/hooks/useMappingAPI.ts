import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useCommonAPI } from './useCommonAPI';

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
  const { loading, error, getRequest, postRequest, putRequest, deleteRequest, clearError } = useCommonAPI();

  // ============================================================================
  // 🔍 HS 코드 조회 (메인 기능)
  // ============================================================================

  const lookupByHSCode = useCallback(async (hs_code_10: string): Promise<HSCNMappingResponse[]> => {
    const result = await getRequest<HSCNMappingResponse[]>(apiEndpoints.cbam.mapping.lookup(hs_code_10));
    return result || [];
  }, [getRequest]);

  // ============================================================================
  // 📋 기본 CRUD 작업
  // ============================================================================

  const getAllMappings = useCallback(async (skip = 0, limit = 100): Promise<HSCNMappingFullResponse[]> => {
    const result = await getRequest<HSCNMappingFullResponse[]>(apiEndpoints.cbam.mapping.list, { skip, limit });
    return result || [];
  }, [getRequest]);

  const getMappingById = useCallback(async (id: number): Promise<HSCNMappingFullResponse> => {
    const result = await getRequest<HSCNMappingFullResponse>(apiEndpoints.cbam.mapping.get(id));
    if (!result) {
      throw new Error('매핑 조회 중 오류가 발생했습니다.');
    }
    return result;
  }, [getRequest]);

  const createMapping = useCallback(async (mappingData: {
    hscode: string;
    aggregoods_name?: string;
    aggregoods_engname?: string;
    cncode_total: string;
    goods_name?: string;
    goods_engname?: string;
  }): Promise<HSCNMappingFullResponse> => {
    const result = await postRequest<HSCNMappingFullResponse>(apiEndpoints.cbam.mapping.create, mappingData);
    if (!result) {
      throw new Error('매핑 생성 중 오류가 발생했습니다.');
    }
    return result;
  }, [postRequest]);

  const updateMapping = useCallback(async (id: number, mappingData: Partial<{
    hscode: string;
    aggregoods_name: string;
    aggregoods_engname: string;
    cncode_total: string;
    goods_name: string;
    goods_engname: string;
  }>): Promise<HSCNMappingFullResponse> => {
    const result = await putRequest<HSCNMappingFullResponse>(apiEndpoints.cbam.mapping.update(id), mappingData);
    if (!result) {
      throw new Error('매핑 수정 중 오류가 발생했습니다.');
    }
    return result;
  }, [putRequest]);

  const deleteMapping = useCallback(async (id: number): Promise<void> => {
    const result = await deleteRequest(apiEndpoints.cbam.mapping.delete(id));
    if (!result) {
      throw new Error('매핑 삭제 중 오류가 발생했습니다.');
    }
  }, [deleteRequest]);

  // ============================================================================
  // 🔍 검색 기능
  // ============================================================================

  const searchByHSCode = useCallback(async (hs_code: string): Promise<HSCNMappingFullResponse[]> => {
    const result = await getRequest<HSCNMappingFullResponse[]>(apiEndpoints.cbam.mapping.search.hs(hs_code));
    return result || [];
  }, [getRequest]);

  const searchByCNCode = useCallback(async (cn_code: string): Promise<HSCNMappingFullResponse[]> => {
    const result = await getRequest<HSCNMappingFullResponse[]>(apiEndpoints.cbam.mapping.search.cn(cn_code));
    return result || [];
  }, [getRequest]);

  const searchByGoodsName = useCallback(async (goods_name: string): Promise<HSCNMappingFullResponse[]> => {
    const result = await getRequest<HSCNMappingFullResponse[]>(apiEndpoints.cbam.mapping.search.goods(goods_name));
    return result || [];
  }, [getRequest]);

  // ============================================================================
  // 📊 통계
  // ============================================================================

  const getMappingStats = useCallback(async (): Promise<MappingStatsResponse> => {
    const result = await getRequest<MappingStatsResponse>(apiEndpoints.cbam.mapping.stats);
    if (!result) {
      throw new Error('매핑 통계 조회 중 오류가 발생했습니다.');
    }
    return result;
  }, [getRequest]);

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
    const result = await postRequest<{
      success: boolean;
      created_count: number;
      failed_count: number;
      errors: string[];
    }>(apiEndpoints.cbam.mapping.batch, { mappings });
    if (!result) {
      throw new Error('매핑 일괄 생성 중 오류가 발생했습니다.');
    }
    return result;
  }, [postRequest]);

  // ============================================================================
  // 🔧 유틸리티 (useCommonAPI에서 제공됨)
  // ============================================================================

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
