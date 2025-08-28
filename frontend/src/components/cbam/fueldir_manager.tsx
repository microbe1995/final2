'use client';

import React, { useState, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

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
  id: number;
  fuel_name: string;
  fuel_factor: number;
  fuel_amount: number;
  fuel_oxyfactor: number;
  fueldir_em: number;
  calculation_formula: string;
}

export default function FuelDirManager({ selectedProcess, onClose }: FuelDirManagerProps) {
  // 연료직접배출량 모달 상태
  const [fuelDirForm, setFuelDirForm] = useState<FuelDirForm>({
    fuel_name: '',
    fuel_factor: 0,
    fuel_amount: 0,
    fuel_oxyfactor: 1.0000
  });
  const [fuelDirResults, setFuelDirResults] = useState<FuelDirResult[]>([]);
  const [isCalculatingFuelDir, setIsCalculatingFuelDir] = useState(false);

  // 연료직접배출량 계산
  const calculateFuelDirEmission = useCallback(async () => {
    if (!fuelDirForm.fuel_name || fuelDirForm.fuel_factor <= 0 || fuelDirForm.fuel_amount <= 0) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setIsCalculatingFuelDir(true);
    try {
      const response = await axiosClient.post(apiEndpoints.calculation.fueldir.calculate, {
        fuel_amount: fuelDirForm.fuel_amount,
        fuel_factor: fuelDirForm.fuel_factor,
        fuel_oxyfactor: fuelDirForm.fuel_oxyfactor
      });

      const calculationResult = response.data;
      console.log('✅ 연료직접배출량 계산 성공:', calculationResult);

      // 결과를 목록에 추가
      setFuelDirResults(prev => [...prev, {
        id: Date.now(),
        fuel_name: fuelDirForm.fuel_name,
        fuel_factor: fuelDirForm.fuel_factor,
        fuel_amount: fuelDirForm.fuel_amount,
        fuel_oxyfactor: fuelDirForm.fuel_oxyfactor,
        fueldir_em: calculationResult.fueldir_em,
        calculation_formula: calculationResult.calculation_formula
      }]);

      // 폼 초기화
      setFuelDirForm({
        fuel_name: '',
        fuel_factor: 0,
        fuel_amount: 0,
        fuel_oxyfactor: 1.0000
      });

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
        
        return axiosClient.post(apiEndpoints.calculation.fueldir.create, requestData);
      });

      const responses = await Promise.all(savePromises);
      console.log('✅ 연료직접배출량 데이터 저장 성공:', responses);
      alert('연료직접배출량 데이터가 성공적으로 저장되었습니다!');
      
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

  // 연료직접배출량 결과 삭제
  const removeFuelDirResult = useCallback((index: number) => {
    setFuelDirResults(prev => prev.filter((_, i) => i !== index));
  }, []);

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
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">투입된 연료명</label>
                <input
                  type="text"
                  value={fuelDirForm.fuel_name}
                  onChange={(e) => setFuelDirForm(prev => ({ ...prev, fuel_name: e.target.value }))}
                  className="w-full px-3 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  placeholder="예: 석탄, 천연가스"
                />
              </div>

              {/* 배출계수 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">배출계수</label>
                <input
                  type="number"
                  step="0.000001"
                  min="0"
                  value={fuelDirForm.fuel_factor}
                  onChange={(e) => setFuelDirForm(prev => ({ ...prev, fuel_factor: parseFloat(e.target.value) || 0 }))}
                  className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000000"
                />
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
                  className="w-full px-3 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
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
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1.0000"
                />
              </div>

              {/* 버튼들 */}
              <div className="flex gap-2">
                <button
                  onClick={calculateFuelDirEmission}
                  disabled={isCalculatingFuelDir}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors disabled:opacity-50"
                >
                  {isCalculatingFuelDir ? '계산 중...' : '확인'}
                </button>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors">
                  수정
                </button>
              </div>
            </div>

            {/* 직접 배출량 표시 */}
            <div className="mt-6 pt-4 border-t border-gray-600">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-300">직접 배출량</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    readOnly
                    value={fuelDirResults.reduce((sum, result) => {
                      const emission = typeof result.fueldir_em === 'number' ? result.fueldir_em : 0;
                      return sum + emission;
                    }, 0).toFixed(6)}
                    className="w-32 px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white text-right"
                  />
                  <button
                    onClick={saveFuelDirData}
                    disabled={fuelDirResults.length === 0}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors disabled:opacity-50"
                  >
                    저장
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 오른쪽: 계산 결과 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-lg font-medium text-white mb-4">계산 결과</h4>
            
            {fuelDirResults.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p>연료 정보를 입력하고 &quot;확인&quot; 버튼을 눌러 계산을 시작하세요.</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {fuelDirResults.map((result, index) => (
                  <div key={result.id} className="bg-gray-600 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <h5 className="font-medium text-white">{result.fuel_name}</h5>
                      <button
                        onClick={() => removeFuelDirResult(index)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        삭제
                      </button>
                    </div>
                    <div className="text-sm text-gray-300 space-y-1">
                      <div>배출계수: {result.fuel_factor}</div>
                      <div>연료량: {result.fuel_amount}</div>
                      <div>산화계수: {result.fuel_oxyfactor}</div>
                      <div className="text-green-400 font-medium">
                        연료직접배출량: {typeof result.fueldir_em === 'number' ? result.fueldir_em.toFixed(6) : '0.000000'} tCO2e
                      </div>
                      <div className="text-xs text-gray-400 mt-2">
                        {result.calculation_formula}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
