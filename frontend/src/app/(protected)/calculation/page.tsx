'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
// StatusBadge has different props, so we'll use simple spans
import { useCalculationAPI } from '@/hooks/useCalculationAPI';
import type {
  FuelCalculationRequest,
  MaterialCalculationRequest,
  PrecursorData,
  CBAMCalculationRequest,
  FuelCalculationResponse,
  MaterialCalculationResponse,
  CBAMCalculationResponse,
  CalculationStatsResponse
} from '@/hooks/useCalculationAPI';

// ============================================================================
// 🧮 CBAM 계산 페이지
// ============================================================================

export default function CalculationPage() {
  const [activeTab, setActiveTab] = useState<'fuel' | 'material' | 'precursor' | 'cbam' | 'stats'>('fuel');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  // API Hooks
  const {
    calculateFuelEmission,
    calculateMaterialEmission,
    getPrecursorList,
    savePrecursorBatch,
    calculateCBAM,
    getCalculationStats,
    getCalculationHistory
  } = useCalculationAPI();

  // Form States
  const [fuelForm, setFuelForm] = useState<FuelCalculationRequest>({
    fuel_name: '',
    fuel_amount: 0
  });

  const [materialForm, setMaterialForm] = useState<MaterialCalculationRequest>({
    material_name: '',
    material_amount: 0
  });

  const [precursorForm, setPrecursorForm] = useState<PrecursorData>({
    user_id: '',
    precursor_name: '',
    emission_factor: 0,
    carbon_content: 0
  });

  const [cbamForm, setCbamForm] = useState<CBAMCalculationRequest>({
    product_name: '',
    fuel_emissions: 0,
    material_emissions: 0,
    precursor_emissions: 0
  });

  // Results
  const [results, setResults] = useState<{
    fuel?: FuelCalculationResponse;
    material?: MaterialCalculationResponse;
    cbam?: CBAMCalculationResponse;
    stats?: CalculationStatsResponse;
  }>({});

  const [precursorList, setPrecursorList] = useState<PrecursorData[]>([]);

  // ============================================================================
  // 🔥 연료 계산
  // ============================================================================
  
  const handleFuelCalculation = async () => {
    if (!fuelForm.fuel_name || fuelForm.fuel_amount <= 0) {
      setToast({ message: '연료명과 연료량을 올바르게 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateFuelEmission(fuelForm);
      
      if (result) {
        setResults(prev => ({ ...prev, fuel: result }));
        setToast({ message: '연료 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '연료 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Fuel calculation error:', error);
      setToast({ message: '연료 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🧱 원료 계산
  // ============================================================================
  
  const handleMaterialCalculation = async () => {
    if (!materialForm.material_name || materialForm.material_amount <= 0) {
      setToast({ message: '원료명과 원료량을 올바르게 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateMaterialEmission(materialForm);
      
      if (result) {
        setResults(prev => ({ ...prev, material: result }));
        setToast({ message: '원료 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '원료 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Material calculation error:', error);
      setToast({ message: '원료 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🎯 CBAM 종합 계산
  // ============================================================================
  
  const handleCBAMCalculation = async () => {
    if (!cbamForm.product_name) {
      setToast({ message: '제품명을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateCBAM(cbamForm);
      
      if (result) {
        setResults(prev => ({ ...prev, cbam: result }));
        setToast({ message: 'CBAM 종합 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: 'CBAM 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('CBAM calculation error:', error);
      setToast({ message: 'CBAM 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🔬 전구물질 관리
  // ============================================================================
  
  const handlePrecursorSave = async () => {
    if (!precursorForm.user_id || !precursorForm.precursor_name) {
      setToast({ message: '사용자 ID와 전구물질명을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await savePrecursorBatch([precursorForm]);
      
      if (result) {
        setToast({ message: `전구물질이 저장되었습니다: ${result.message}`, type: 'success' });
        // 폼 초기화
        setPrecursorForm({
          user_id: precursorForm.user_id, // 사용자 ID는 유지
          precursor_name: '',
          emission_factor: 0,
          carbon_content: 0
        });
      } else {
        setToast({ message: '전구물질 저장 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Precursor save error:', error);
      setToast({ message: '전구물질 저장 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handlePrecursorLoad = async () => {
    if (!precursorForm.user_id) {
      setToast({ message: '사용자 ID를 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await getPrecursorList(precursorForm.user_id);
      
      if (result) {
        setPrecursorList(result.precursors);
        setToast({ message: `${result.total_count}개의 전구물질을 조회했습니다.`, type: 'success' });
      } else {
        setToast({ message: '전구물질 조회 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Precursor load error:', error);
      setToast({ message: '전구물질 조회 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 📊 통계 로드
  // ============================================================================
  
  const loadStats = async () => {
    try {
      const result = await getCalculationStats();
      if (result) {
        setResults(prev => ({ ...prev, stats: result }));
      }
    } catch (error) {
      console.error('Stats load error:', error);
    }
  };

  // 컴포넌트 마운트 시 통계 로드
  useEffect(() => {
    if (activeTab === 'stats') {
      loadStats();
    }
  }, [activeTab]);

  // ============================================================================
  // 🎨 렌더링 함수들
  // ============================================================================

  const renderFuelCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔥 연료 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              연료명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={fuelForm.fuel_name}
              onChange={(e) => setFuelForm(prev => ({ ...prev, fuel_name: e.target.value }))}
              placeholder="예: 천연가스"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              연료량 (톤) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={fuelForm.fuel_amount}
              onChange={(e) => setFuelForm(prev => ({ ...prev, fuel_amount: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleFuelCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          연료 배출량 계산
        </Button>

        {results.fuel && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
            <h4 className="font-semibold text-green-400 mb-3">🔥 연료 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>연료명:</strong> {results.fuel.fuel_name}</p>
              <p><strong>총 배출량:</strong> {results.fuel.emission?.toFixed(2)} tCO₂</p>
              <p><strong>배출계수:</strong> {results.fuel.emission_factor} tCO₂/TJ</p>
              <p><strong>순발열량:</strong> {results.fuel.net_calorific_value} TJ/Gg</p>
              <p><strong>계산식:</strong> {results.fuel.calculation_formula}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderMaterialCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🧱 원료 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              원료명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={materialForm.material_name}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, material_name: e.target.value }))}
              placeholder="예: 철광석"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              원료량 (톤) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={materialForm.material_amount}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, material_amount: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleMaterialCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          원료 배출량 계산
        </Button>

        {results.material && (
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <h4 className="font-semibold text-blue-400 mb-3">🧱 원료 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>원료명:</strong> {results.material.material_name}</p>
              <p><strong>총 배출량:</strong> {results.material.emission?.toFixed(2)} tCO₂</p>
              <p><strong>배출계수:</strong> {results.material.emission_factor} tCO₂/톤</p>
              <p><strong>계산식:</strong> {results.material.calculation_formula}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderPrecursorManagement = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔬 전구물질 관리</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">사용자 ID <span className="text-red-500">*</span>
            </label>
            <Input
              value={precursorForm.user_id}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, user_id: e.target.value }))}
              placeholder="사용자 ID"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">전구물질명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={precursorForm.precursor_name}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, precursor_name: e.target.value }))}
              placeholder="예: 석회석"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">배출계수            </label>
            <Input
              type="number"
              value={precursorForm.emission_factor}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, emission_factor: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">탄소함량            </label>
            <Input
              type="number"
              value={precursorForm.carbon_content}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, carbon_content: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handlePrecursorSave}
            loading={loading}
            variant="primary"
            className="flex-1 md:flex-none"
          >
            전구물질 저장
          </Button>
          
          <Button
            onClick={handlePrecursorLoad}
            loading={loading}
            variant="secondary"
            className="flex-1 md:flex-none"
          >
            전구물질 조회
          </Button>
        </div>

        {/* 전구물질 목록 */}
        {precursorList.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-white mb-3">저장된 전구물질</h4>
            <div className="space-y-2">
              {precursorList.map((precursor, index) => (
                <div key={index} className="p-3 bg-gray-800 border border-gray-700 rounded-lg">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div><strong>이름:</strong> {precursor.precursor_name}</div>
                    <div><strong>배출계수:</strong> {precursor.emission_factor}</div>
                    <div><strong>탄소함량:</strong> {precursor.carbon_content}</div>
                    <div><strong>사용자:</strong> {precursor.user_id}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderCBAMCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🎯 CBAM 종합 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">제품명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={cbamForm.product_name}
              onChange={(e) => setCbamForm(prev => ({ ...prev, product_name: e.target.value }))}
              placeholder="예: 철강 제품"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">연료 배출량 (tCO₂)            </label>
            <Input
              type="number"
              value={cbamForm.fuel_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, fuel_emissions: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">원료 배출량 (tCO₂)            </label>
            <Input
              type="number"
              value={cbamForm.material_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, material_emissions: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">전구물질 배출량 (tCO₂)            </label>
            <Input
              type="number"
              value={cbamForm.precursor_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, precursor_emissions: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleCBAMCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          CBAM 종합 계산
        </Button>

        {results.cbam && (
          <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <h4 className="font-semibold text-purple-400 mb-3">🎯 CBAM 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>제품명:</strong> {results.cbam.product_name}</p>
              <p><strong>총 배출량:</strong> {results.cbam.emission?.toFixed(2)} tCO₂eq</p>
              <p><strong>CBAM 요율:</strong> €{results.cbam.cbam_rate}/tCO₂eq</p>
              <p><strong>CBAM 비용:</strong> €{results.cbam.cbam_cost?.toFixed(2)}</p>
              {results.cbam.breakdown && (
                <div className="mt-3 pt-3 border-t border-purple-500/30">
                  <p className="font-semibold mb-1">배출량 세부사항:</p>
                  <p>• 연료 배출량: {results.cbam.breakdown.fuel_emissions.toFixed(2)} tCO₂</p>
                  <p>• 원료 배출량: {results.cbam.breakdown.material_emissions.toFixed(2)} tCO₂</p>
                  <p>• 전구물질 배출량: {results.cbam.breakdown.precursor_emissions.toFixed(2)} tCO₂</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderStats = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">📊 계산 통계</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-blue-400 mb-2">연료 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.fuel_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
          
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-green-400 mb-2">원료 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.material_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
          
          <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-purple-400 mb-2">CBAM 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.cbam_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
          
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-orange-400 mb-2">전체 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.total_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
        </div>

        {/* 최근 계산 이력 */}
        {results.stats?.recent_calculations && results.stats.recent_calculations.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-white mb-3">최근 계산 이력</h4>
            <div className="space-y-2">
              {results.stats.recent_calculations.map((calc, index) => (
                <div key={index} className="p-3 bg-gray-800 border border-gray-700 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">{calc.type}</span>
                      <span className="text-sm text-gray-300">
                        {new Date(calc.timestamp).toLocaleString('ko-KR')}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-white">
                      {calc.emission.toFixed(2)} tCO₂eq
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🧮 CBAM 배출량 계산</h1>
          <p className="text-gray-300">
            연료, 원료, 전구물질의 배출량을 계산하고 CBAM 비용을 산출합니다
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-8">
          {[
            { key: 'fuel', label: '🔥 연료 계산', badge: 'Fuel' },
            { key: 'material', label: '🧱 원료 계산', badge: 'Material' },
            { key: 'precursor', label: '🔬 전구물질', badge: 'Precursor' },
            { key: 'cbam', label: '🎯 CBAM 계산', badge: 'CBAM' },
            { key: 'stats', label: '📊 통계', badge: 'Stats' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {tab.label}
              <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">{tab.badge}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'fuel' && renderFuelCalculation()}
        {activeTab === 'material' && renderMaterialCalculation()}
        {activeTab === 'precursor' && renderPrecursorManagement()}
        {activeTab === 'cbam' && renderCBAMCalculation()}
        {activeTab === 'stats' && renderStats()}

        {/* Toast */}
        {toast && (
          <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            toast.type === 'success' ? 'bg-green-600' :
            toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
          } text-white`}>
            <div className="flex items-center justify-between">
              <span>{toast.message}</span>
              <button
                onClick={() => setToast(null)}
                className="ml-2 text-white hover:text-gray-200"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
