'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';

export default function InterpretationPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const [interpretation, setInterpretation] = useState({
    keyFindings: '',
    limitations: '',
    assumptions: '',
    conclusions: '',
    recommendations: '',
    uncertainty: '',
    sensitivity: '',
    completeness: '',
    consistency: '',
    transparency: '',
  });

  const handleInputChange = (
    field: keyof typeof interpretation,
    value: string
  ) => {
    setInterpretation(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // TODO: 실제 API 호출 구현
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMessage('해석 결과가 성공적으로 저장되었습니다!');
    } catch (error) {
      setMessage(`오류가 발생했습니다: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='min-h-screen p-8'>
      <div className='max-w-4xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8'>결과 해석</h1>

        <form onSubmit={handleSubmit} className='space-y-8'>
          {/* 주요 발견사항 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>주요 발견사항</h2>
            <textarea
              value={interpretation.keyFindings}
              onChange={e => handleInputChange('keyFindings', e.target.value)}
              className='w-full p-3 border rounded-md bg-background h-32'
              placeholder='LCA 분석에서 발견된 주요 결과와 인사이트를 설명하세요'
              required
            />
          </div>

          {/* 한계점 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>분석의 한계점</h2>
            <textarea
              value={interpretation.limitations}
              onChange={e => handleInputChange('limitations', e.target.value)}
              className='w-full p-3 border rounded-md bg-background h-32'
              placeholder='분석에서 식별된 한계점과 제약사항을 설명하세요'
              required
            />
          </div>

          {/* 가정사항 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>가정사항</h2>
            <textarea
              value={interpretation.assumptions}
              onChange={e => handleInputChange('assumptions', e.target.value)}
              className='w-full p-3 border rounded-md bg-background h-32'
              placeholder='분석에 사용된 주요 가정사항들을 나열하세요'
              required
            />
          </div>

          {/* 결론 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>결론</h2>
            <textarea
              value={interpretation.conclusions}
              onChange={e => handleInputChange('conclusions', e.target.value)}
              className='w-full p-3 border rounded-md bg-background h-32'
              placeholder='분석 결과를 바탕으로 한 주요 결론을 제시하세요'
              required
            />
          </div>

          {/* 권고사항 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>권고사항</h2>
            <textarea
              value={interpretation.recommendations}
              onChange={e =>
                handleInputChange('recommendations', e.target.value)
              }
              className='w-full p-3 border rounded-md bg-background h-32'
              placeholder='개선을 위한 구체적인 권고사항을 제시하세요'
              required
            />
          </div>

          {/* 데이터 품질 평가 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>데이터 품질 평가</h2>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <div>
                <label className='block text-sm font-medium mb-2'>
                  불확실성
                </label>
                <textarea
                  value={interpretation.uncertainty}
                  onChange={e =>
                    handleInputChange('uncertainty', e.target.value)
                  }
                  className='w-full p-3 border rounded-md bg-background h-24'
                  placeholder='데이터 불확실성에 대한 평가'
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>민감도</label>
                <textarea
                  value={interpretation.sensitivity}
                  onChange={e =>
                    handleInputChange('sensitivity', e.target.value)
                  }
                  className='w-full p-3 border rounded-md bg-background h-24'
                  placeholder='민감도 분석 결과'
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>완전성</label>
                <textarea
                  value={interpretation.completeness}
                  onChange={e =>
                    handleInputChange('completeness', e.target.value)
                  }
                  className='w-full p-3 border rounded-md bg-background h-24'
                  placeholder='데이터 완전성 평가'
                />
              </div>
              <div>
                <label className='block text-sm font-medium mb-2'>일관성</label>
                <textarea
                  value={interpretation.consistency}
                  onChange={e =>
                    handleInputChange('consistency', e.target.value)
                  }
                  className='w-full p-3 border rounded-md bg-background h-24'
                  placeholder='데이터 일관성 평가'
                />
              </div>
            </div>
          </div>

          {/* 투명성 */}
          <div className='bg-card p-6 rounded-lg border'>
            <h2 className='text-xl font-semibold mb-4'>투명성</h2>
            <textarea
              value={interpretation.transparency}
              onChange={e => handleInputChange('transparency', e.target.value)}
              className='w-full p-3 border rounded-md bg-background h-32'
              placeholder='분석 과정의 투명성과 재현 가능성에 대해 설명하세요'
              required
            />
          </div>

          {/* 제출 버튼 */}
          <div className='flex justify-end'>
            <button
              type='submit'
              disabled={loading}
              className='bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50'
            >
              {loading ? '저장 중...' : '해석 결과 저장'}
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
