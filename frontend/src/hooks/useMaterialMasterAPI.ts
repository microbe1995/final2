import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { MaterialMaster, MaterialMasterList, MaterialMasterFactor } from '@/lib/types';

export const useMaterialMasterAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 모든 원료 마스터 데이터 조회
  const getAllMaterials = useCallback(async (): Promise<MaterialMasterList | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(apiEndpoints.calculation.materialMaster.list);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '원료 마스터 데이터 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('원료 마스터 데이터 조회 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 원료명으로 검색
  const searchMaterials = useCallback(async (searchTerm: string): Promise<MaterialMaster[] | null> => {
    if (!searchTerm.trim()) {
      return [];
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(
        apiEndpoints.calculation.materialMaster.search(searchTerm)
      );
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '원료 검색 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('원료 검색 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 원료명으로 배출계수 조회 (자동 매핑)
  const getMaterialFactor = useCallback(async (matName: string): Promise<MaterialMasterFactor | null> => {
    if (!matName.trim()) {
      return null;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.get(
        apiEndpoints.calculation.materialMaster.getFactor(matName)
      );
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '배출계수 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('배출계수 조회 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 자동 배출계수로 원료 생성
  const createMatDirWithAutoFactor = useCallback(async (matDirData: any): Promise<any | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosClient.post(
        apiEndpoints.calculation.materialMaster.autoFactor,
        matDirData
      );
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '원료 데이터 생성 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('원료 데이터 생성 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getAllMaterials,
    searchMaterials,
    getMaterialFactor,
    createMatDirWithAutoFactor,
  };
};
