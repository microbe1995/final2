'use client';

import React, { useState } from 'react';
import CommonShell from '@/components/CommonShell';
import ProcessManager from '@/components/cbam/ProcessManager';
import { ReactFlowProvider } from '@/hooks/ReactFlowProvider';
import { useCalculationAPI } from '@/hooks/useCalculationAPI';
import type {
  FuelCalculationRequest,
  MaterialCalculationRequest,
  CBAMCalculationRequest,
  PrecursorData,
} from '@/hooks/useCalculationAPI';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

// ============================================================================
// 🎯 CBAM 관리 페이지
// ============================================================================

export default function CBAMPage() {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'flow' | 'calculation' | 'reports' | 'settings'
  >('overview');

  // 계산 API 훅
  const {
    calculateFuelEmission,
    calculateMaterialEmission,
    calculateCBAM,
    getCalculationStats,
  } = useCalculationAPI();

  // 계산 폼 상태
  const [fuelForm, setFuelForm] = useState<FuelCalculationRequest>({
    fuel_name: '',
    activity_data: 0,
    activity_unit: 'kg',
  });

  const [materialForm, setMaterialForm] = useState<MaterialCalculationRequest>({
    material_name: '',
    activity_data: 0,
    activity_unit: 'kg',
  });

  const [cbamForm, setCbamForm] = useState<CBAMCalculationRequest>({
    product_name: '',
    fuel_emissions: 0,
    material_emissions: 0,
    precursor_emissions: 0,
  });

  const [calculationResults, setCalculationResults] = useState<{
    fuel?: any;
    material?: any;
    cbam?: any;
  }>({});

  const [isCalculating, setIsCalculating] = useState(false);

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
          CBAM 프로세스 관리
        </h3>
        <p className='stitch-caption text-white/60'>
          CBAM 관련 프로세스 플로우를 생성하고 관리합니다.
        </p>
        <div className='mt-6'>
          <ReactFlowProvider>
            <ProcessManager />
          </ReactFlowProvider>
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

  // ============================================================================
  // 🧮 계산 핸들러 함수들
  // ============================================================================

  const handleFuelCalculation = async () => {
    setIsCalculating(true);
    try {
      const result = await calculateFuelEmission(fuelForm);
      if (result) {
        setCalculationResults(prev => ({ ...prev, fuel: result }));
        setCbamForm(prev => ({ ...prev, fuel_emissions: result.total_emissions }));
      }
    } catch (error) {
      console.error('연료 계산 실패:', error);
    }
    setIsCalculating(false);
  };

  const handleMaterialCalculation = async () => {
    setIsCalculating(true);
    try {
      const result = await calculateMaterialEmission(materialForm);
      if (result) {
        setCalculationResults(prev => ({ ...prev, material: result }));
        setCbamForm(prev => ({ ...prev, material_emissions: result.total_emissions }));
      }
    } catch (error) {
      console.error('원료 계산 실패:', error);
    }
    setIsCalculating(false);
  };

  const handleCBAMCalculation = async () => {
    setIsCalculating(true);
    try {
      const result = await calculateCBAM(cbamForm);
      if (result) {
        setCalculationResults(prev => ({ ...prev, cbam: result }));
      }
    } catch (error) {
      console.error('CBAM 계산 실패:', error);
    }
    setIsCalculating(false);
  };

  // ============================================================================
  // 🧮 계산 렌더링 함수
  // ============================================================================

  const renderCalculation = () => (
    <div className='space-y-6'>
      {/* 연료 배출량 계산 */}
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>🔥 연료 배출량 계산</h3>
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              연료명 *
            </label>
            <Input
              type='text'
              value={fuelForm.fuel_name}
              onChange={(e) => setFuelForm(prev => ({ ...prev, fuel_name: e.target.value }))}
              placeholder='예: 천연가스, 석탄, 경유'
              className='w-full bg-white/10 border-white/20 text-white'
            />
          </div>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              활동 데이터 *
            </label>
            <Input
              type='number'
              value={fuelForm.activity_data}
              onChange={(e) => setFuelForm(prev => ({ ...prev, activity_data: Number(e.target.value) }))}
              placeholder='사용량'
              className='w-full bg-white/10 border-white/20 text-white'
            />
          </div>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              단위 *
            </label>
            <select
              value={fuelForm.activity_unit}
              onChange={(e) => setFuelForm(prev => ({ ...prev, activity_unit: e.target.value }))}
              className='w-full p-2 bg-white/10 border border-white/20 text-white rounded-md'
            >
              <option value='kg'>kg</option>
              <option value='ton'>ton</option>
              <option value='L'>L</option>
              <option value='m3'>m³</option>
            </select>
          </div>
        </div>
        <Button
          onClick={handleFuelCalculation}
          disabled={isCalculating || !fuelForm.fuel_name || !fuelForm.activity_data}
          className='bg-primary hover:bg-primary/90'
        >
          {isCalculating ? '계산 중...' : '연료 배출량 계산'}
        </Button>
        
        {calculationResults.fuel && (
          <div className='mt-4 p-4 bg-green-500/20 border border-green-500/30 rounded-lg'>
            <h4 className='font-semibold text-green-400 mb-2'>연료 계산 결과</h4>
            <p className='text-white'>
              <strong>{calculationResults.fuel.fuel_name}</strong>: {calculationResults.fuel.total_emissions.toFixed(2)} kg CO₂eq
            </p>
          </div>
        )}
      </div>

      {/* 원료 배출량 계산 */}
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>🏭 원료 배출량 계산</h3>
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              원료명 *
            </label>
            <Input
              type='text'
              value={materialForm.material_name}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, material_name: e.target.value }))}
              placeholder='예: 철강, 시멘트, 알루미늄'
              className='w-full bg-white/10 border-white/20 text-white'
            />
          </div>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              활동 데이터 *
            </label>
            <Input
              type='number'
              value={materialForm.activity_data}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, activity_data: Number(e.target.value) }))}
              placeholder='생산량'
              className='w-full bg-white/10 border-white/20 text-white'
            />
          </div>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              단위 *
            </label>
            <select
              value={materialForm.activity_unit}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, activity_unit: e.target.value }))}
              className='w-full p-2 bg-white/10 border border-white/20 text-white rounded-md'
            >
              <option value='kg'>kg</option>
              <option value='ton'>ton</option>
            </select>
          </div>
        </div>
        <Button
          onClick={handleMaterialCalculation}
          disabled={isCalculating || !materialForm.material_name || !materialForm.activity_data}
          className='bg-primary hover:bg-primary/90'
        >
          {isCalculating ? '계산 중...' : '원료 배출량 계산'}
        </Button>
        
        {calculationResults.material && (
          <div className='mt-4 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg'>
            <h4 className='font-semibold text-blue-400 mb-2'>원료 계산 결과</h4>
            <p className='text-white'>
              <strong>{calculationResults.material.material_name}</strong>: {calculationResults.material.total_emissions.toFixed(2)} kg CO₂eq
            </p>
          </div>
        )}
      </div>

      {/* CBAM 종합 계산 */}
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4'>🎯 CBAM 종합 계산</h3>
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              제품명 *
            </label>
            <Input
              type='text'
              value={cbamForm.product_name}
              onChange={(e) => setCbamForm(prev => ({ ...prev, product_name: e.target.value }))}
              placeholder='CBAM 대상 제품명'
              className='w-full bg-white/10 border-white/20 text-white'
            />
          </div>
          <div>
            <label className='block text-sm font-medium text-white mb-2'>
              전구물질 배출량 (kg CO₂eq)
            </label>
            <Input
              type='number'
              value={cbamForm.precursor_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, precursor_emissions: Number(e.target.value) }))}
              placeholder='전구물질 배출량'
              className='w-full bg-white/10 border-white/20 text-white'
            />
          </div>
        </div>
        
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
          <div className='p-4 bg-white/5 rounded-lg'>
            <p className='text-white/60 text-sm'>연료 배출량</p>
            <p className='text-white font-semibold'>{cbamForm.fuel_emissions.toFixed(2)} kg CO₂eq</p>
          </div>
          <div className='p-4 bg-white/5 rounded-lg'>
            <p className='text-white/60 text-sm'>원료 배출량</p>
            <p className='text-white font-semibold'>{cbamForm.material_emissions.toFixed(2)} kg CO₂eq</p>
          </div>
        </div>

        <Button
          onClick={handleCBAMCalculation}
          disabled={isCalculating || !cbamForm.product_name}
          className='bg-primary hover:bg-primary/90'
        >
          {isCalculating ? '계산 중...' : 'CBAM 비용 계산'}
        </Button>
        
        {calculationResults.cbam && (
          <div className='mt-4 p-4 bg-purple-500/20 border border-purple-500/30 rounded-lg'>
            <h4 className='font-semibold text-purple-400 mb-2'>CBAM 계산 결과</h4>
            <div className='space-y-2 text-white'>
              <p><strong>제품:</strong> {calculationResults.cbam.product_name}</p>
              <p><strong>총 배출량:</strong> {calculationResults.cbam.total_emissions.toFixed(2)} kg CO₂eq</p>
              <p><strong>CBAM 비용:</strong> €{calculationResults.cbam.cbam_cost.toFixed(2)}</p>
              <p><strong>CBAM 요율:</strong> €{calculationResults.cbam.cbam_rate.toFixed(2)}/ton CO₂eq</p>
            </div>
          </div>
        )}
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
            onClick={() => setActiveTab('flow')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'flow'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            프로세스 관리
          </button>
          <button
            onClick={() => setActiveTab('calculation')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'calculation'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            🧮 계산
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
        {activeTab === 'flow' && renderFlow()}
        {activeTab === 'calculation' && renderCalculation()}
        {activeTab === 'reports' && renderReports()}
        {activeTab === 'settings' && renderSettings()}
      </div>
    </CommonShell>
  );
}
