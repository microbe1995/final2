'use client';

import { useState } from 'react';
import { saveScope } from '@/lib/actions';
import type { ProjectMeta, AnalysisScope } from '@/lib/types';
import LcaLayout from '@/components/lca/LcaLayout';

export default function ScopePage() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState<ProjectMeta & AnalysisScope>({
    projectName: '',
    reason: '',
    owner: '',
    period: '',
    unit: '',
    productName: '',
    majorFunction: '',
    secondaryFunction: '',
    productClass: '',
    productFeatures: '',
    packaging: '',
    lifecycle: '',
    processOverview: '',
    dataQuality: '',
    exclusions: '',
    assumptions: '',
    methodSet: '',
    summary: '',
  });

  const handleInputChange = (
    field: keyof (ProjectMeta & AnalysisScope),
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const result = await saveScope('current-project', formData);
      if (result.success) {
        setMessage('스코프가 성공적으로 저장되었습니다!');
      } else {
        setMessage(`오류: ${result.message}`);
      }
    } catch (error) {
      setMessage(`오류가 발생했습니다: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LcaLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-ecotrace-text mb-8">프로젝트 스코프 정의</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* 프로젝트 메타데이터 */}
          <div className="bg-ecotrace-surface p-6 rounded-lg border border-ecotrace-border">
            <h2 className="text-xl font-semibold text-ecotrace-text mb-4">프로젝트 정보</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  프로젝트명
                </label>
                <input
                  type="text"
                  value={formData.projectName}
                  onChange={e =>
                    handleInputChange('projectName', e.target.value)
                  }
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  분석 목적
                </label>
                <input
                  type="text"
                  value={formData.reason}
                  onChange={e => handleInputChange('reason', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  프로젝트 책임자
                </label>
                <input
                  type="text"
                  value={formData.owner}
                  onChange={e => handleInputChange('owner', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  분석 기간
                </label>
                <input
                  type="text"
                  value={formData.period}
                  onChange={e => handleInputChange('period', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  placeholder="예: 2024년 1월 ~ 12월"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  기능 단위
                </label>
                <input
                  type="text"
                  value={formData.unit}
                  onChange={e => handleInputChange('unit', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  placeholder="예: 1톤, 1개"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  제품명
                </label>
                <input
                  type="text"
                  value={formData.productName}
                  onChange={e => handleInputChange('productName', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  required
                />
              </div>
            </div>
          </div>

          {/* 제품 기능 */}
          <div className="bg-ecotrace-surface p-6 rounded-lg border border-ecotrace-border">
            <h2 className="text-xl font-semibold text-ecotrace-text mb-4">제품 기능</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  주요 기능
                </label>
                <textarea
                  value={formData.majorFunction}
                  onChange={e => handleInputChange('majorFunction', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="제품의 주요 기능을 설명하세요"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  보조 기능
                </label>
                <textarea
                  value={formData.secondaryFunction}
                  onChange={e => handleInputChange('secondaryFunction', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="제품의 보조 기능을 설명하세요"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  제품 분류
                </label>
                <input
                  type="text"
                  value={formData.productClass}
                  onChange={e => handleInputChange('productClass', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  placeholder="예: 철강제품, 자동차부품"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  제품 특징
                </label>
                <textarea
                  value={formData.productFeatures}
                  onChange={e => handleInputChange('productFeatures', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="제품의 주요 특징을 설명하세요"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  포장 정보
                </label>
                <input
                  type="text"
                  value={formData.packaging}
                  onChange={e => handleInputChange('packaging', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  placeholder="포장 방식 및 재질"
                />
              </div>
            </div>
          </div>

          {/* 분석 범위 */}
          <div className="bg-ecotrace-surface p-6 rounded-lg border border-ecotrace-border">
            <h2 className="text-xl font-semibold text-ecotrace-text mb-4">분석 범위</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  생명주기 단계
                </label>
                <textarea
                  value={formData.lifecycle}
                  onChange={e => handleInputChange('lifecycle', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="포함할 생명주기 단계를 설명하세요 (예: 원료채취, 제조, 사용, 폐기)"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  공정 개요
                </label>
                <textarea
                  value={formData.processOverview}
                  onChange={e => handleInputChange('processOverview', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="주요 공정 흐름을 설명하세요"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  데이터 품질
                </label>
                <textarea
                  value={formData.dataQuality}
                  onChange={e => handleInputChange('dataQuality', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="데이터 품질 기준 및 평가 방법을 설명하세요"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  제외 항목
                </label>
                <textarea
                  value={formData.exclusions}
                  onChange={e => handleInputChange('exclusions', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="분석에서 제외하는 항목과 그 이유를 설명하세요"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  가정사항
                </label>
                <textarea
                  value={formData.assumptions}
                  onChange={e => handleInputChange('assumptions', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="분석에 사용하는 주요 가정사항을 설명하세요"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  방법론 세트
                </label>
                <input
                  type="text"
                  value={formData.methodSet}
                  onChange={e => handleInputChange('methodSet', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20"
                  placeholder="예: IPCC, ReCiPe, CML"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ecotrace-text mb-2">
                  요약
                </label>
                <textarea
                  value={formData.summary}
                  onChange={e => handleInputChange('summary', e.target.value)}
                  className="w-full p-2 border border-ecotrace-border rounded-md bg-ecotrace-background text-ecotrace-text placeholder-ecotrace-textSecondary focus:border-ecotrace-accent focus:ring-1 focus:ring-ecotrace-accent/20 h-20"
                  placeholder="스코프 정의의 주요 내용을 요약하세요"
                  required
                />
              </div>
            </div>
          </div>

          {/* 제출 버튼 */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={loading}
              className="bg-ecotrace-accent text-white px-8 py-3 rounded-lg hover:bg-ecotrace-accent/90 disabled:opacity-50 font-medium transition-colors"
            >
              {loading ? '저장 중...' : '스코프 저장'}
            </button>
          </div>
        </form>

        {/* 메시지 표시 */}
        {message && (
          <div className={`mt-6 p-4 rounded-md ${
            message.includes('성공') ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
            {message}
          </div>
        )}
      </div>
    </LcaLayout>
  );
}
