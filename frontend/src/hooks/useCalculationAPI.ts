import { useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

// ============================================================================
// 🧮 Calculation API Types
// ============================================================================

// Request Types
export interface FuelCalculationRequest {
  fuel_name: string;
  fuel_amount: number;
}

export interface MaterialCalculationRequest {
  material_name: string;
  material_amount: number;
}

export interface PrecursorData {
  user_id: string;
  precursor_name: string;
  emission_factor: number;
  carbon_content: number;
}

export interface CBAMCalculationRequest {
  product_name: string;
  fuel_emissions: number;
  material_emissions: number;
  precursor_emissions: number;
}

// Response Types
export interface FuelCalculationResponse {
  emission: number;
  fuel_name: string;
  emission_factor: number;
  net_calorific_value: number;
  calculation_formula: string;
}

export interface MaterialCalculationResponse {
  emission: number;
  material_name: string;
  emission_factor: number;
  calculation_formula: string;
}

export interface PrecursorListResponse {
  precursors: PrecursorData[];
  total_count: number;
}

export interface PrecursorSaveResponse {
  saved_count: number;
  message: string;
}

export interface CBAMCalculationResponse {
  product_name: string;
  emission: number;
  cbam_cost: number;
  cbam_rate: number;
  breakdown: {
    fuel_emissions: number;
    material_emissions: number;
    precursor_emissions: number;
  };
}

export interface CalculationStatsResponse {
  fuel_calculations: number;
  material_calculations: number;
  cbam_calculations: number;
  total_calculations: number;
  recent_calculations: Array<{
    type: string;
    timestamp: string;
    emission: number;
  }>;
}

// ============================================================================
// 🚀 Calculation API Hook (실제 API 호출)
// ============================================================================

export const useCalculationAPI = () => {
  // 🔥 연료 배출량 계산 (실제 API 호출)
  const calculateFuelEmission = useCallback(
    async (data: FuelCalculationRequest): Promise<FuelCalculationResponse | null> => {
      try {
        const response = await axiosClient.post(apiEndpoints.calculation.fuel, data);
        return response.data;
      } catch (error) {
        console.error('Error calculating fuel emission:', error);
        return null;
      }
    },
    []
  );

  // 🧱 원료 배출량 계산 (실제 API 호출)
  const calculateMaterialEmission = useCallback(
    async (data: MaterialCalculationRequest): Promise<MaterialCalculationResponse | null> => {
      try {
        const response = await axiosClient.post(apiEndpoints.calculation.material, data);
        return response.data;
      } catch (error) {
        console.error('Error calculating material emission:', error);
        return null;
      }
    },
    []
  );

  // 🔬 전구물질 목록 조회 (실제 API 호출)
  const getPrecursorList = useCallback(
    async (userId: string): Promise<PrecursorListResponse | null> => {
      try {
        const response = await axiosClient.get(`${apiEndpoints.calculation.precursors}/${userId}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching precursor list:', error);
        return null;
      }
    },
    []
  );

  // 🔬 전구물질 배치 저장 (실제 API 호출)
  const savePrecursorBatch = useCallback(
    async (precursors: PrecursorData[]): Promise<PrecursorSaveResponse | null> => {
      try {
        const response = await axiosClient.post(apiEndpoints.calculation.precursorsBatch, {
          precursors
        });
        return response.data;
      } catch (error) {
        console.error('Error saving precursor batch:', error);
        return null;
      }
    },
    []
  );

  // 🎯 CBAM 종합 계산 (실제 API 호출)
  const calculateCBAM = useCallback(
    async (data: CBAMCalculationRequest): Promise<CBAMCalculationResponse | null> => {
      try {
        const response = await axiosClient.post(apiEndpoints.calculation.cbam, data);
        return response.data;
      } catch (error) {
        console.error('Error calculating CBAM:', error);
        return null;
      }
    },
    []
  );

  // 📊 계산 통계 조회 (실제 API 호출)
  const getCalculationStats = useCallback(
    async (): Promise<CalculationStatsResponse | null> => {
      try {
        const response = await axiosClient.get(apiEndpoints.calculation.stats);
        return response.data;
      } catch (error) {
        console.error('Error fetching calculation stats:', error);
        return null;
      }
    },
    []
  );

  // 📈 계산 이력 조회 (실제 API 호출)
  const getCalculationHistory = useCallback(
    async (type?: string, limit?: number): Promise<any[] | null> => {
      try {
        const params: any = {};
        if (type) params.type = type;
        if (limit) params.limit = limit;
        
        const response = await axiosClient.get(apiEndpoints.calculation.history, { params });
        return response.data;
      } catch (error) {
        console.error('Error fetching calculation history:', error);
        return null;
      }
    },
    []
  );

  return {
    calculateFuelEmission,
    calculateMaterialEmission,
    getPrecursorList,
    savePrecursorBatch,
    calculateCBAM,
    getCalculationStats,
    getCalculationHistory,
  };
};
