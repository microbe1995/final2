export interface ProjectMeta {
  id?: string;
  projectName: string;
  reason: string;
  owner: string;
  period: string;
  unit: string;
  productName: string;
  majorFunction: string;
  secondaryFunction: string;
  productClass: string;
  productFeatures: string;
  packaging: string;
}

export interface AnalysisScope {
  lifecycle: string;
  processOverview: string;
  dataQuality: string;
  exclusions: string;
  assumptions: string;
  methodSet: string;
  summary: string;
}

export interface LciItem {
  id: string;
  processName: string;
  category: string;
  unit: string;
  value: number;
  uncertainty: number;
  dataQuality: string;
  source: string;
  notes: string;
}

export interface LciaResult {
  id: string;
  category: string;
  value: number;
  unit: string;
  method: string;
  timestamp: string;
}

export interface ReportConfig {
  format: 'pdf' | 'docx' | 'html';
  includeCharts: boolean;
  includeTables: boolean;
  sections: string[];
}

// ============================================================================
// 🏗️ Material Master 관련 타입들 (새로 추가)
// ============================================================================

export interface MaterialMaster {
  id: number;
  mat_name: string;
  mat_engname: string;
  carbon_content?: number;
  mat_factor: number;
}

export interface MaterialMasterList {
  materials: MaterialMaster[];
  total_count: number;
}

export interface MaterialMasterFactor {
  mat_name: string;
  mat_factor: number | null;
  carbon_content?: number | null;
  found: boolean;
}

export interface MaterialMasterSearchRequest {
  mat_name: string;
}

// ============================================================================
// 🏗️ Fuel Master 관련 타입들 (새로 추가)
// ============================================================================

export interface FuelMaster {
  id: number;
  fuel_name: string;
  fuel_engname: string;
  fuel_factor: number;
  net_calory?: number;
}

export interface FuelMasterList {
  fuels: FuelMaster[];
  total_count: number;
}

export interface FuelMasterFactor {
  fuel_name: string;
  fuel_factor: number | null;
  net_calory?: number | null;
  found: boolean;
}

export interface FuelMasterSearchRequest {
  fuel_name: string;
}
