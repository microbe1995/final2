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
