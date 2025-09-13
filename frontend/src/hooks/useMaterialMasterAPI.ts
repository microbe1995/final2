import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useCommonAPI } from './useCommonAPI';

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
// 🔍 원료 마스터 API 훅 (@mapping/ 패턴과 동일)
// ============================================================================

export const useMaterialMasterAPI = () => {
  const { loading, error, getRequest, postRequest, putRequest, deleteRequest, clearError } = useCommonAPI();

  // ============================================================================
  // 🔍 원료명 조회 (메인 기능 - @mapping/의 lookupByHSCode와 동일 패턴)
  // ============================================================================

  const lookupMaterialByName = useCallback(async (mat_name: string): Promise<MaterialNameLookupResponse> => {
    const result = await getRequest<any>(apiEndpoints.materialMaster.search(mat_name));
    if (result) {
      const materials = Array.isArray(result) ? result : [];
      return {
        success: true,
        data: materials,
        count: materials.length,
        message: `${materials.length}개의 원료를 찾았습니다.`
      };
    }
    return {
      success: false,
      data: [],
      count: 0,
      message: '원료명 조회 실패'
    };
  }, [getRequest]);

  // ============================================================================
  // 📋 기본 CRUD 작업
  // ============================================================================

  const getMaterialMasterList = useCallback(async (skip = 0, limit = 100): Promise<MaterialMappingFull[]> => {
    const result = await getRequest<any>(apiEndpoints.materialMaster.list, { skip, limit });
    if (result) {
      // API 응답이 { materials: [], total_count: number } 형식인지 확인
      if (result.materials) {
        return result.materials;
      }
      // 배열을 직접 반환하는 경우
      return Array.isArray(result) ? result : [];
    }
    return [];
  }, [getRequest]);

  const searchMaterialByName = useCallback(async (matName: string): Promise<MaterialNameLookupResponse> => {
    // lookupMaterialByName과 동일한 로직 사용
    return await lookupMaterialByName(matName);
  }, [lookupMaterialByName]);

  const getMaterialFactor = useCallback(async (matName: string): Promise<MaterialNameLookupResponse> => {
    // lookupMaterialByName과 동일한 로직 사용
    return await lookupMaterialByName(matName);
  }, [lookupMaterialByName]);

  // ============================================================================
  // 🚀 자동 매핑 기능 (프론트엔드 편의 기능)
  // ============================================================================

  const getMaterialNameSuggestions = useCallback(async (query: string): Promise<string[]> => {
    if (!query.trim()) return [];
    
    try {
      const result = await lookupMaterialByName(query);
      if (result.success && result.data.length > 0) {
        // 원료명만 추출하여 반환
        return result.data.map((item: MaterialMapping) => item.mat_name);
      }
      return [];
    } catch (err) {
      return [];
    }
  }, [lookupMaterialByName]);

  const autoMapMaterialFactor = useCallback(async (matName: string): Promise<number | null> => {
    try {
      const result = await lookupMaterialByName(matName);
      if (result.success && result.data.length > 0) {
        // 첫 번째 결과의 배출계수 반환
        return result.data[0].mat_factor;
      }
      return null;
    } catch (err) {
      return null;
    }
  }, [lookupMaterialByName]);

  return {
    loading,
    error,
    clearError,
    // 메인 기능
    lookupMaterialByName,
    // 기본 CRUD
    getMaterialMasterList,
    searchMaterialByName,
    getMaterialFactor,
    // 자동 매핑 기능
    getMaterialNameSuggestions,
    autoMapMaterialFactor,
  };
};
