'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import CommonShell from '@/components/common/CommonShell';
import axiosClient from '@/lib/axiosClient';
import { RefreshCw, ArrowRight } from 'lucide-react';
import { DummyData } from '@/hooks/useDummyData';

// ============================================================================
// 🎯 CBAM 관리 페이지
// ============================================================================

export default function CBAMPage() {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'install' | 'boundary' | 'reports' | 'settings'
  >('overview');

  // 더미 데이터 상태 관리
  const [dummyData, setDummyData] = useState<DummyData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 🔴 추가: 데이터 타입 변환 함수
  const normalizeDummyData = (rawData: any[]): DummyData[] => {
    return rawData.map(item => ({
      ...item,
      // 숫자 필드들을 안전하게 int로 변환
      생산수량: Math.round(Number(item.생산수량 || 0)),
      수량: Math.round(Number(item.수량 || 0)),
      // 날짜 필드들을 안전하게 처리
      투입일: item.투입일 || null,
      종료일: item.종료일 || null,
      // 문자열 필드들을 안전하게 처리
      로트번호: String(item.로트번호 || ''),
      생산품명: String(item.생산품명 || ''),
      공정: String(item.공정 || ''),
      투입물명: item.투입물명 || null,
      단위: String(item.단위 || ''),
      created_at: String(item.created_at || ''),
      updated_at: String(item.updated_at || '')
    }));
  };

  // 더미 데이터 조회 함수
  const fetchDummyData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // cbam 서비스를 통해 더미 데이터 조회
      const response = await axiosClient.get('/api/v1/cbam/dummy');
      let data: DummyData[] = [];
      
      if (response.data && Array.isArray(response.data)) {
        data = response.data;
      } else if (response.data && response.data.items && Array.isArray(response.data.items)) {
        data = response.data.items;
      } else {
        data = [];
      }
      
      // 🔴 추가: 데이터 타입 정규화
      console.log('🔍 원본 데이터 샘플:', data.slice(0, 2));
      const normalizedData = normalizeDummyData(data);
      console.log('🔍 정규화된 데이터 샘플:', normalizedData.slice(0, 2));
      setDummyData(normalizedData);
      console.log('✅ 더미 데이터 조회 성공:', normalizedData.length, '개');
      console.log('🔍 데이터 타입 정규화 완료');
    } catch (err: any) {
      console.error('❌ 더미 데이터 조회 실패:', err);
      setError(err.response?.data?.detail || err.message || '데이터를 불러오는데 실패했습니다.');
      setDummyData([]);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    fetchDummyData();
  }, []);

  const renderOverview = () => {

    return (
      <div className='space-y-6'>
        <div className='stitch-card p-6'>
          <div className='flex items-center justify-between mb-4'>
            <div>
              <h3 className='stitch-h1 text-lg font-semibold mb-2'>투입물 데이터</h3>
              <p className='stitch-caption text-white/60'>
                생산에 투입되는 원자재 및 자재 정보를 관리합니다.
              </p>
            </div>
            <div className='flex gap-3'>
              <button
                onClick={fetchDummyData}
                disabled={loading}
                className='inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50'
              >
                <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                새로고침
              </button>
              <button className='inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors'>
                <ArrowRight size={16} />
                수정하러 가기
              </button>
            </div>
          </div>

          {/* 데이터 테이블 */}
          <div className='mt-6 overflow-x-auto'>
            {loading ? (
              <div className='text-center py-8'>
                <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto'></div>
                <p className='text-white/60 mt-2'>데이터를 불러오는 중...</p>
              </div>
            ) : error ? (
              <div className='text-center py-8'>
                <p className='text-red-400'>{error}</p>
                <button
                  onClick={fetchDummyData}
                  className='mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors'
                >
                  다시 시도
                </button>
              </div>
            ) : (
              <table className='w-full text-sm'>
                <thead>
                  <tr className='border-b border-white/20'>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>로트번호</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>제품명</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>생산수량</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>입력일</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>종료일</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>공정명</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>투입물</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>수량</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>단위</th>
                    <th className='text-left py-3 px-4 font-medium text-white/80'>AI추천</th>
                  </tr>
                </thead>
                <tbody>
                  {dummyData.length === 0 ? (
                    <tr>
                      <td colSpan={10} className='text-center py-8 text-white/40'>
                        데이터가 없습니다.
                      </td>
                    </tr>
                  ) : (
                    dummyData.map((item) => (
                      <tr key={item.id} className='border-b border-white/10 hover:bg-white/5 transition-colors'>
                        <td className='py-3 px-4 text-white/90'>{item.로트번호}</td>
                        <td className='py-3 px-4 text-white/90'>{item.생산품명}</td>
                        <td className='py-3 px-4 text-white/90'>{item.생산수량}</td>
                        <td className='py-3 px-4 text-white/90'>{item.투입일 || '-'}</td>
                        <td className='py-3 px-4 text-white/90'>{item.종료일 || '-'}</td>
                        <td className='py-3 px-4 text-white/90'>{item.공정}</td>
                        <td className='py-3 px-4 text-white/90'>{item.투입물명 || '-'}</td>
                        <td className='py-3 px-4 text-white/90'>{item.수량}</td>
                        <td className='py-3 px-4 text-white/90'>{item.단위}</td>
                        <td className='py-3 px-4 text-white/90'>
                          <span className='px-2 py-1 bg-blue-600/20 text-blue-400 rounded-full text-xs'>
                            추천
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderInstall = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>
          CBAM 사업장 관리
        </h3>
        <p className='stitch-caption text-white/60'>
          CBAM 적용 대상 사업장 정보를 생성하고 관리합니다.
        </p>
        <div className='mt-6'>
          <Link 
            href='/cbam/install'
            className='inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
          >
            🏭 사업장 관리 페이지로 이동
          </Link>
        </div>
      </div>
    </div>
  );

  const renderBoundary = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>
          CBAM 산정경계설정
        </h3>
        <p className='stitch-caption text-white/60'>
          CBAM 배출량 산정을 위한 경계를 설정하고 노드를 생성합니다.
        </p>
        <div className='mt-6'>
          <Link 
            href='/cbam/process-manager'
            className='inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
          >
            🔄 산정경계 설정 페이지로 이동
          </Link>
        </div>
      </div>
    </div>
  );

  const renderReports = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>CBAM 보고서</h3>
        <p className='stitch-caption text-white/60'>
          탄소국경조정메커니즘 관련 보고서를 생성하고 관리합니다.
        </p>
        <div className='mt-4 p-4 bg-white/5 rounded-lg'>
          <p className='text-white/40 text-sm'>
            보고서 기능은 개발 중입니다...
          </p>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>CBAM 설정</h3>
        <p className='stitch-caption text-white/60'>
          CBAM 관련 설정을 구성합니다.
        </p>
        <div className='mt-4 p-4 bg-white/5 rounded-lg'>
          <p className='text-white/40 text-sm'>설정 기능은 개발 중입니다...</p>
        </div>
      </div>
    </div>
  );

  return (
    <CommonShell>
      <div className='space-y-6'>
        {/* 페이지 헤더 */}
        <div className='flex flex-col gap-3'>
          <h1 className='stitch-h1 text-3xl font-bold'>CBAM 관리</h1>
          <p className='stitch-caption'>
            탄소국경조정메커니즘(CBAM) 프로세스 및 계산 관리
          </p>
        </div>

        {/* 탭 네비게이션 */}
        <div className='flex space-x-1 p-1 bg-white/5 rounded-lg'>
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'overview'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            투입물
          </button>
          <button
            onClick={() => setActiveTab('install')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'install'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            사업장관리
          </button>
          <button
            onClick={() => setActiveTab('boundary')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'boundary'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            산정경계설정
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'reports'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            보고서
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'settings'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            설정
          </button>
        </div>

        {/* 탭 콘텐츠 */}
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'install' && renderInstall()}
        {activeTab === 'boundary' && renderBoundary()}
        {activeTab === 'reports' && renderReports()}
        {activeTab === 'settings' && renderSettings()}
      </div>
    </CommonShell>
  );
}
