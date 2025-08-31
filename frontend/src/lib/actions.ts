'use server';

import type { ProjectMeta, AnalysisScope, LciItem } from '@/lib/types';

// Base API configuration for microservice integration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

// 🔴 추가: 환경변수 검증
if (!API_BASE_URL) {
  console.warn('[ACTIONS] NEXT_PUBLIC_API_BASE_URL 환경변수가 설정되지 않았습니다.');
}

interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// Generic API call wrapper for microservice communication
async function apiCall<T = any>(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'POST',
  data?: any
): Promise<ApiResponse<T>> {
  try {
    // 🔴 수정: 실제 API 호출 구현
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const responseData = await response.json();
    
    return {
      success: true,
      message: 'API call successful',
      data: responseData as T,
    };
  } catch (error) {
    console.error(`[API ERROR] ${endpoint}:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown API error',
    };
  }
}

// Project Management Service Actions
export async function createProject(projectData: Partial<ProjectMeta>) {
  return await apiCall('/api/v1/cbam/projects', 'POST', projectData);
}

export async function getProject(projectId: string) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}`, 'GET');
}

export async function updateProject(
  projectId: string,
  projectData: Partial<ProjectMeta>
) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}`, 'PUT', projectData);
}

// Scope Service Actions
export async function saveScope(
  projectId: string,
  formData: ProjectMeta & AnalysisScope
) {

  // Split data for different microservices
  const projectMeta = {
    projectName: formData.projectName,
    reason: formData.reason,
    owner: formData.owner,
    period: formData.period,
    unit: formData.unit,
    productName: formData.productName,
    majorFunction: formData.majorFunction,
    secondaryFunction: formData.secondaryFunction,
    productClass: formData.productClass,
    productFeatures: formData.productFeatures,
    packaging: formData.packaging,
  };

  const analysisScope = {
    lifecycle: formData.lifecycle,
    processOverview: formData.processOverview,
    dataQuality: formData.dataQuality,
    exclusions: formData.exclusions,
    assumptions: formData.assumptions,
    methodSet: formData.methodSet,
    summary: formData.summary,
  };

  // Call multiple microservices
  const [projectResult, scopeResult] = await Promise.all([
    apiCall(`/api/v1/cbam/projects/${projectId}/meta`, 'PUT', projectMeta),
    apiCall(`/api/v1/cbam/projects/${projectId}/scope`, 'PUT', analysisScope),
  ]);

  if (!projectResult.success || !scopeResult.success) {
    return {
      success: false,
      message: 'Failed to save some data',
      error: `Project: ${projectResult.message}, Scope: ${scopeResult.message}`,
    };
  }

  return {
    success: true,
    message: 'Scope and project metadata saved successfully',
  };
}

// LCI Service Actions
export async function saveLci(projectId: string, items: LciItem[]) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}/lci`, 'PUT', { items });
}

export async function getLciData(projectId: string) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}`, 'GET');
}

export async function validateLciData(projectId: string) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}/lci/validate`, 'POST');
}

// LCIA Service Actions
export async function startLciaRun(
  projectId: string,
  config: { method: string; categories: string[] }
) {

  const result = await apiCall(`/api/v1/cbam/projects/${projectId}/lcia/run`, 'POST', {
    methodSet: config.method,
    categories: config.categories,
    timestamp: new Date().toISOString(),
  });

  if (result.success) {
    return {
      success: true,
      data: { runId: result.data?.runId || `run-${Date.now()}` },
      message: 'LCIA calculation started',
    };
  }

  return result;
}

export async function getLciaResults(projectId: string, runId?: string) {
  const endpoint = runId
    ? `/api/v1/cbam/projects/${projectId}/lcia/results/${runId}`
    : `/api/v1/cbam/projects/${projectId}/lcia/results/latest`;
  return await apiCall(endpoint, 'GET');
}

export async function getLciaHistory(projectId: string) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}/lcia/history`, 'GET');
}

// Report Service Actions
export async function requestReport(
  projectId: string,
  format: 'pdf' | 'docx' | 'html' = 'pdf'
): Promise<
  | {
      success: true;
      reportUrl: string;
      reportId: string;
      message: string;
    }
  | ApiResponse<any>
> {

  const result = await apiCall(
    `/api/v1/cbam/projects/${projectId}/report/generate`,
    'POST',
    {
      format,
      timestamp: new Date().toISOString(),
      includeCharts: true,
      includeTables: true,
    }
  );

  if (result.success) {
    return {
      success: true,
      reportUrl: result.data?.reportUrl || `/reports/${projectId}.${format}`,
      reportId: result.data?.reportId || `report-${Date.now()}`,
      message: 'Report generated successfully',
    };
  }

  return result;
}

export async function getReportStatus(reportId: string) {
  return await apiCall(`/api/v1/cbam/reports/${reportId}/status`, 'GET');
}

// File Upload Service Actions
export async function uploadProcessDiagram(projectId: string, file: File) {

  // TODO: Implement actual file upload to file service
  const formData = new FormData();
  formData.append('file', file);
  formData.append('projectId', projectId);
  formData.append('type', 'process-diagram');

  return await apiCall(`/api/v1/cbam/files/upload/process-diagram`, 'POST', {
    fileName: file.name,
    fileSize: file.size,
    mimeType: file.type,
    projectId,
  });
}

// Data Quality Service Actions
export async function validateDataQuality(projectId: string) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}/quality/validate`, 'POST');
}

export async function getDataQualityReport(projectId: string) {
  return await apiCall(`/api/v1/cbam/projects/${projectId}/quality/report`, 'GET');
}
