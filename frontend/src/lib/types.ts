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


/**
 * CBAM 관련 타입 정의
 * 단일 책임: 모든 훅에서 사용하는 공통 타입 정의
 */

export interface Install {
  id: number;
  install_name: string;
  reporting_year?: string;
}

export interface Product {
  id: number;
  product_name: string;
  product_category?: string;
  product_amount?: number;
  product_sell?: number;
  product_eusell?: number;
  install_id: number;
  cncode_total?: string;
  goods_name?: string;
  aggrgoods_name?: string;
}

export interface Process {
  id: number;
  process_name: string;
  // 공정 소속 사업장 ID (백엔드 응답 포함)
  install_id?: number;
  // 선택적으로 내려오는 사업장명
  install_name?: string;
  start_period?: string;
  end_period?: string;
  products?: Product[];
}
