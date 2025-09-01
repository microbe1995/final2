'use client';

import React, { useState, useCallback, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useFuelMasterAPI } from '@/hooks/useFuelMasterAPI';
import { FuelMaster, FuelMasterFactor } from '@/lib/types';

interface FuelDirManagerProps {
  selectedProcess: any;
  onClose: () => void;
}

interface FuelDirForm {
  fuel_name: string;
  fuel_factor: number;
  fuel_amount: number;
  fuel_oxyfactor: number;
}

interface FuelDirResult {
  id: number | string;
  fuel_name: string;
  fuel_factor: number;
  fuel_amount: number;
  fuel_oxyfactor: number;
  fueldir_em: number;
  calculation_formula: string;
  type?: 'fueldir' | 'matdir';
  created_at?: string;
  updated_at?: string;
}

export default function FuelDirManager({ selectedProcess, onClose }: FuelDirManagerProps) {
  // Fuel Master API Hook
  const { searchFuels, getFuelFactor, createFuelDirWithAutoFactor, loading, error } = useFuelMasterAPI();

  // 연료직접배출량 모달 상태
  const [fuelDirForm, setFuelDirForm] = useState<FuelDirForm>({
    fuel_name: '',
    fuel_factor: 0,
    fuel_amount: 0,
    fuel_oxyfactor: 1.0000
  });
  const [fuelDirResults, setFuelDirResults] = useState<FuelDirResult[]>([]);
  const [isCalculatingFuelDir, setIsCalculatingFuelDir] = useState(false);

  // Fuel Master 자동 배출계수 관련 상태
  const [fuelSuggestions, setFuelSuggestions] = useState<FuelMaster[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [autoFactorStatus, setAutoFactorStatus] = useState<string>('');

  // 데이터 로딩 상태
  const [isLoadingData, setIsLoadingData] = useState(false);

  // 연료명 변경 시 실시간 검색
  const handleFuelNameChange = useCallback(async (fuelName: string) => {
    setFuelDirForm(prev => ({ ...prev, fuel_name: fuelName }));
    
    if (fuelName.trim().length >= 1) {
      const suggestions = await searchFuels(fuelName);
      if (suggestions) {
        setFuelSuggestions(suggestions);
        setShowSuggestions(true);
      }
    } else {
      setFuelSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchFuels]);

  // 연료 선택 시 배출계수만 자동 매핑
  const handleFuelSelect = useCallback((fuel: FuelMaster) => {
    // 연료명은 자동으로 설정하지 않음 (사용자가 자유롭게 입력할 수 있도록)
    setFuelSuggestions([]);
    setShowSuggestions(false);
    
    // 배출계수만 자동 매핑
    setFuelDirForm(prev => ({ ...prev, fuel_factor: fuel.fuel_factor || 0 }));
    setAutoFactorStatus(`✅ 자동 설정: ${fuel.fuel_name} (배출계수: ${fuel.fuel_factor || 0})`);
  }, []);

  // 연료명 입력 완료 시 배출계수 자동 조회
  const handleFuelNameBlur = useCallback(async () => {
    if (fuelDirForm.fuel_name && fuelDirForm.fuel_factor === 0) {
      setAutoFactorStatus('🔍 배출계수 조회 중...');
      try {
        const factorResponse = await getFuelFactor(fuelDirForm.fuel_name);
        
        if (factorResponse && factorResponse.found && factorResponse.fuel_factor !== null) {
          const factor = factorResponse.fuel_factor;
          setFuelDirForm(prev => ({ ...prev, fuel_factor: factor }));
          setAutoFactorStatus(`✅ 자동 조회: ${fuelDirForm.fuel_name} (배출계수: ${factor})`);
        } else {
          setAutoFactorStatus(`⚠️ 배출계수를 찾을 수 없음: ${fuelDirForm.fuel_name}`);
        }
      } catch (err) {
        console.error('배출계수 조회 실패:', err);
        setAutoFactorStatus(`❌ 배출계수 조회 실패: ${fuelDirForm.fuel_name}`);
      }
    }
  }, [fuelDirForm.fuel_name, fuelDirForm.fuel_factor, getFuelFactor]);

  // 연료직접배출량 계산
  const calculateFuelDirEmission = useCallback(async () => {
    if (!fuelDirForm.fuel_name || fuelDirForm.fuel_factor <= 0 || fuelDirForm.fuel_amount <= 0) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setIsCalculatingFuelDir(true);
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.fueldir.calculate, {
        fuel_amount: fuelDirForm.fuel_amount,
        fuel_factor: fuelDirForm.fuel_factor,
        fuel_oxyfactor: fuelDirForm.fuel_oxyfactor
      });

      const calculationResult = response.data;
      console.log('✅ 연료직접배출량 계산 성공:', calculationResult);

      // 결과를 목록에 추가
      const newResult: FuelDirResult = {
        id: Date.now(),
        fuel_name: fuelDirForm.fuel_name,
        fuel_factor: fuelDirForm.fuel_factor,
        fuel_amount: fuelDirForm.fuel_amount,
        fuel_oxyfactor: fuelDirForm.fuel_oxyfactor,
        fueldir_em: calculationResult.fueldir_em,
        calculation_formula: calculationResult.calculation_formula,
        type: 'fueldir',
        created_at: new Date().toISOString()
      };

      setFuelDirResults(prev => [newResult, ...prev]);

      // 폼 초기화
      setFuelDirForm({
        fuel_name: '',
        fuel_factor: 0,
        fuel_amount: 0,
        fuel_oxyfactor: 1.0000
      });
      setAutoFactorStatus('');

    } catch (error: any) {
      console.error('❌ 연료직접배출량 계산 실패:', error);
      alert(`연료직접배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsCalculatingFuelDir(false);
    }
  }, [fuelDirForm]);

  // 연료직접배출량 저장
  const saveFuelDirData = useCallback(async () => {
    if (!selectedProcess || fuelDirResults.length === 0) {
      alert('저장할 데이터가 없습니다.');
      return;
    }

    try {
      console.log('💾 저장 시작:', {
        process_id: selectedProcess.id,
        results: fuelDirResults
      });

      const savePromises = fuelDirResults.map((result, index) => {
        const requestData = {
          process_id: selectedProcess.id,
          fuel_name: result.fuel_name,
          fuel_factor: result.fuel_factor,
          fuel_amount: result.fuel_amount,
          fuel_oxyfactor: result.fuel_oxyfactor
        };
        
        console.log(`📤 저장 요청 ${index + 1}:`, requestData);
        
        return axiosClient.post(apiEndpoints.cbam.fueldir.create, requestData);
      });

      const responses = await Promise.all(savePromises);
      console.log('✅ 연료직접배출량 데이터 저장 성공:', responses);
      
      // 🚀 자동 집계: 해당 공정의 직접귀속배출량 계산
      try {
        console.log('🔄 자동 집계 시작: 공정 ID', selectedProcess.id);
        const aggregationResponse = await axiosClient.post(
          apiEndpoints.cbam.calculation.process.attrdir(selectedProcess.id)
        );
        console.log('✅ 자동 집계 성공:', aggregationResponse.data);
      } catch (aggregationError: any) {
        console.warn('⚠️ 자동 집계 실패 (수동으로 나중에 실행 가능):', aggregationError);
        // 자동 집계 실패해도 저장은 성공했으므로 경고만 표시
      }
      
      alert('연료직접배출량 데이터가 성공적으로 저장되었습니다!');
      
      // 저장 후 기존 데이터 다시 로드
      await loadAllExistingData();
      
      // 모달 닫기
      onClose();

    } catch (error: any) {
      console.error('❌ 연료직접배출량 데이터 저장 실패:', error);
      console.error('❌ 에러 상세:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      alert(`연료직접배출량 데이터 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess, fuelDirResults, onClose]);

  // 연료직접배출량 결과 삭제 (로컬에서만)
  const removeFuelDirResult = useCallback((index: number) => {
    setFuelDirResults(prev => prev.filter((_, i) => i !== index));
  }, []);

  // ============================================================================
  // 🔍 기존 데이터 로드 및 관리
  // ============================================================================

  // 모든 기존 데이터 로드 (fueldir + matdir)
  const loadAllExistingData = useCallback(async () => {
    if (!selectedProcess?.id) return;
    
    setIsLoadingData(true);
    try {
      console.log('🔍 기존 데이터 로드 시작:', selectedProcess.id);
      
      // 연료직접배출량과 원료직접배출량 데이터를 병렬로 로드
      const [fueldirResponse, matdirResponse] = await Promise.all([
        axiosClient.get(apiEndpoints.cbam.fueldir.byProcess(selectedProcess.id)),
        axiosClient.get(apiEndpoints.cbam.matdir.byProcess(selectedProcess.id))
      ]);
      
      const allResults: FuelDirResult[] = [];
      
      // 연료직접배출량 데이터 처리
      if (fueldirResponse.data && Array.isArray(fueldirResponse.data)) {
        const fueldirResults = fueldirResponse.data.map((item: any) => ({
          id: item.id,
          fuel_name: item.fuel_name,
          fuel_factor: parseFloat(item.fuel_factor) || 0,
          fuel_amount: parseFloat(item.fuel_amount) || 0,
          fuel_oxyfactor: parseFloat(item.fuel_oxyfactor) || 1.0000,
          fueldir_em: parseFloat(item.fueldir_em) || 0,
          calculation_formula: `연료직접배출량 = ${item.fuel_amount} × ${item.fuel_factor} × ${item.fuel_oxyfactor}`,
          type: 'fueldir' as const,
          created_at: item.created_at,
          updated_at: item.updated_at
        }));
        allResults.push(...fueldirResults);
      }
      
      // 원료직접배출량 데이터 처리
      if (matdirResponse.data && Array.isArray(matdirResponse.data)) {
        const matdirResults = matdirResponse.data.map((item: any) => ({
          id: `matdir_${item.id}`,
          fuel_name: item.mat_name,
          fuel_factor: parseFloat(item.mat_factor) || 0,
          fuel_amount: parseFloat(item.mat_amount) || 0,
          fuel_oxyfactor: parseFloat(item.oxyfactor) || 1.0000,
          fueldir_em: parseFloat(item.matdir_em) || 0,
          calculation_formula: `원료직접배출량 = ${item.mat_amount} × ${item.mat_factor} × ${item.oxyfactor}`,
          type: 'matdir' as const,
          created_at: item.created_at,
          updated_at: item.updated_at
        }));
        allResults.push(...matdirResults);
      }
      
      // 생성일 기준으로 최신순 정렬
      allResults.sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB.getTime() - dateA.getTime();
      });
      
      setFuelDirResults(allResults);
      console.log('✅ 기존 데이터 로드 완료:', allResults.length, '개');
      
    } catch (error: any) {
      console.warn('⚠️ 기존 데이터 로드 실패:', error);
      // 에러가 발생해도 새로 계산할 수 있도록 계속 진행
    } finally {
      setIsLoadingData(false);
    }
  }, [selectedProcess?.id]);

  // 컴포넌트 마운트 시 기존 데이터 로드
  useEffect(() => {
    if (selectedProcess?.id) {
      loadAllExistingData();
    }
  }, [selectedProcess?.id, loadAllExistingData]);

  // ============================================================================
  // ✏️ 결과 수정 기능
  // ============================================================================

  const [editingResult, setEditingResult] = useState<FuelDirResult | null>(null);
  const [editForm, setEditForm] = useState<FuelDirForm>({
    fuel_name: '',
    fuel_factor: 0,
    fuel_amount: 0,
    fuel_oxyfactor: 1.0000
  });

  const startEditing = useCallback((result: FuelDirResult) => {
    setEditingResult(result);
    setEditForm({
      fuel_name: result.fuel_name,
      fuel_factor: result.fuel_factor,
      fuel_amount: result.fuel_amount,
      fuel_oxyfactor: result.fuel_oxyfactor
    });
  }, []);

  const cancelEditing = useCallback(() => {
    setEditingResult(null);
    setEditForm({
      fuel_name: '',
      fuel_factor: 0,
      fuel_amount: 0,
      fuel_oxyfactor: 1.0000
    });
  }, []);

  const saveEdit = useCallback(async () => {
    if (!editingResult || !selectedProcess?.id) return;
    
    try {
      const isMatDir = editingResult.id.toString().startsWith('matdir_');
      const endpoint = isMatDir ? apiEndpoints.cbam.matdir.update : apiEndpoints.cbam.fueldir.update;
      const actualId = isMatDir ? parseInt(editingResult.id.toString().replace('matdir_', '')) : Number(editingResult.id);
      
      if (isMatDir) {
        // matdir의 경우 필드명 변경
        const matdirUpdateData = {
          mat_name: editForm.fuel_name,
          mat_factor: editForm.fuel_factor,
          mat_amount: editForm.fuel_amount,
          oxyfactor: editForm.fuel_oxyfactor
        };
        
        await axiosClient.put(endpoint(actualId), matdirUpdateData);
      } else {
        // fueldir의 경우
        const fueldirUpdateData = {
          fuel_name: editForm.fuel_name,
          fuel_factor: editForm.fuel_factor,
          fuel_amount: editForm.fuel_amount,
          fuel_oxyfactor: editForm.fuel_oxyfactor
        };
        
        await axiosClient.put(endpoint(actualId), fueldirUpdateData);
      }

      // 결과 목록 업데이트
      setFuelDirResults(prev => prev.map(result => 
        result.id === editingResult.id 
          ? { 
              ...result, 
              ...editForm,
              updated_at: new Date().toISOString()
            }
          : result
      ));
      
      setEditingResult(null);
      alert('수정이 완료되었습니다!');
      
    } catch (error: any) {
      console.error('❌ 결과 수정 실패:', error);
      alert(`수정에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [editingResult, editForm, selectedProcess?.id]);

  // ============================================================================
  // 🗑️ 결과 삭제 기능
  // ============================================================================

  const deleteResult = useCallback(async (result: FuelDirResult) => {
    if (!selectedProcess?.id) return;
    
    if (!confirm('정말로 이 결과를 삭제하시겠습니까?')) return;
    
    try {
      const isMatDir = result.id.toString().startsWith('matdir_');
      const endpoint = isMatDir ? apiEndpoints.cbam.matdir.delete : apiEndpoints.cbam.fueldir.delete;
      const actualId = isMatDir ? parseInt(result.id.toString().replace('matdir_', '')) : Number(result.id);
      
      await axiosClient.delete(endpoint(actualId));
      
      // 결과 목록에서 제거
      setFuelDirResults(prev => prev.filter(r => r.id !== result.id));
      alert('삭제가 완료되었습니다!');
      
    } catch (error: any) {
      console.error('❌ 결과 삭제 실패:', error);
      alert(`삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess?.id]);

  // 날짜 포맷팅 함수
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-6xl mx-4 shadow-2xl">
        {/* 모달 헤더 */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-white">
            ⛽ 연료직접배출량 - {selectedProcess?.process_name}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl transition-colors"
          >
            ×
          </button>
        </div>

        {/* 탭 네비게이션 */}
        <div className="mb-6 flex gap-2 border-b border-gray-700">
          <div className="px-4 py-2 text-sm font-medium text-blue-400 border-b-2 border-blue-400">
            연료 | 공정 배출 활동량
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 왼쪽: 입력 폼 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">연료 | 공정 배출 활동량</h4>
              <button className="text-blue-400 hover:text-blue-300">+</button>
            </div>

            <div className="space-y-4">
              {/* 투입된 연료명 */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  투입된 연료명
                  <span className="text-xs text-gray-400 ml-2">(자유 입력 가능)</span>
                </label>
                <input
                  type="text"
                  value={fuelDirForm.fuel_name}
                  onChange={(e) => handleFuelNameChange(e.target.value)}
                  onBlur={handleFuelNameBlur}
                  className="w-full px-3 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  placeholder="예: 원유, 휘발유, 등유"
                />
                
                {/* 자동 배출계수 상태 표시 */}
                {autoFactorStatus && (
                  <div className={`mt-1 text-xs ${
                    autoFactorStatus.includes('✅') ? 'text-green-400' : 
                    autoFactorStatus.includes('⚠️') ? 'text-yellow-400' : 
                    'text-blue-400'
                  }`}>
                    {autoFactorStatus}
                  </div>
                )}

                {/* 연료 제안 드롭다운 */}
                {showSuggestions && fuelSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-md shadow-lg max-h-40 overflow-y-auto">
                    {fuelSuggestions.map((fuel, index) => (
                      <button
                        key={fuel.id}
                        onClick={() => handleFuelSelect(fuel)}
                        className="w-full px-3 py-2 text-left text-white hover:bg-gray-600 focus:bg-gray-600 focus:outline-none"
                      >
                        <div className="font-medium">{fuel.fuel_name}</div>
                        <div className="text-xs text-gray-400">배출계수 자동 설정</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* 배출계수 (읽기 전용) */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  배출계수 {fuelDirForm.fuel_factor > 0 && <span className="text-green-400">(자동 설정됨)</span>}
                </label>
                <div className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white">
                  {fuelDirForm.fuel_factor > 0 ? fuelDirForm.fuel_factor : '연료를 선택해주세요'}
                </div>
              </div>

              {/* 투입된 연료량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">투입된 연료량</label>
                <input
                  type="number"
                  step="0.000001"
                  min="0"
                  value={fuelDirForm.fuel_amount}
                  onChange={(e) => setFuelDirForm(prev => ({ ...prev, fuel_amount: parseFloat(e.target.value) || 0 }))}
                  className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000000"
                />
              </div>

              {/* 산화계수 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">산화계수</label>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  value={fuelDirForm.fuel_oxyfactor}
                  onChange={(e) => setFuelDirForm(prev => ({ ...prev, fuel_oxyfactor: parseFloat(e.target.value) || 1.0000 }))}
                  className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1.0000"
                />
              </div>

              {/* 계산 버튼 */}
              <button
                onClick={calculateFuelDirEmission}
                disabled={isCalculatingFuelDir}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {isCalculatingFuelDir ? '계산 중...' : '🧮 연료직접배출량 계산'}
              </button>
            </div>
          </div>

          {/* 오른쪽: 계산 결과 목록 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">계산 결과</h4>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">{fuelDirResults.length}개</span>
                <button
                  onClick={loadAllExistingData}
                  disabled={isLoadingData}
                  className="text-blue-400 hover:text-blue-300 text-sm disabled:text-gray-500"
                >
                  {isLoadingData ? '로딩 중...' : '🔄 새로고침'}
                </button>
              </div>
            </div>

            {isLoadingData ? (
              <div className="text-center text-gray-400 py-8">
                데이터를 불러오는 중...
              </div>
            ) : fuelDirResults.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                계산된 결과가 없습니다.
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {fuelDirResults.map((result, index) => (
                  <div key={result.id} className="bg-gray-600 rounded-lg p-3">
                    {editingResult?.id === result.id ? (
                      // 수정 모드
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-blue-400">
                            {result.type === 'matdir' ? '원료직접배출량' : '연료직접배출량'} 수정 중
                          </span>
                          <div className="flex gap-2">
                            <button
                              onClick={saveEdit}
                              className="text-green-400 hover:text-green-300 text-sm"
                            >
                              저장
                            </button>
                            <button
                              onClick={cancelEditing}
                              className="text-gray-400 hover:text-gray-300 text-sm"
                            >
                              취소
                            </button>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="text"
                            value={editForm.fuel_name}
                            onChange={(e) => setEditForm(prev => ({ ...prev, fuel_name: e.target.value }))}
                            className="px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white text-sm"
                            placeholder="이름"
                          />
                          <input
                            type="number"
                            step="0.000001"
                            value={editForm.fuel_amount}
                            onChange={(e) => setEditForm(prev => ({ ...prev, fuel_amount: parseFloat(e.target.value) || 0 }))}
                            className="px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white text-sm"
                            placeholder="수량"
                          />
                          <input
                            type="number"
                            step="0.000001"
                            value={editForm.fuel_factor}
                            onChange={(e) => setEditForm(prev => ({ ...prev, fuel_factor: parseFloat(e.target.value) || 0 }))}
                            className="px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white text-sm"
                            placeholder="배출계수"
                          />
                          <input
                            type="number"
                            step="0.0001"
                            value={editForm.fuel_oxyfactor}
                            onChange={(e) => setEditForm(prev => ({ ...prev, fuel_oxyfactor: parseFloat(e.target.value) || 1.0000 }))}
                            className="px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white text-sm"
                            placeholder="산화계수"
                          />
                        </div>
                      </div>
                    ) : (
                      // 표시 모드
                      <>
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <h5 className="font-medium text-white">{result.fuel_name}</h5>
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              result.type === 'matdir' 
                                ? 'bg-purple-600 text-white' 
                                : 'bg-blue-600 text-white'
                            }`}>
                              {result.type === 'matdir' ? '원료' : '연료'}
                            </span>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => startEditing(result)}
                              className="text-blue-400 hover:text-blue-300 text-sm"
                            >
                              수정
                            </button>
                            <button
                              onClick={() => deleteResult(result)}
                              className="text-red-400 hover:text-red-300 text-sm"
                            >
                              삭제
                            </button>
                          </div>
                        </div>
                        
                        <div className="text-sm text-gray-300 space-y-1">
                          <div className="grid grid-cols-2 gap-4">
                            <div>배출계수: {result.fuel_factor}</div>
                            <div>수량: {result.fuel_amount}</div>
                            <div>산화계수: {result.fuel_oxyfactor}</div>
                            <div className="font-medium text-green-400">
                              배출량: {result.fueldir_em}
                            </div>
                          </div>
                          
                          <div className="text-xs text-gray-400 mt-2 p-2 bg-gray-700 rounded">
                            {result.calculation_formula}
                          </div>
                          
                          {result.created_at && (
                            <div className="text-xs text-gray-500 mt-2">
                              생성: {formatDate(result.created_at)}
                              {result.updated_at && result.updated_at !== result.created_at && 
                                ` | 수정: ${formatDate(result.updated_at)}`
                              }
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}

            {fuelDirResults.length > 0 && (
              <button
                onClick={saveFuelDirData}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors mt-4"
              >
                💾 연료직접배출량 데이터 저장
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
