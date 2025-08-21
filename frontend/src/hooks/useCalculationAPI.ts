// ============================================================================
// 🧮 CBAM 계산 API Hook
// ============================================================================

import { useCallback } from 'react';
import { useAPI } from './useAPI';

// ============================================================================
// 📋 계산 요청/응답 타입 정의
// ============================================================================

interface FuelCalculationRequest {
  fuel_name: string;
  activity_data: number;
  activity_unit: string;
  emission_factor?: number;
  calorific_value?: number;
  oxidation_factor?: number;
}

interface FuelCalculationResponse {
  result_id: string;
  fuel_name: string;
  activity_data: number;
  activity_unit: string;
  emission_factor: number;
  calorific_value: number;
  oxidation_factor: number;
  total_emissions: number;
  calculation_timestamp: string;
  message: string;
}

interface MaterialCalculationRequest {
  material_name: string;
  activity_data: number;
  activity_unit: string;
  emission_factor?: number;
  conversion_factor?: number;
}

interface MaterialCalculationResponse {
  result_id: string;
  material_name: string;
  activity_data: number;
  activity_unit: string;
  emission_factor: number;
  conversion_factor: number;
  total_emissions: number;
  calculation_timestamp: string;
  message: string;
}

interface PrecursorData {
  precursor_id: string;
  precursor_name: string;
  quantity: number;
  unit: string;
  emission_factor: number;
  carbon_content?: number;
}

interface CBAMCalculationRequest {
  product_name: string;
  fuel_emissions: number;
  material_emissions: number;
  precursor_emissions: number;
  cbam_rate?: number;
  currency?: string;
}

interface CBAMCalculationResponse {
  calculation_id: string;
  product_name: string;
  fuel_emissions: number;
  material_emissions: number;
  precursor_emissions: number;
  total_emissions: number;
  cbam_rate: number;
  cbam_cost: number;
  currency: string;
  calculation_timestamp: string;
  message: string;
}

// ============================================================================
// 🧮 계산 API Hook
// ============================================================================

export const useCalculationAPI = () => {
  const api = useAPI('/api/v1/boundary');

  // 🔥 연료 배출량 계산
  const calculateFuelEmission = useCallback(
    async (data: FuelCalculationRequest): Promise<FuelCalculationResponse | null> => {
      try {
        return await api.post('/calc/fuel/calculate', data);
      } catch (error) {
        console.error('연료 배출량 계산 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 🏭 원료 배출량 계산
  const calculateMaterialEmission = useCallback(
    async (data: MaterialCalculationRequest): Promise<MaterialCalculationResponse | null> => {
      try {
        return await api.post('/calc/material/calculate', data);
      } catch (error) {
        console.error('원료 배출량 계산 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 📋 전구물질 조회
  const getPrecursorList = useCallback(
    async (userId: string): Promise<PrecursorData[] | null> => {
      try {
        const response = await api.get(`/calc/precursor/user/${userId}`);
        return response?.precursors || [];
      } catch (error) {
        console.error('전구물질 조회 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 💾 전구물질 저장
  const savePrecursorBatch = useCallback(
    async (precursors: PrecursorData[]): Promise<boolean> => {
      try {
        await api.post('/calc/precursor/save-batch', { precursors });
        return true;
      } catch (error) {
        console.error('전구물질 저장 실패:', error);
        return false;
      }
    },
    [api]
  );

  // 🎯 CBAM 종합 계산
  const calculateCBAM = useCallback(
    async (data: CBAMCalculationRequest): Promise<CBAMCalculationResponse | null> => {
      try {
        return await api.post('/calc/cbam', data);
      } catch (error) {
        console.error('CBAM 종합 계산 실패:', error);
        return null;
      }
    },
    [api]
  );

  // 📊 계산 통계 조회
  const getCalculationStats = useCallback(
    async (): Promise<any | null> => {
      try {
        return await api.get('/calc/stats');
      } catch (error) {
        console.error('계산 통계 조회 실패:', error);
        return null;
      }
    },
    [api]
  );

  return {
    calculateFuelEmission,
    calculateMaterialEmission,
    getPrecursorList,
    savePrecursorBatch,
    calculateCBAM,
    getCalculationStats,
  };
};

export type {
  FuelCalculationRequest,
  FuelCalculationResponse,
  MaterialCalculationRequest,
  MaterialCalculationResponse,
  PrecursorData,
  CBAMCalculationRequest,
  CBAMCalculationResponse,
};
