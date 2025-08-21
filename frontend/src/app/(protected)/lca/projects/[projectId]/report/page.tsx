'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import { requestReport, getReportStatus } from '@/lib/actions';

export default function ReportPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [reportId, setReportId] = useState('');
  const [reportFormat, setReportFormat] = useState<'pdf' | 'docx' | 'html'>(
    'pdf'
  );
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeTables, setIncludeTables] = useState(true);
  const [reportStatus, setReportStatus] = useState<'pending' | 'completed'>(
    'pending'
  );
  const [reportUrl, setReportUrl] = useState('');

  const handleGenerateReport = async () => {
    setLoading(true);
    setMessage('');

    try {
      const result = await requestReport(projectId, reportFormat);
      if (result.success && 'reportId' in result) {
        setReportId(result.reportId || '');
        setReportUrl(result.reportUrl || '');
        setReportStatus('pending');
        setMessage('보고서 생성이 시작되었습니다!');
        // 상태 폴링 시작
        setTimeout(() => checkReportStatus(), 2000);
      } else {
        setMessage(`오류: ${result.message}`);
      }
    } catch (error) {
      setMessage(`오류가 발생했습니다: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const checkReportStatus = async () => {
    if (!reportId) return;

    try {
      const result = await getReportStatus(reportId);
      if (result.success && result.data) {
        setReportStatus(result.data.status || 'pending');
        if (result.data.status === 'completed') {
          setMessage('보고서 생성이 완료되었습니다!');
        }
      }
    } catch (error) {
      console.error('상태 확인 실패:', error);
    }
  };

  return (
    <div className='min-h-screen p-8'>
      <div className='max-w-4xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8'>LCA 보고서 생성</h1>

        {/* 보고서 생성 설정 */}
        <div className='bg-card p-6 rounded-lg border mb-8'>
          <h2 className='text-xl font-semibold mb-4'>보고서 설정</h2>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            <div>
              <label className='block text-sm font-medium mb-2'>
                보고서 형식
              </label>
              <select
                value={reportFormat}
                onChange={e =>
                  setReportFormat(e.target.value as 'pdf' | 'docx' | 'html')
                }
                className='w-full p-2 border rounded-md bg-background'
                required
              >
                <option value='pdf'>PDF</option>
                <option value='docx'>Word (DOCX)</option>
                <option value='html'>HTML</option>
              </select>
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>
                포함 내용
              </label>
              <div className='space-y-2'>
                <label className='flex items-center space-x-2'>
                  <input
                    type='checkbox'
                    checked={includeCharts}
                    onChange={e => setIncludeCharts(e.target.checked)}
                    className='rounded border-gray-300'
                  />
                  <span className='text-sm'>차트 및 그래프</span>
                </label>
                <label className='flex items-center space-x-2'>
                  <input
                    type='checkbox'
                    checked={includeTables}
                    onChange={e => setIncludeTables(e.target.checked)}
                    className='rounded border-gray-300'
                  />
                  <span className='text-sm'>상세 테이블</span>
                </label>
              </div>
            </div>
          </div>

          <div className='mt-6'>
            <button
              onClick={handleGenerateReport}
              disabled={loading}
              className='bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50'
            >
              {loading ? '생성 중...' : '보고서 생성'}
            </button>
          </div>
        </div>

        {/* 생성된 보고서 */}
        {reportId && (
          <div className='bg-card p-6 rounded-lg border mb-8'>
            <h2 className='text-xl font-semibold mb-4'>생성된 보고서</h2>
            <div className='mb-4'>
              <strong>보고서 ID:</strong> {reportId}
            </div>
            <div className='mb-4'>
              <strong>형식:</strong> {reportFormat.toUpperCase()}
            </div>
            <div className='mb-4'>
              <strong>상태:</strong>
              <span
                className={`ml-2 px-2 py-1 rounded-full text-xs ${
                  reportStatus === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {reportStatus === 'completed' ? '완료' : '생성 중'}
              </span>
            </div>

            {reportStatus === 'completed' && (
              <div className='mt-4'>
                <a
                  href={reportUrl}
                  target='_blank'
                  rel='noopener noreferrer'
                  className='bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700'
                >
                  보고서 다운로드
                </a>
              </div>
            )}

            <div className='mt-4'>
              <button
                onClick={checkReportStatus}
                className='bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/90'
              >
                상태 확인
              </button>
            </div>
          </div>
        )}

        {/* 보고서 템플릿 */}
        <div className='bg-card p-6 rounded-lg border mb-8'>
          <h2 className='text-xl font-semibold mb-4'>보고서 템플릿</h2>
          <div className='space-y-4'>
            <div className='border-l-4 border-primary pl-4'>
              <h3 className='font-semibold'>1. 실행 요약</h3>
              <p className='text-sm text-muted-foreground'>
                프로젝트 개요, 목적, 범위, 주요 결과 요약
              </p>
            </div>
            <div className='border-l-4 border-primary pl-4'>
              <h3 className='font-semibold'>2. 목적 및 범위</h3>
              <p className='text-sm text-muted-foreground'>
                분석 목적, 제품 시스템 경계, 기능 단위, 영향 카테고리
              </p>
            </div>
            <div className='border-l-4 border-primary pl-4'>
              <h3 className='font-semibold'>3. 생명주기 인벤토리</h3>
              <p className='text-sm text-muted-foreground'>
                데이터 수집 방법, 공정 흐름도, 데이터 품질 평가
              </p>
            </div>
            <div className='border-l-4 border-primary pl-4'>
              <h3 className='font-semibold'>4. 생명주기 영향평가</h3>
              <p className='text-sm text-muted-foreground'>
                방법론 선택, 영향 카테고리별 결과, 정규화 및 가중치
              </p>
            </div>
            <div className='border-l-4 border-primary pl-4'>
              <h3 className='font-semibold'>5. 해석</h3>
              <p className='text-sm text-muted-foreground'>
                주요 발견사항, 한계점, 결론, 권고사항
              </p>
            </div>
            <div className='border-l-4 border-primary pl-4'>
              <h3 className='font-semibold'>6. 부록</h3>
              <p className='text-sm text-muted-foreground'>
                상세 데이터, 계산 방법, 참고문헌
              </p>
            </div>
          </div>
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
      </div>
    </div>
  );
}
