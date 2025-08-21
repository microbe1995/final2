'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import { startLciaRun, getLciaResults, getLciaHistory } from '@/lib/actions';

export default function LciaPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [runId, setRunId] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  const [config, setConfig] = useState({
    method: '',
    categories: [] as string[],
  });

  const impactCategories = [
    '기후변화 (GWP)',
    '오존층 파괴 (ODP)',
    '산성화 (AP)',
    '부영양화 (EP)',
    '광화학적 오존 생성 (POCP)',
    '인간독성 (HTP)',
    '생태독성 (ETP)',
    '토지사용 (LUP)',
    '자원고갈 (ADP)',
  ];

  const handleCategoryToggle = (category: string) => {
    setConfig(prev => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category],
    }));
  };

  const handleStartRun = async () => {
    if (!config.method || config.categories.length === 0) {
      setMessage('방법론과 영향 카테고리를 선택해주세요.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const result = await startLciaRun(projectId, config);
      if (result.success) {
        setRunId(result.data?.runId || `run-${Date.now()}`);
        setMessage('LCIA 계산이 시작되었습니다!');
        // 결과 폴링 시작
        setTimeout(() => fetchResults(), 2000);
      } else {
        setMessage(`오류: ${result.message}`);
      }
    } catch (error) {
      setMessage(`오류가 발생했습니다: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const result = await getLciaResults(projectId, runId);
      if (result.success && result.data) {
        setResults(result.data.results || []);
      }
    } catch (error) {
      console.error('결과 조회 실패:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const result = await getLciaHistory(projectId);
      if (result.success && result.data) {
        setHistory(result.data.runs || []);
      }
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
    }
  };

  return (
    <div className='min-h-screen p-8'>
      <div className='max-w-6xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8'>생명주기 영향평가 (LCIA)</h1>

        {/* LCIA 실행 설정 */}
        <div className='bg-card p-6 rounded-lg border mb-8'>
          <h2 className='text-xl font-semibold mb-4'>LCIA 실행 설정</h2>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            <div>
              <label className='block text-sm font-medium mb-2'>
                방법론 선택
              </label>
              <select
                value={config.method}
                onChange={e => setConfig({ ...config, method: e.target.value })}
                className='w-full p-2 border rounded-md bg-background'
                required
              >
                <option value=''>방법론 선택</option>
                <option value='ipcc'>IPCC (기후변화)</option>
                <option value='recipe'>ReCiPe</option>
                <option value='cml'>CML</option>
                <option value='trad'>TRACI</option>
                <option value='ilcd'>ILCD</option>
              </select>
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>
                선택된 카테고리
              </label>
              <div className='text-sm text-muted-foreground'>
                {config.categories.length}개 선택됨
              </div>
            </div>
          </div>

          <div className='mt-6'>
            <label className='block text-sm font-medium mb-4'>
              영향 카테고리 선택
            </label>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3'>
              {impactCategories.map(category => (
                <label key={category} className='flex items-center space-x-2'>
                  <input
                    type='checkbox'
                    checked={config.categories.includes(category)}
                    onChange={() => handleCategoryToggle(category)}
                    className='rounded border-gray-300'
                  />
                  <span className='text-sm'>{category}</span>
                </label>
              ))}
            </div>
          </div>

          <div className='mt-6'>
            <button
              onClick={handleStartRun}
              disabled={
                loading || !config.method || config.categories.length === 0
              }
              className='bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50'
            >
              {loading ? '실행 중...' : 'LCIA 실행 시작'}
            </button>
          </div>
        </div>

        {/* 실행 결과 */}
        {runId && (
          <div className='bg-card p-6 rounded-lg border mb-8'>
            <h2 className='text-xl font-semibold mb-4'>실행 결과</h2>
            <div className='mb-4'>
              <strong>실행 ID:</strong> {runId}
            </div>
            {results.length > 0 ? (
              <div className='overflow-x-auto'>
                <table className='w-full'>
                  <thead>
                    <tr className='border-b'>
                      <th className='text-left p-2'>영향 카테고리</th>
                      <th className='text-left p-2'>수치</th>
                      <th className='text-left p-2'>단위</th>
                      <th className='text-left p-2'>방법론</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result, index) => (
                      <tr key={index} className='border-b'>
                        <td className='p-2'>{result.category}</td>
                        <td className='p-2'>{result.value}</td>
                        <td className='p-2'>{result.unit}</td>
                        <td className='p-2'>{result.method}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className='text-muted-foreground'>결과를 불러오는 중...</p>
            )}
            <div className='mt-4'>
              <button
                onClick={fetchResults}
                className='bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/90'
              >
                결과 새로고침
              </button>
            </div>
          </div>
        )}

        {/* 실행 히스토리 */}
        <div className='bg-card p-6 rounded-lg border mb-8'>
          <div className='flex justify-between items-center mb-4'>
            <h2 className='text-xl font-semibold'>실행 히스토리</h2>
            <button
              onClick={fetchHistory}
              className='bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/90'
            >
              히스토리 조회
            </button>
          </div>
          {history.length > 0 ? (
            <div className='overflow-x-auto'>
              <table className='w-full'>
                <thead>
                  <tr className='border-b'>
                    <th className='text-left p-2'>실행 ID</th>
                    <th className='text-left p-2'>방법론</th>
                    <th className='text-left p-2'>카테고리 수</th>
                    <th className='text-left p-2'>실행 시간</th>
                    <th className='text-left p-2'>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map(run => (
                    <tr key={run.id} className='border-b'>
                      <td className='p-2'>{run.id}</td>
                      <td className='p-2'>{run.method}</td>
                      <td className='p-2'>{run.categories?.length || 0}</td>
                      <td className='p-2'>
                        {new Date(run.timestamp).toLocaleString('ko-KR')}
                      </td>
                      <td className='p-2'>
                        <span
                          className={`px-2 py-1 rounded-full text-xs ${
                            run.status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {run.status === 'completed' ? '완료' : '진행 중'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className='text-muted-foreground'>실행 히스토리가 없습니다.</p>
          )}
        </div>

        {/* 메시지 표시 */}
        {message && (
          <div
            className={`p-4 rounded-md ${
              message.includes('시작')
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
