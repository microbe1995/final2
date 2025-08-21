import { useCallback } from 'react';

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
// 🚀 Calculation API Hook (Mock Implementation)
// ============================================================================

export const useCalculationAPI = () => {
  // Mock implementations for now
  const calculateFuelEmission = useCallback(
    async (data: FuelCalculationRequest): Promise<FuelCalculationResponse | null> => {
      try {
        // Mock calculation
        const emission = data.fuel_amount * 2.5;
        return {
          emission,
          fuel_name: data.fuel_name,
          emission_factor: 2.5,
          net_calorific_value: 43.0,
          calculation_formula: "연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3"
        };
      } catch (error) {
        console.error('Error calculating fuel emission:', error);
        return null;
      }
    },
    []
  );

  const calculateMaterialEmission = useCallback(
    async (data: MaterialCalculationRequest): Promise<MaterialCalculationResponse | null> => {
      try {
        // Mock calculation
        const emission = data.material_amount * 1.8;
        return {
          emission,
          material_name: data.material_name,
          emission_factor: 1.8,
          calculation_formula: "원료량(톤) × 배출계수(tCO2/톤)"
        };
      } catch (error) {
        console.error('Error calculating material emission:', error);
        return null;
      }
    },
    []
  );

  const getPrecursorList = useCallback(
    async (userId: string): Promise<PrecursorListResponse | null> => {
      try {
        // Mock data
        return {
          precursors: [
            {
              user_id: userId,
              precursor_name: "석회석",
              emission_factor: 0.44,
              carbon_content: 12.0
            }
          ],
          total_count: 1
        };
      } catch (error) {
        console.error('Error fetching precursor list:', error);
        return null;
      }
    },
    []
  );

  const savePrecursorBatch = useCallback(
    async (precursors: PrecursorData[]): Promise<PrecursorSaveResponse | null> => {
      try {
        // Mock save
        return {
          saved_count: precursors.length,
          message: `${precursors.length}개의 전구물질이 저장되었습니다.`
        };
      } catch (error) {
        console.error('Error saving precursor batch:', error);
        return null;
      }
    },
    []
  );

  const calculateCBAM = useCallback(
    async (data: CBAMCalculationRequest): Promise<CBAMCalculationResponse | null> => {
      try {
        const totalEmissions = data.fuel_emissions + data.material_emissions + data.precursor_emissions;
        const cbamRate = 75.0; // EUR/tCO2eq
        const cbamCost = totalEmissions * cbamRate;

        return {
          product_name: data.product_name,
          emission: totalEmissions,
          cbam_cost: cbamCost,
          cbam_rate: cbamRate,
          breakdown: {
            fuel_emissions: data.fuel_emissions,
            material_emissions: data.material_emissions,
            precursor_emissions: data.precursor_emissions
          }
        };
      } catch (error) {
        console.error('Error calculating CBAM:', error);
        return null;
      }
    },
    []
  );

  const getCalculationStats = useCallback(
    async (): Promise<CalculationStatsResponse | null> => {
      try {
        // Mock stats
        return {
          fuel_calculations: 12,
          material_calculations: 8,
          cbam_calculations: 5,
          total_calculations: 25,
          recent_calculations: [
            {
              type: "연료",
              timestamp: new Date().toISOString(),
              emission: 125.5
            },
            {
              type: "원료",
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              emission: 89.2
            }
          ]
        };
      } catch (error) {
        console.error('Error fetching calculation stats:', error);
        return null;
      }
    },
    []
  );

  const getCalculationHistory = useCallback(
    async (type?: string, limit?: number): Promise<any[] | null> => {
      try {
        // Mock history
        return [];
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
