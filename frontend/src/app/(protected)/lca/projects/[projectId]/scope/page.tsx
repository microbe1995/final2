'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import { saveScope } from '@/lib/actions';
import type { ProjectMeta, AnalysisScope } from '@/lib/types';

export default function ScopePage() {
  const params = useParams();
  const projectId = params.projectId as string;
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
      const result = await saveScope(projectId, formData);
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
    <div className='min-h-screen p-8'>
      <div className='max-w-4xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8'>프로젝트 스코프 정의</h1>

        <form onSubmit={handleSubmit} className='space-y-8'>
          {/* 프로젝트 메타데이터 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>프로젝트 정보</h2>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  프로젝트명
                </label>
                <input
                  type='text'
                  value={formData.projectName}
                  onChange={e =>
                    handleInputChange('projectName', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  분석 목적
                </label>
                <input
                  type='text'
                  value={formData.reason}
                  onChange={e => handleInputChange('reason', e.target.value)}
                  className='w-full p-2 border rounded-md bg-background'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>담당자</label>
                <input
                  type='text'
                  value={formData.owner}
                  onChange={e => handleInputChange('owner', e.target.value)}
                  className='w-full p-2 border rounded-md bg-background'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  분석 기간
                </label>
                <input
                  type='text'
                  value={formData.period}
                  onChange={e => handleInputChange('period', e.target.value)}
                  className='w-full p-2 border rounded-md bg-background'
                  placeholder='예: 2024년 1월 ~ 12월'
                  required
                />
              </div>
            </div>
          </div>

          {/* 제품 정보 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>제품 정보</h2>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
              <div>
                <label className='block text-sm font-medium mb-2'>제품명</label>
                <input
                  type='text'
                  value={formData.productName}
                  onChange={e =>
                    handleInputChange('productName', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  주요 기능
                </label>
                <input
                  type='text'
                  value={formData.majorFunction}
                  onChange={e =>
                    handleInputChange('majorFunction', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  보조 기능
                </label>
                <input
                  type='text'
                  value={formData.secondaryFunction}
                  onChange={e =>
                    handleInputChange('secondaryFunction', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background'
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  제품 분류
                </label>
                <input
                  type='text'
                  value={formData.productClass}
                  onChange={e =>
                    handleInputChange('productClass', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background'
                  required
                />
              </div>
            </div>
          </div>

          {/* 분석 범위 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>분석 범위</h2>
            <div className='space-y-4'>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  생명주기 단계
                </label>
                <textarea
                  value={formData.lifecycle}
                  onChange={e => handleInputChange('lifecycle', e.target.value)}
                  className='w-full p-2 border rounded-md bg-background h-20'
                  placeholder='원료 추출, 제조, 사용, 폐기 등 포함할 생명주기 단계를 설명하세요'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  공정 개요
                </label>
                <textarea
                  value={formData.processOverview}
                  onChange={e =>
                    handleInputChange('processOverview', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background h-20'
                  placeholder='주요 공정과 단계를 설명하세요'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  데이터 품질
                </label>
                <textarea
                  value={formData.dataQuality}
                  onChange={e =>
                    handleInputChange('dataQuality', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background h-20'
                  placeholder='데이터 품질 기준과 평가 방법을 설명하세요'
                  required
                />
              </div>
            </div>
          </div>

          {/* 제외 사항 및 가정 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>제외 사항 및 가정</h2>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  제외 사항
                </label>
                <textarea
                  value={formData.exclusions}
                  onChange={e =>
                    handleInputChange('exclusions', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background h-20'
                  placeholder='분석에서 제외하는 공정이나 단계를 설명하세요'
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  가정 사항
                </label>
                <textarea
                  value={formData.assumptions}
                  onChange={e =>
                    handleInputChange('assumptions', e.target.value)
                  }
                  className='w-full p-2 border rounded-md bg-background h-20'
                  placeholder='분석에 사용하는 가정 사항을 설명하세요'
                />
              </div>
            </div>
          </div>

          {/* 방법론 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>방법론</h2>
            <div className='space-y-4'>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  방법론 세트
                </label>
                <input
                  type='text'
                  value={formData.methodSet}
                  onChange={e => handleInputChange('methodSet', e.target.value)}
                  className='w-full p-2 border rounded-md bg-background'
                  placeholder='예: IPCC, ReCiPe, CML 등'
                  required
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>요약</label>
                <textarea
                  value={formData.summary}
                  onChange={e => handleInputChange('summary', e.target.value)}
                  className='w-full p-2 border rounded-md bg-background h-20'
                  placeholder='스코프 정의의 주요 내용을 요약하세요'
                  required
                />
              </div>
            </div>
          </div>

          {/* 제출 버튼 */}
          <div className='flex justify-end'>
            <button
              type='submit'
              disabled={loading}
              className='bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50'
            >
              {loading ? '저장 중...' : '스코프 저장'}
            </button>
          </div>

          {/* 메시지 표시 */}
          {message && (
            <div
              className={`p-4 rounded-md ${
                message.includes('성공')
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
