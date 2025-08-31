import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { FuelMaster, FuelMasterList, FuelMasterFactor } from '@/lib/types';

export const useFuelMasterAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 모든 연료 마스터 데이터 조회
  const getAllFuels = useCallback(async (): Promise<FuelMasterList | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.get(apiEndpoints.cbam.fuelMaster.list);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '연료 마스터 데이터 조회 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('연료 마스터 데이터 조회 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 연료명으로 검색
  const searchFuels = useCallback(async (searchTerm: string): Promise<FuelMaster[] | null> => {
    if (!searchTerm.trim()) {
      return [];
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.get(
        apiEndpoints.cbam.fuelMaster.search(searchTerm)
      );
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '연료 검색 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('연료 검색 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 연료명으로 배출계수 조회 (자동 매핑)
  const getFuelFactor = useCallback(async (fuelName: string): Promise<FuelMasterFactor | null> => {
    if (!fuelName.trim()) {
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.get(
        apiEndpoints.cbam.fuelMaster.getFactor(fuelName)
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

  // 자동 배출계수로 연료 생성
  const createFuelDirWithAutoFactor = useCallback(async (fuelDirData: any): Promise<any | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.post(
        apiEndpoints.cbam.fuelMaster.autoFactor,
        fuelDirData
      );
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '연료 데이터 생성 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('연료 데이터 생성 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getAllFuels,
    searchFuels,
    getFuelFactor,
    createFuelDirWithAutoFactor,
  };
};
