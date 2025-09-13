import { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { FuelMaster, FuelMasterList, FuelMasterFactor } from '@/lib/types';
import { useCommonAPI } from './useCommonAPI';

export const useFuelMasterAPI = () => {
  const { loading, error, getRequest, postRequest, putRequest, deleteRequest, clearError } = useCommonAPI();

  // 모든 연료 마스터 데이터 조회
  const getAllFuels = useCallback(async (): Promise<FuelMasterList | null> => {
    return await getRequest<FuelMasterList>(apiEndpoints.cbam.fuelMaster.list);
  }, [getRequest]);

  // 연료명으로 검색
  const searchFuels = useCallback(async (searchTerm: string): Promise<FuelMaster[] | null> => {
    if (!searchTerm.trim()) {
      return [];
    }
    return await getRequest<FuelMaster[]>(apiEndpoints.cbam.fuelMaster.search(searchTerm));
  }, [getRequest]);

  // 연료명으로 배출계수 조회 (자동 매핑)
  const getFuelFactor = useCallback(async (fuelName: string): Promise<FuelMasterFactor | null> => {
    if (!fuelName.trim()) {
      return null;
    }
    return await getRequest<FuelMasterFactor>(apiEndpoints.cbam.fuelMaster.getFactor(fuelName));
  }, [getRequest]);

  // 자동 배출계수로 연료 생성
  const createFuelDirWithAutoFactor = useCallback(async (fuelDirData: any): Promise<any | null> => {
    return await postRequest<any>(apiEndpoints.cbam.fuelMaster.autoFactor, fuelDirData);
  }, [postRequest]);

  return {
    loading,
    error,
    clearError,
    getAllFuels,
    searchFuels,
    getFuelFactor,
    createFuelDirWithAutoFactor,
  };
};
