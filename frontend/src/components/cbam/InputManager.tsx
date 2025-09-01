'use client';

import React, { useState, useCallback, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useFuelMasterAPI } from '@/hooks/useFuelMasterAPI';
import { FuelMaster } from '@/lib/types';

interface InputManagerProps {
  selectedProcess: any;
  onClose: () => void;
  onDataSaved?: () => void; // 데이터 저장 후 콜백 추가
}

interface InputForm {
  name: string;
  factor: number;
  amount: number;
  oxyfactor: number;
}

interface InputResult {
  id: number | string;
  name: string;
  factor: number;
  amount: number;
  oxyfactor: number;
  emission: number;
  calculation_formula: string;
  type: 'matdir' | 'fueldir';
  created_at?: string;
  updated_at?: string;
}

export default function InputManager({ selectedProcess, onClose, onDataSaved }: InputManagerProps) {
  // Fuel Master API Hook
  const { searchFuels, getFuelFactor } = useFuelMasterAPI();

  // 현재 활성 탭
  const [activeTab, setActiveTab] = useState<'matdir' | 'fueldir'>('matdir');

  // 입력 폼 상태
  const [matdirForm, setMatdirForm] = useState<InputForm>({
    name: '',
    factor: 0,
    amount: 0,
    oxyfactor: 1.0000
  });

  const [fueldirForm, setFueldirForm] = useState<InputForm>({
    name: '',
    factor: 0,
    amount: 0,
    oxyfactor: 1.0000
  });

  // 결과 목록
  const [inputResults, setInputResults] = useState<InputResult[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(false);

  // Fuel Master 자동 배출계수 관련 상태
  const [fuelSuggestions, setFuelSuggestions] = useState<FuelMaster[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [autoFactorStatus, setAutoFactorStatus] = useState<string>('');
  
  // Material Master 자동 배출계수 관련 상태
  const [materialSuggestions, setMaterialSuggestions] = useState<any[]>([]);
  const [showMaterialSuggestions, setShowMaterialSuggestions] = useState(false);
  const [materialAutoFactorStatus, setMaterialAutoFactorStatus] = useState<string>('');

  // 수정 모드 상태
  const [editingResult, setEditingResult] = useState<InputResult | null>(null);
  const [editForm, setEditForm] = useState<InputForm>({
    name: '',
    factor: 0,
    amount: 0,
    oxyfactor: 1.0000
  });

  // ============================================================================
  // 🔍 기존 데이터 로드
  // ============================================================================

  const loadAllExistingData = useCallback(async () => {
    if (!selectedProcess?.id) return;
    
    setIsLoadingData(true);
    try {
      console.log('🔍 기존 데이터 로드 시작:', selectedProcess.id);
      
      // 원료직접배출량과 연료직접배출량 데이터를 병렬로 로드
      const [matdirResponse, fueldirResponse] = await Promise.all([
        axiosClient.get(apiEndpoints.cbam.matdir.byProcess(selectedProcess.id)),
        axiosClient.get(apiEndpoints.cbam.fueldir.byProcess(selectedProcess.id))
      ]);
      
      const allResults: InputResult[] = [];
      
      // 원료직접배출량 데이터 처리
      if (matdirResponse.data && Array.isArray(matdirResponse.data)) {
        const matdirResults = matdirResponse.data.map((item: any) => ({
          id: item.id,
          name: item.mat_name,
          factor: parseFloat(item.mat_factor) || 0,
          amount: parseFloat(item.mat_amount) || 0,
          oxyfactor: parseFloat(item.oxyfactor) || 1.0000,
          emission: parseFloat(item.matdir_em) || 0,
          calculation_formula: `원료직접배출량 = ${item.mat_amount} × ${item.mat_factor} × ${item.oxyfactor}`,
          type: 'matdir' as const,
          created_at: item.created_at,
          updated_at: item.updated_at
        }));
        allResults.push(...matdirResults);
      }
      
      // 연료직접배출량 데이터 처리
      if (fueldirResponse.data && Array.isArray(fueldirResponse.data)) {
        const fueldirResults = fueldirResponse.data.map((item: any) => ({
          id: item.id,
          name: item.fuel_name,
          factor: parseFloat(item.fuel_factor) || 0,
          amount: parseFloat(item.fuel_amount) || 0,
          oxyfactor: parseFloat(item.fuel_oxyfactor) || 1.0000,
          emission: parseFloat(item.fueldir_em) || 0,
          calculation_formula: `연료직접배출량 = ${item.fuel_amount} × ${item.fuel_factor} × ${item.fuel_oxyfactor}`,
          type: 'fueldir' as const,
          created_at: item.created_at,
          updated_at: item.updated_at
        }));
        allResults.push(...fueldirResults);
      }
      
      // 생성일 기준으로 최신순 정렬
      allResults.sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB.getTime() - dateA.getTime();
      });
      
      setInputResults(allResults);
      console.log('✅ 기존 데이터 로드 완료:', allResults.length, '개');
      
    } catch (error: any) {
      console.warn('⚠️ 기존 데이터 로드 실패:', error);
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
  // 🔧 원료직접배출량 관련 함수들
  // ============================================================================

  const handleMatdirNameChange = useCallback(async (name: string) => {
    setMatdirForm(prev => ({ ...prev, name }));
    
    if (name.trim().length >= 1) {
      try {
         console.log('🔍 Material Master 검색 시작:', name);
        console.log('🔍 API 엔드포인트:', apiEndpoints.materialMaster.search(name));
        
        // Material Master에서 원료명 검색
        const response = await axiosClient.get(apiEndpoints.materialMaster.search(name));
        console.log('✅ Material Master 검색 응답:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          setMaterialSuggestions(response.data);
          setShowMaterialSuggestions(true);
          console.log('✅ Material Master 검색 결과:', response.data.length, '개');
        } else {
          console.warn('⚠️ Material Master 검색 결과가 배열이 아님:', response.data);
          setMaterialSuggestions([]);
          setShowMaterialSuggestions(false);
        }
      } catch (err: any) {
        console.error('❌ 원료 검색 실패:', err);
        console.error('❌ 에러 상세:', err.response?.data || err.message);
        setMaterialSuggestions([]);
        setShowMaterialSuggestions(false);
      }
    } else {
      setMaterialSuggestions([]);
      setShowMaterialSuggestions(false);
    }
  }, []);

  const handleMatdirNameBlur = useCallback(async () => {
    if (matdirForm.name && matdirForm.factor === 0) {
      setMaterialAutoFactorStatus('🔍 배출계수 조회 중...');
      try {
        console.log('🔍 Material Master 배출계수 조회 시작:', matdirForm.name);
        console.log('🔍 API 엔드포인트:', apiEndpoints.materialMaster.getFactor(matdirForm.name));
        
        const response = await axiosClient.get(apiEndpoints.materialMaster.getFactor(matdirForm.name));
        console.log('✅ Material Master 배출계수 조회 응답:', response.data);
        
        if (response.data && response.data.found && response.data.mat_factor !== null) {
          const factor = response.data.mat_factor;
          setMatdirForm(prev => ({ ...prev, factor }));
          setMaterialAutoFactorStatus(`✅ 자동 조회: ${matdirForm.name} (배출계수: ${factor})`);
          console.log('✅ 배출계수 자동 설정 성공:', factor);
        } else {
          setMaterialAutoFactorStatus(`⚠️ 배출계수를 찾을 수 없음: ${matdirForm.name}`);
          console.warn('⚠️ 배출계수를 찾을 수 없음:', response.data);
        }
      } catch (err: any) {
        console.error('❌ 배출계수 조회 실패:', err);
        console.error('❌ 에러 상세:', err.response?.data || err.message);
        setMaterialAutoFactorStatus(`❌ 배출계수 조회 실패: ${matdirForm.name}`);
      }
    }
  }, [matdirForm.name, matdirForm.factor]);

  const handleMaterialSelect = useCallback((material: any) => {
    setMaterialSuggestions([]);
    setShowMaterialSuggestions(false);
    setMatdirForm(prev => ({ 
      ...prev, 
      name: material.mat_name || material.name,
      factor: material.mat_factor || 0 
    }));
    setMaterialAutoFactorStatus(`✅ 자동 설정: ${material.mat_name || material.name} (배출계수: ${material.mat_factor || 0})`);
  }, []);

  const calculateMatdirEmission = useCallback(async () => {
    if (!matdirForm.name || matdirForm.factor <= 0 || matdirForm.amount <= 0) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setIsCalculating(true);
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.matdir.calculate, {
        mat_amount: matdirForm.amount,
        mat_factor: matdirForm.factor,
        oxyfactor: matdirForm.oxyfactor
      });

      const calculationResult = response.data;
      console.log('✅ 원료직접배출량 계산 성공:', calculationResult);

      // 결과를 목록에 추가
      const newResult: InputResult = {
        id: Date.now(),
        name: matdirForm.name,
        factor: matdirForm.factor,
        amount: matdirForm.amount,
        oxyfactor: matdirForm.oxyfactor,
        emission: calculationResult.matdir_em,
        calculation_formula: calculationResult.calculation_formula,
        type: 'matdir',
        created_at: new Date().toISOString()
      };

      setInputResults(prev => [newResult, ...prev]);

      // 폼 초기화
      setMatdirForm({
        name: '',
        factor: 0,
        amount: 0,
        oxyfactor: 1.0000
      });
      setMaterialAutoFactorStatus('');

    } catch (error: any) {
      console.error('❌ 원료직접배출량 계산 실패:', error);
      alert(`원료직접배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsCalculating(false);
    }
  }, [matdirForm]);

  // ============================================================================
  // ⛽ 연료직접배출량 관련 함수들
  // ============================================================================

  const handleFueldirNameChange = useCallback(async (name: string) => {
    setFueldirForm(prev => ({ ...prev, name }));
    
    if (name.trim().length >= 1) {
      const suggestions = await searchFuels(name);
      if (suggestions) {
        setFuelSuggestions(suggestions);
        setShowSuggestions(true);
      }
    } else {
      setFuelSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchFuels]);

  const handleFuelSelect = useCallback((fuel: FuelMaster) => {
    setFuelSuggestions([]);
    setShowSuggestions(false);
    setFueldirForm(prev => ({ ...prev, factor: fuel.fuel_factor || 0 }));
    setAutoFactorStatus(`✅ 자동 설정: ${fuel.fuel_name} (배출계수: ${fuel.fuel_factor || 0})`);
  }, []);

  const handleFueldirNameBlur = useCallback(async () => {
    if (fueldirForm.name && fueldirForm.factor === 0) {
      setAutoFactorStatus('🔍 배출계수 조회 중...');
      try {
        const factorResponse = await getFuelFactor(fueldirForm.name);
        
        if (factorResponse && factorResponse.found && factorResponse.fuel_factor !== null) {
          const factor = factorResponse.fuel_factor;
          setFueldirForm(prev => ({ ...prev, factor }));
          setAutoFactorStatus(`✅ 자동 조회: ${fueldirForm.name} (배출계수: ${factor})`);
        } else {
          setAutoFactorStatus(`⚠️ 배출계수를 찾을 수 없음: ${fueldirForm.name}`);
        }
      } catch (err) {
        console.error('배출계수 조회 실패:', err);
        setAutoFactorStatus(`❌ 배출계수 조회 실패: ${fueldirForm.name}`);
      }
    }
  }, [fueldirForm.name, fueldirForm.factor, getFuelFactor]);

  const calculateFueldirEmission = useCallback(async () => {
    if (!fueldirForm.name || fueldirForm.factor <= 0 || fueldirForm.amount <= 0) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    setIsCalculating(true);
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.fueldir.calculate, {
        fuel_amount: fueldirForm.amount,
        fuel_factor: fueldirForm.factor,
        fuel_oxyfactor: fueldirForm.oxyfactor
      });

      const calculationResult = response.data;
      console.log('✅ 연료직접배출량 계산 성공:', calculationResult);

      // 결과를 목록에 추가
      const newResult: InputResult = {
        id: Date.now(),
        name: fueldirForm.name,
        factor: fueldirForm.factor,
        amount: fueldirForm.amount,
        oxyfactor: fueldirForm.oxyfactor,
        emission: calculationResult.fueldir_em,
        calculation_formula: calculationResult.calculation_formula,
        type: 'fueldir',
        created_at: new Date().toISOString()
      };

      setInputResults(prev => [newResult, ...prev]);

      // 폼 초기화
      setFueldirForm({
        name: '',
        factor: 0,
        amount: 0,
        oxyfactor: 1.0000
      });
      setAutoFactorStatus('');

    } catch (error: any) {
      console.error('❌ 연료직접배출량 계산 실패:', error);
      alert(`연료직접배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsCalculating(false);
    }
  }, [fueldirForm]);

  // ============================================================================
  // ✏️ 수정 기능
  // ============================================================================

  const startEditing = useCallback((result: InputResult) => {
    setEditingResult(result);
    setEditForm({
      name: result.name,
      factor: result.factor,
      amount: result.amount,
      oxyfactor: result.oxyfactor
    });
  }, []);

  const cancelEditing = useCallback(() => {
    setEditingResult(null);
    setEditForm({
      name: '',
      factor: 0,
      amount: 0,
      oxyfactor: 1.0000
    });
  }, []);

  const saveEdit = useCallback(async () => {
    if (!editingResult || !selectedProcess?.id) return;
    
    try {
      const endpoint = editingResult.type === 'matdir' 
        ? apiEndpoints.cbam.matdir.update 
        : apiEndpoints.cbam.fueldir.update;
      
      const actualId = Number(editingResult.id);
      
      if (editingResult.type === 'matdir') {
        const updateData = {
          mat_name: editForm.name,
          mat_factor: editForm.factor,
          mat_amount: editForm.amount,
          oxyfactor: editForm.oxyfactor
        };
        await axiosClient.put(endpoint(actualId), updateData);
      } else {
        const updateData = {
          fuel_name: editForm.name,
          fuel_factor: editForm.factor,
          fuel_amount: editForm.amount,
          fuel_oxyfactor: editForm.oxyfactor
        };
        await axiosClient.put(endpoint(actualId), updateData);
      }

      // 결과 목록 업데이트
      setInputResults(prev => prev.map(result => 
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
  // 🗑️ 삭제 기능
  // ============================================================================

  const deleteResult = useCallback(async (result: InputResult) => {
    if (!selectedProcess?.id) return;
    
    if (!confirm('정말로 이 결과를 삭제하시겠습니까?')) return;
    
    try {
      const endpoint = result.type === 'matdir' 
        ? apiEndpoints.cbam.matdir.delete 
        : apiEndpoints.cbam.fueldir.delete;
      
      const actualId = Number(result.id);
      await axiosClient.delete(endpoint(actualId));
      
      // 결과 목록에서 제거
      setInputResults(prev => prev.filter(r => r.id !== result.id));
      alert('삭제가 완료되었습니다!');
      
    } catch (error: any) {
      console.error('❌ 결과 삭제 실패:', error);
      alert(`삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess?.id]);

  // ============================================================================
  // 💾 저장 기능
  // ============================================================================

  const saveAllData = useCallback(async () => {
    if (!selectedProcess || inputResults.length === 0) {
      alert('저장할 데이터가 없습니다.');
      return;
    }

    try {
      console.log('💾 저장 시작:', {
        process_id: selectedProcess.id,
        results: inputResults
      });

      // 이미 DB에 저장된 데이터는 건너뛰기
      const newResults = inputResults.filter(result => !result.created_at);
      
      if (newResults.length === 0) {
        alert('모든 데이터가 이미 저장되어 있습니다.');
        return;
      }

      const savePromises = newResults.map((result, index) => {
        if (result.type === 'matdir') {
          const requestData = {
            process_id: selectedProcess.id,
            mat_name: result.name,
            mat_factor: result.factor,
            mat_amount: result.amount,
            oxyfactor: result.oxyfactor
          };
          return axiosClient.post(apiEndpoints.cbam.matdir.create, requestData);
        } else {
          const requestData = {
            process_id: selectedProcess.id,
            fuel_name: result.name,
            fuel_factor: result.factor,
            fuel_amount: result.amount,
            fuel_oxyfactor: result.oxyfactor
          };
          return axiosClient.post(apiEndpoints.cbam.fueldir.create, requestData);
        }
      });

      const responses = await Promise.all(savePromises);
      console.log('✅ 데이터 저장 성공:', responses);
      
      // 자동 집계: 해당 공정의 직접귀속배출량 계산
      try {
        const aggregationResponse = await axiosClient.post(
          apiEndpoints.cbam.calculation.process.attrdir(selectedProcess.id)
        );
        console.log('✅ 자동 집계 성공:', aggregationResponse.data);
      } catch (aggregationError: any) {
        console.warn('⚠️ 자동 집계 실패:', aggregationError);
      }
      
      alert('모든 데이터가 성공적으로 저장되었습니다!');
      
      // 저장 후 기존 데이터 다시 로드
      await loadAllExistingData();
      
      // 부모 컴포넌트에 데이터 저장 완료 알림
      if (onDataSaved) {
        onDataSaved();
      }
      
    } catch (error: any) {
      console.error('❌ 데이터 저장 실패:', error);
      alert(`데이터 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess, inputResults, loadAllExistingData]);

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
            📊 투입량 입력 - {selectedProcess?.process_name}
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
          <button
            onClick={() => setActiveTab('matdir')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'matdir'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            원료직접배출량
          </button>
          <button
            onClick={() => setActiveTab('fueldir')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'fueldir'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            연료직접배출량
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 왼쪽: 입력 폼 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">
                {activeTab === 'matdir' ? '원료' : '연료'} | 공정 배출 활동량
              </h4>
              <button className="text-blue-400 hover:text-blue-300">+</button>
            </div>

            {activeTab === 'matdir' ? (
              // 원료직접배출량 입력 폼
              <div className="space-y-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    투입된 원료명
                    <span className="text-xs text-gray-400 ml-2">(자유 입력 가능)</span>
                  </label>
                  <input
                    type="text"
                    value={matdirForm.name}
                    onChange={(e) => handleMatdirNameChange(e.target.value)}
                    onBlur={handleMatdirNameBlur}
                    className="w-full px-3 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="예: 직접환원철, EAF 탄소 전극"
                  />
                  
                  {materialAutoFactorStatus && (
                    <div className={`mt-1 text-xs ${
                      materialAutoFactorStatus.includes('✅') ? 'text-green-400' : 
                      materialAutoFactorStatus.includes('⚠️') ? 'text-yellow-400' : 
                      'text-blue-400'
                    }`}>
                      {materialAutoFactorStatus}
                    </div>
                  )}

                  {showMaterialSuggestions && materialSuggestions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-md shadow-lg max-h-40 overflow-y-auto">
                      {materialSuggestions.map((material, index) => (
                        <button
                          key={material.id || index}
                          onClick={() => handleMaterialSelect(material)}
                          className="w-full px-3 py-2 text-left text-white hover:bg-gray-600 focus:bg-gray-600 focus:outline-none"
                        >
                          <div className="font-medium">{material.mat_name || material.name}</div>
                          <div className="text-xs text-gray-400">배출계수 자동 설정</div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    배출계수 {matdirForm.factor > 0 && <span className="text-green-400">(Master Table 자동 설정)</span>}
                    <span className="text-xs text-red-400 ml-2">(수정 불가)</span>
                  </label>
                  <input
                    type="number"
                    step="0.000001"
                    min="0"
                    value={matdirForm.factor}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-500 border border-gray-400 rounded-md text-gray-300 cursor-not-allowed"
                    placeholder="Master Table에서 자동 설정됨"
                  />
                  <div className="text-xs text-gray-400 mt-1">
                    💡 배출계수는 Master Table의 값만 사용 가능합니다
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">투입된 원료량</label>
                  <input
                    type="number"
                    step="0.000001"
                    min="0"
                    value={matdirForm.amount}
                    onChange={(e) => setMatdirForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.000000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">산화계수</label>
                  <input
                    type="number"
                    step="0.0001"
                    min="0"
                    value={matdirForm.oxyfactor}
                    onChange={(e) => setMatdirForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1.0000 }))}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="1.0000"
                  />
                </div>

                <button
                  onClick={calculateMatdirEmission}
                  disabled={isCalculating}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  {isCalculating ? '계산 중...' : '🧮 원료직접배출량 계산'}
                </button>
              </div>
            ) : (
              // 연료직접배출량 입력 폼
              <div className="space-y-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    투입된 연료명
                    <span className="text-xs text-gray-400 ml-2">(자유 입력 가능)</span>
                  </label>
                  <input
                    type="text"
                    value={fueldirForm.name}
                    onChange={(e) => handleFueldirNameChange(e.target.value)}
                    onBlur={handleFueldirNameBlur}
                    className="w-full px-3 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="예: 원유, 휘발유, 등유"
                  />
                  
                  {autoFactorStatus && (
                    <div className={`mt-1 text-xs ${
                      autoFactorStatus.includes('✅') ? 'text-green-400' : 
                      autoFactorStatus.includes('⚠️') ? 'text-yellow-400' : 
                      'text-blue-400'
                    }`}>
                      {autoFactorStatus}
                    </div>
                  )}

                  {showSuggestions && fuelSuggestions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-md shadow-lg max-h-40 overflow-y-auto">
                      {fuelSuggestions.map((fuel) => (
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

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    배출계수 {fueldirForm.factor > 0 && <span className="text-green-400">(Master Table 자동 설정)</span>}
                    <span className="text-xs text-red-400 ml-2">(수정 불가)</span>
                  </label>
                  <input
                    type="number"
                    step="0.000001"
                    min="0"
                    value={fueldirForm.factor}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-500 border border-gray-400 rounded-md text-gray-300 cursor-not-allowed"
                    placeholder="Master Table에서 자동 설정됨"
                  />
                  <div className="text-xs text-gray-400 mt-1">
                    💡 배출계수는 Master Table의 값만 사용 가능합니다
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">투입된 연료량</label>
                  <input
                    type="number"
                    step="0.000001"
                    min="0"
                    value={fueldirForm.amount}
                    onChange={(e) => setFueldirForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.000000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">산화계수</label>
                  <input
                    type="number"
                    step="0.0001"
                    min="0"
                    value={fueldirForm.oxyfactor}
                    onChange={(e) => setFueldirForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1.0000 }))}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="1.0000"
                  />
                </div>

                <button
                  onClick={calculateFueldirEmission}
                  disabled={isCalculating}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  {isCalculating ? '계산 중...' : '🧮 연료직접배출량 계산'}
                </button>
              </div>
            )}
          </div>

          {/* 오른쪽: 입력된 목록 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">입력된 목록</h4>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">{inputResults.length}개</span>
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
            ) : inputResults.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                입력된 데이터가 없습니다.
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {inputResults.map((result) => (
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
                            value={editForm.name}
                            onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                            className="px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white text-sm"
                            placeholder="이름"
                          />
                          <input
                            type="number"
                            step="0.000001"
                            value={editForm.amount}
                            onChange={(e) => setEditForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                            className="px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white text-sm"
                            placeholder="수량"
                          />
                          <input
                            type="number"
                            step="0.000001"
                            value={editForm.factor}
                            readOnly
                            className="px-2 py-1 bg-gray-600 border border-gray-400 rounded text-gray-400 text-sm cursor-not-allowed"
                            placeholder="배출계수 (수정불가)"
                            title="배출계수는 Master Table의 값만 사용 가능합니다"
                          />
                          <input
                            type="number"
                            step="0.0001"
                            value={editForm.oxyfactor}
                            onChange={(e) => setEditForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1.0000 }))}
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
                            <h5 className="font-medium text-white">{result.name}</h5>
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
                            <div>배출계수: {result.factor}</div>
                            <div>수량: {result.amount}</div>
                            <div>산화계수: {result.oxyfactor}</div>
                            <div className="font-medium text-green-400">
                              배출량: {result.emission}
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

            {inputResults.length > 0 && (
              <button
                onClick={saveAllData}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors mt-4"
              >
                💾 모든 데이터 저장
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
