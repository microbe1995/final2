'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import CommonShell from '@/components/common/CommonShell';

// ============================================================================
// 🎯 CBAM 관리 페이지
// ============================================================================

export default function CBAMPage() {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'install' | 'flow' | 'reports' | 'settings'
  >('overview');

  const renderOverview = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>CBAM 개요</h3>
        <p className='stitch-caption text-white/60'>
          탄소국경조정메커니즘(CBAM)은 EU가 수입되는 특정 상품의 탄소 배출량에
          대해 탄소 가격을 부과하는 제도입니다.
        </p>
        <div className='mt-4 grid grid-cols-1 md:grid-cols-3 gap-4'>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>적용 대상</h4>
            <p className='text-white/60 text-sm'>
              철강, 시멘트, 알루미늄, 비료, 전기, 수소 등
            </p>
          </div>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>탄소 가격</h4>
            <p className='text-white/60 text-sm'>
              EU ETS 평균 가격 기준으로 계산
            </p>
          </div>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>시행 일정</h4>
            <p className='text-white/60 text-sm'>2023년 10월부터 단계적 시행</p>
          </div>
        </div>
      </div>
    </div>
  );



  const renderFlow = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>
          CBAM 시설군 설정
        </h3>
        <p className='stitch-caption text-white/60'>
          CBAM 배출량 산정을 위한 경계를 설정하고 노드를 생성합니다.
        </p>
        <div className='mt-6'>
          <Link 
            href='/cbam/process-manager'
            className='inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
          >
            🔄 시설군 설정 페이지로 이동
          </Link>
        </div>
        <div className='mt-4 grid grid-cols-1 md:grid-cols-2 gap-4'>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>노드 생성</h4>
            <p className='text-white/60 text-sm'>
              배출량 산정을 위한 노드 및 엣지 생성
            </p>
          </div>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>경계 설정</h4>
            <p className='text-white/60 text-sm'>
              배출량 산정 경계 및 범위 설정
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderInstall = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>
          사업장 관리
        </h3>
        <p className='stitch-caption text-white/60'>
          사업장별 제품 및 프로세스 기준정보를 설정하고 관리합니다.
        </p>
        <div className='mt-6'>
          <Link 
            href='/cbam/install'
            className='inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
          >
            🏭 사업장 관리 페이지로 이동
          </Link>
        </div>
        <div className='mt-4 grid grid-cols-1 md:grid-cols-3 gap-4'>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>사업장 등록</h4>
            <p className='text-white/60 text-sm'>
              CBAM 적용 대상 사업장 정보 등록 및 관리
            </p>
          </div>
          <div className='p-4 bg-white/5 rounded-lg'>
            <h4 className='font-semibold text-white mb-2'>제품 관리</h4>
            <p className='text-white/60 text-sm'>
              사업장별 제품 정보 등록 및 관리
            </p>
          </div>
                     <div className='p-4 bg-white/5 rounded-lg'>
             <h4 className='font-semibold text-white mb-2'>산정경계설정</h4>
             <p className='text-white/60 text-sm'>
               배출량 산정 경계 및 노드 설정
             </p>
           </div>
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
            개요
          </button>
                                 <button
              onClick={() => setActiveTab('install')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'install'
                  ? 'bg-primary text-white'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              기준정보 관리
            </button>
                       <button
              onClick={() => setActiveTab('flow')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'flow'
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
         {activeTab === 'flow' && renderFlow()}
         {activeTab === 'reports' && renderReports()}
         {activeTab === 'settings' && renderSettings()}
      </div>
    </CommonShell>
  );
}
