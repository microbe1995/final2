'use client';

import React, { useState, useCallback, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useMaterialMasterAPI, MaterialMapping } from '@/hooks/useMaterialMasterAPI';

interface MatDirManagerProps {
  selectedProcess: any;
  onClose: () => void;
}

interface MatDirForm {
  mat_name: string;
  mat_factor: number;
  mat_amount: number;
  oxyfactor: number;
}

interface MatDirResult {
  id: number;
  mat_name: string;
  mat_factor: number;
  mat_amount: number;
  oxyfactor: number;
  matdir_em: number;
  calculation_formula: string;
}

export default function MatDirManager({ selectedProcess, onClose }: MatDirManagerProps) {
  // Material Master API 훅 (matdir 스키마 기반)
  const { 
    searchMaterialByName, 
    getMaterialFactor, 
    getMaterialNameSuggestions,
    autoMapMaterialFactor,
    loading: materialLoading, 
    error: materialError 
  } = useMaterialMasterAPI();

  // 원료직접배출량 모달 상태
  const [matDirForm, setMatDirForm] = useState<MatDirForm>({
    mat_name: '',
    mat_factor: 0,
    mat_amount: 0,
    oxyfactor: 1.0000
  });
  const [matDirResults, setMatDirResults] = useState<MatDirResult[]>([]);
  const [isCalculatingMatDir, setIsCalculatingMatDir] = useState(false);

  // Material Master 관련 상태 (matdir 스키마 기반)
  const [materialSuggestions, setMaterialSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [autoFactorStatus, setAutoFactorStatus] = useState<string>('');

  // 원료명 입력 시 자동 검색
  const handleMaterialNameChange = useCallback(async (matName: string) => {
    setMatDirForm(prev => ({ ...prev, mat_name: matName }));
    
    if (matName.length >= 2) {
      const suggestions = await getMaterialNameSuggestions(matName);
      setMaterialSuggestions(suggestions);
      setShowSuggestions(true);
    } else {
      setMaterialSuggestions([]);
      setShowSuggestions(false);
    }
  }, [getMaterialNameSuggestions]);

  // 원료명 선택 시 배출계수 자동 조회
  const handleMaterialSelect = useCallback(async (selectedName: string) => {
    setMatDirForm(prev => ({ 
      ...prev, 
      mat_name: selectedName
    }));
    setShowSuggestions(false);
    
    // 배출계수 자동 매핑
    try {
      const autoFactor = await autoMapMaterialFactor(selectedName);
      if (autoFactor !== null) {
        setMatDirForm(prev => ({ ...prev, mat_factor: autoFactor }));
        setAutoFactorStatus(`✅ 자동 설정: ${selectedName} (배출계수: ${autoFactor})`);
      } else {
        setAutoFactorStatus(`⚠️ 배출계수를 찾을 수 없음: ${selectedName}`);
      }
    } catch (err) {
      setAutoFactorStatus(`❌ 배출계수 조회 실패: ${selectedName}`);
    }
  }, [autoMapMaterialFactor]);

  // 원료명 입력 완료 시 배출계수 자동 조회
  const handleMaterialNameBlur = useCallback(async () => {
    if (matDirForm.mat_name && matDirForm.mat_factor === 0) {
      setAutoFactorStatus('🔍 배출계수 조회 중...');
      try {
        const factorData = await getMaterialFactor(matDirForm.mat_name);
        
        if (factorData.success && factorData.data.length > 0) {
          const factor = factorData.data[0].mat_factor;
          setMatDirForm(prev => ({ ...prev, mat_factor: factor }));
          setAutoFactorStatus(`✅ 자동 조회: ${matDirForm.mat_name} (배출계수: ${factor})`);
        } else {
          setAutoFactorStatus(`⚠️ 배출계수를 찾을 수 없음: ${matDirForm.mat_name}`);
        }
      } catch (err) {
        setAutoFactorStatus(`❌ 배출계수 조회 실패: ${matDirForm.mat_name}`);
      }
    }
  }, [matDirForm.mat_name, matDirForm.mat_factor, getMaterialFactor]);

  // 원료직접배출량 계산
  const calculateMatDirEmission = useCallback(async () => {
    if (!matDirForm.mat_name || matDirForm.mat_factor <= 0 || matDirForm.mat_amount <= 0) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setIsCalculatingMatDir(true);
    try {
      const response = await axiosClient.post(apiEndpoints.calculation.matdir.calculate, {
        mat_amount: matDirForm.mat_amount,
        mat_factor: matDirForm.mat_factor,
        oxyfactor: matDirForm.oxyfactor
      });

      const calculationResult = response.data;
      console.log('✅ 원료직접배출량 계산 성공:', calculationResult);

      // 결과를 목록에 추가
      setMatDirResults(prev => [...prev, {
        id: Date.now(),
        mat_name: matDirForm.mat_name,
        mat_factor: matDirForm.mat_factor,
        mat_amount: matDirForm.mat_amount,
        oxyfactor: matDirForm.oxyfactor,
        matdir_em: calculationResult.matdir_em,
        calculation_formula: calculationResult.calculation_formula
      }]);

      // 폼 초기화
      setMatDirForm({
        mat_name: '',
        mat_factor: 0,
        mat_amount: 0,
        oxyfactor: 1.0000
      });
      setAutoFactorStatus('');

    } catch (error: any) {
      console.error('❌ 원료직접배출량 계산 실패:', error);
      alert(`원료직접배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsCalculatingMatDir(false);
    }
  }, [matDirForm]);

  // 원료직접배출량 저장
  const saveMatDirData = useCallback(async () => {
    if (!selectedProcess || matDirResults.length === 0) {
      alert('저장할 데이터가 없습니다.');
      return;
    }

    try {
      console.log('💾 저장 시작:', {
        process_id: selectedProcess.id,
        results: matDirResults
      });

      const savePromises = matDirResults.map((result, index) => {
        const requestData = {
          process_id: selectedProcess.id,
          mat_name: result.mat_name,
          mat_factor: result.mat_factor,
          mat_amount: result.mat_amount,
          oxyfactor: result.oxyfactor
        };
        
        console.log(`📤 저장 요청 ${index + 1}:`, requestData);
        
        return axiosClient.post(apiEndpoints.calculation.matdir.create, requestData);
      });

      const responses = await Promise.all(savePromises);
      console.log('✅ 원료직접배출량 데이터 저장 성공:', responses);
      
      // 🚀 자동 집계: 해당 공정의 직접귀속배출량 계산
      try {
        console.log('🔄 자동 집계 시작: 공정 ID', selectedProcess.id);
        const aggregationResponse = await axiosClient.post(
          `/api/v1/boundary/emission/process/${selectedProcess.id}/attrdir`
        );
        console.log('✅ 자동 집계 성공:', aggregationResponse.data);
      } catch (aggregationError: any) {
        console.warn('⚠️ 자동 집계 실패 (수동으로 나중에 실행 가능):', aggregationError);
        // 자동 집계 실패해도 저장은 성공했으므로 경고만 표시
      }
      
      alert('원료직접배출량 데이터가 성공적으로 저장되었습니다!');
      
      // 모달 닫기
      onClose();

    } catch (error: any) {
      console.error('❌ 원료직접배출량 데이터 저장 실패:', error);
      console.error('❌ 에러 상세:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      alert(`원료직접배출량 데이터 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess, matDirResults, onClose]);

  // 원료직접배출량 결과 삭제
  const removeMatDirResult = useCallback((index: number) => {
    setMatDirResults(prev => prev.filter((_, i) => i !== index));
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-6xl mx-4 shadow-2xl">
        {/* 모달 헤더 */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-white">
            📊 원료직접배출량 - {selectedProcess?.process_name}
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
            원료 | 공정 배출 활동량
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 왼쪽: 입력 폼 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">원료 | 공정 배출 활동량</h4>
              <button className="text-blue-400 hover:text-blue-300">+</button>
            </div>

            <div className="space-y-4">
              {/* 투입된 원료명 */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-300 mb-2">투입된 원료명</label>
                <input
                  type="text"
                  value={matDirForm.mat_name}
                  onChange={(e) => handleMaterialNameChange(e.target.value)}
                  onBlur={handleMaterialNameBlur}
                  className="w-full px-3 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  placeholder="예: 직접환원철, EAF 탄소 전극"
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

                {/* 원료명 제안 드롭다운 */}
                {showSuggestions && materialSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-md shadow-lg max-h-40 overflow-y-auto">
                    {materialSuggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleMaterialSelect(suggestion)}
                        className="w-full px-3 py-2 text-left text-white hover:bg-gray-600 focus:bg-gray-600 focus:outline-none"
                      >
                        <div className="font-medium">{suggestion}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* 배출계수 (읽기 전용) */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  배출계수 {matDirForm.mat_factor > 0 && <span className="text-green-400">(자동 설정됨)</span>}
                </label>
                <div className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white">
                  {matDirForm.mat_factor > 0 ? matDirForm.mat_factor : '원료를 선택해주세요'}
                </div>
              </div>

              {/* 투입된 원료량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">투입된 원료량</label>
                <input
                  type="number"
                  step="0.000001"
                  min="0"
                  value={matDirForm.mat_amount}
                  onChange={(e) => setMatDirForm(prev => ({ ...prev, mat_amount: parseFloat(e.target.value) || 0 }))}
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
                  value={matDirForm.oxyfactor}
                  onChange={(e) => setMatDirForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1.0000 }))}
                  className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1.0000"
                />
              </div>

              {/* 계산 버튼 */}
              <button
                onClick={calculateMatDirEmission}
                disabled={isCalculatingMatDir || materialLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {isCalculatingMatDir ? '계산 중...' : '🧮 원료직접배출량 계산'}
              </button>
            </div>
          </div>

          {/* 오른쪽: 결과 목록 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">계산 결과</h4>
              <span className="text-sm text-gray-400">{matDirResults.length}개</span>
            </div>

            {matDirResults.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                계산된 결과가 없습니다.
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {matDirResults.map((result, index) => (
                  <div key={result.id} className="bg-gray-600 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <h5 className="font-medium text-white">{result.mat_name}</h5>
                      <button
                        onClick={() => removeMatDirResult(index)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        삭제
                      </button>
                    </div>
                    <div className="text-sm text-gray-300 space-y-1">
                      <div>배출계수: {result.mat_factor}</div>
                      <div>원료량: {result.mat_amount}</div>
                      <div>산화계수: {result.oxyfactor}</div>
                      <div className="font-medium text-green-400">
                        원료직접배출량: {result.matdir_em}
                      </div>
                      <div className="text-xs text-gray-400 mt-2">
                        {result.calculation_formula}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {matDirResults.length > 0 && (
              <button
                onClick={saveMatDirData}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors mt-4"
              >
                💾 원료직접배출량 데이터 저장
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
