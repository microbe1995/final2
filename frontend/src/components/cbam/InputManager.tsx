'use client';

import React, { useState, useCallback, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useFuelMasterAPI } from '@/hooks/useFuelMasterAPI';
import { useMaterialMasterAPI } from '@/hooks/useMaterialMasterAPI';
import { useDummyData } from '@/hooks/useDummyData';

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
  const { getFuelFactor, searchFuels } = useFuelMasterAPI();
  const { autoMapMaterialFactor } = useMaterialMasterAPI();
  const { getMaterialsFor, getFuelsFor } = useDummyData();

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

  // Material Master 자동 배출계수 관련 상태 (이제 사용 최소화)
  const [materialSuggestions, setMaterialSuggestions] = useState<any[]>([]);
  const [showMaterialSuggestions, setShowMaterialSuggestions] = useState(false);
  const [materialAutoFactorStatus, setMaterialAutoFactorStatus] = useState<string>('');

  // Dummy 기반 원료 옵션
  const [materialOptions, setMaterialOptions] = useState<{ name: string; amount: number; unit: string }[]>([]);
  const [fuelOptions, setFuelOptions] = useState<{ name: string; amount: number; unit: string }[]>([]);

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
      
    } catch (error: any) {
      // no-op
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
  // 🔧 원료직접배출량 관련 함수들 (입력 → 드롭다운 선택 방식)
  // ============================================================================

  const handleMatdirNameChange = useCallback(async (name: string) => {
    // 선택한 항목이 연료(Fuel Master 매칭)인지 확인 → 연료면 자동 매핑 금지
    let isFuel = false;
    try {
      const suggestions = await searchFuels(name);
      isFuel = Array.isArray(suggestions) && suggestions.length > 0;
    } catch {
      isFuel = false;
    }

    if (isFuel) {
      // 연료는 원료 탭에서 자동반영 금지
      setMatdirForm(prev => ({ ...prev, name, factor: 0, amount: 0, oxyfactor: 1.0000 }));
      setMaterialAutoFactorStatus(`⚠️ '${name}'은(는) 연료로 분류되어 원료 탭에서는 자동 설정되지 않습니다.`);
      return;
    }

    // 원료: 배출계수 매칭 성공 시에만 더미에서 수량 자동 설정
    const matched = materialOptions.find(opt => opt.name === name);
    // 우선 이름/산화계수만 적용, 수량은 보류
    setMatdirForm(prev => ({
      ...prev,
      name,
      amount: 0,
      oxyfactor: 1.0000,
    }));
    try {
      const factor = await autoMapMaterialFactor(name);
      if (factor !== null) {
        // 배출계수 매칭 성공 → 이때만 더미 수량을 반영
        const amountFromDummy = matched ? Number(matched.amount) || 0 : 0;
        setMatdirForm(prev => ({ ...prev, factor, amount: amountFromDummy }));
        setMaterialAutoFactorStatus(`✅ 자동 설정: ${name} (배출계수: ${factor})`);
      } else {
        // 매칭 실패 → 수량 자동 로딩 금지(0 유지)
        setMatdirForm(prev => ({ ...prev, factor: 0, amount: 0 }));
        setMaterialAutoFactorStatus(`⚠️ 배출계수를 찾을 수 없음: ${name}. 수량 자동설정이 비활성화됩니다.`);
      }
    } catch {
      setMatdirForm(prev => ({ ...prev, factor: 0, amount: 0 }));
      setMaterialAutoFactorStatus(`❌ 배출계수 조회 실패: ${name}`);
    }
  }, [materialOptions, autoMapMaterialFactor, searchFuels]);

  const handleMatdirNameBlur = useCallback(async () => {
    // 드롭다운 선택이므로 blur 시 추가 조회 없음
  }, []);

  const handleMaterialSelect = useCallback((opt: { name: string; amount: number; unit: string }) => {
    setMatdirForm(prev => ({ ...prev, name: opt.name }));
  }, []);

  // 선택된 공정/기간/제품명 기준으로 더미 원료 옵션 로드
  useEffect(() => {
    (async () => {
      if (!selectedProcess) return;
      try {
        const processName = selectedProcess?.process_name || selectedProcess?.processData?.process_name || selectedProcess?.label;
        const startDate = selectedProcess?.start_period || selectedProcess?.processData?.start_period || selectedProcess?.startDate;
        const endDate = selectedProcess?.end_period || selectedProcess?.processData?.end_period || selectedProcess?.endDate;
        const productNames: string[] | undefined = selectedProcess?.product_names
          ? String(selectedProcess.product_names).split(',').map((s: string) => s.trim()).filter(Boolean)
          : undefined;
        const options = await getMaterialsFor({ processName, startDate, endDate, productNames });
        setMaterialOptions(options);
      } catch {
        setMaterialOptions([]);
      }
    })();
  }, [selectedProcess, getMaterialsFor]);

  // 선택된 공정/기간/제품명 기준으로 더미 연료 옵션 로드
  useEffect(() => {
    (async () => {
      if (!selectedProcess) return;
      try {
        const processName = selectedProcess?.process_name || selectedProcess?.processData?.process_name || selectedProcess?.label;
        const startDate = selectedProcess?.start_period || selectedProcess?.processData?.start_period || selectedProcess?.startDate;
        const endDate = selectedProcess?.end_period || selectedProcess?.processData?.end_period || selectedProcess?.endDate;
        const productNames: string[] | undefined = selectedProcess?.product_names
          ? String(selectedProcess.product_names).split(',').map((s: string) => s.trim()).filter(Boolean)
          : undefined;
        const options = await getFuelsFor({ processName, startDate, endDate, productNames });
        setFuelOptions(options);
      } catch {
        setFuelOptions([]);
      }
    })();
  }, [selectedProcess, getFuelsFor]);

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

      // 결과를 목록에 추가
      const newResult: InputResult = {
        id: Date.now(),
        name: matdirForm.name,
        factor: matdirForm.factor,
        amount: matdirForm.amount,
        oxyfactor: matdirForm.oxyfactor,
        emission: calculationResult.matdir_em,
        calculation_formula: calculationResult.calculation_formula,
        type: 'matdir'
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
      alert(`원료직접배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsCalculating(false);
    }
  }, [matdirForm]);

  // ============================================================================
  // ⛽ 연료직접배출량: 더미 기반 드롭다운 + Master에서 배출계수 자동 설정
  // ============================================================================

  const handleFuelDropdownChange = useCallback(async (name: string) => {
    // 선택된 연료명 반영
    setFueldirForm(prev => ({ ...prev, name }));
    if (!name) return;

    // 더미 연료 옵션에서 동일 이름의 기본 투입량을 자동 설정 (원료 로직과 동일)
    const matched = fuelOptions.find(opt => opt.name === name);
    if (matched) {
      setFueldirForm(prev => ({ ...prev, amount: Number(matched.amount) || 0, oxyfactor: 1.0000 }));
    } else {
      setFueldirForm(prev => ({ ...prev, amount: 0, oxyfactor: 1.0000 }));
    }

    // Fuel Master에서 배출계수 자동 조회
    try {
      const factorResponse = await getFuelFactor(name);
      if (factorResponse && factorResponse.found && factorResponse.fuel_factor !== null) {
        const factor = factorResponse.fuel_factor;
        setFueldirForm(prev => ({ ...prev, factor }));
      }
    } catch {
      // no-op: 자동 설정 실패 시 사용자 입력 대기
    }
  }, [fuelOptions, getFuelFactor]);

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

      const newResult: InputResult = {
        id: Date.now(),
        name: fueldirForm.name,
        factor: fueldirForm.factor,
        amount: fueldirForm.amount,
        oxyfactor: fueldirForm.oxyfactor,
        emission: calculationResult.fueldir_em,
        calculation_formula: calculationResult.calculation_formula,
        type: 'fueldir'
      };

      setInputResults(prev => [newResult, ...prev]);

      setFueldirForm({ name: '', factor: 0, amount: 0, oxyfactor: 1.0000 });

    } catch (error: any) {
      alert(`연료직접배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsCalculating(false);
    }
  }, [fueldirForm]);

  // =========================================================================
  // ✏️ 수정/삭제/저장 함수들 (이하 동일)
  // =========================================================================

  const startEditing = useCallback((result: InputResult) => {
    setEditingResult(result);
    setEditForm({ name: result.name, factor: result.factor, amount: result.amount, oxyfactor: result.oxyfactor });
  }, []);

  const cancelEditing = useCallback(() => {
    setEditingResult(null);
    setEditForm({ name: '', factor: 0, amount: 0, oxyfactor: 1.0000 });
  }, []);

  const saveEdit = useCallback(async () => {
    if (!editingResult || !selectedProcess?.id) return;
    try {
      const endpoint = editingResult.type === 'matdir' ? apiEndpoints.cbam.matdir.update : apiEndpoints.cbam.fueldir.update;
      const actualId = Number(editingResult.id);
      if (editingResult.type === 'matdir') {
        const updateData = { mat_name: editForm.name, mat_factor: editForm.factor, mat_amount: editForm.amount, oxyfactor: editForm.oxyfactor };
        await axiosClient.put(endpoint(actualId), updateData);
      } else {
        const updateData = { fuel_name: editForm.name, fuel_factor: editForm.factor, fuel_amount: editForm.amount, fuel_oxyfactor: editForm.oxyfactor };
        await axiosClient.put(endpoint(actualId), updateData);
      }
      setInputResults(prev => prev.map(r => (r.id === editingResult.id ? { ...r, ...editForm, updated_at: new Date().toISOString() } : r)));
      try { await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(selectedProcess.id)); } catch {}
      setEditingResult(null);
      alert('수정이 완료되었습니다!');
      if (onDataSaved) onDataSaved();
    } catch (error: any) {
      alert(`수정에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [editingResult, editForm, selectedProcess?.id]);

  const deleteResult = useCallback(async (result: InputResult) => {
    if (!selectedProcess?.id) return;
    if (!confirm('정말로 이 결과를 삭제하시겠습니까?')) return;
    try {
      if (!result.created_at) {
        setInputResults(prev => prev.filter(r => r.id !== result.id));
        return;
      }
      const endpoint = result.type === 'matdir' ? apiEndpoints.cbam.matdir.delete : apiEndpoints.cbam.fueldir.delete;
      const actualId = Number(result.id);
      await axiosClient.delete(endpoint(actualId));
      setInputResults(prev => prev.filter(r => r.id !== result.id));
      alert('삭제가 완료되었습니다!');
      try { await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(selectedProcess.id)); } catch {}
      if (onDataSaved) onDataSaved();
    } catch (error: any) {
      alert(`삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess?.id]);

  const saveAllData = useCallback(async () => {
    if (!selectedProcess || inputResults.length === 0) {
      alert('저장할 데이터가 없습니다.');
      return;
    }
    try {
      const newResults = inputResults.filter(result => !result.created_at);
      if (newResults.length === 0) {
        alert('모든 데이터가 이미 저장되어 있습니다.');
        return;
      }
      const savePromises = newResults.map((result) => {
        if (result.type === 'matdir') {
          const requestData = { process_id: selectedProcess.id, mat_name: result.name, mat_factor: result.factor, mat_amount: result.amount, oxyfactor: result.oxyfactor };
          return axiosClient.post(apiEndpoints.cbam.matdir.create, requestData);
        } else {
          const requestData = { process_id: selectedProcess.id, fuel_name: result.name, fuel_factor: result.factor, fuel_amount: result.amount, fuel_oxyfactor: result.oxyfactor };
          return axiosClient.post(apiEndpoints.cbam.fueldir.create, requestData);
        }
      });
      await Promise.all(savePromises);
      try { await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(selectedProcess.id)); } catch {}
      alert('모든 데이터가 성공적으로 저장되었습니다!');
      await loadAllExistingData();
      if (onDataSaved) onDataSaved();
    } catch (error: any) {
      alert(`데이터 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    }
  }, [selectedProcess, inputResults, loadAllExistingData]);

  // 날짜 포맷팅 함수
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-6xl mx-4 shadow-2xl">
        {/* 모달 헤더 */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-white">📊 투입량 입력 - {selectedProcess?.process_name}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl transition-colors">×</button>
        </div>

        {/* 탭 네비게이션 */}
        <div className="mb-6 flex gap-2 border-b border-gray-700">
          <button onClick={() => setActiveTab('matdir')} className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'matdir' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}>원료직접배출량</button>
          <button onClick={() => setActiveTab('fueldir')} className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'fueldir' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}>연료직접배출량</button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 왼쪽: 입력 폼 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">{activeTab === 'matdir' ? '원료' : '연료'} | 공정 배출 활동량</h4>
              <button className="text-blue-400 hover:text-blue-300">+</button>
            </div>

            {activeTab === 'matdir' ? (
              <div className="space-y-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-300 mb-2">투입된 원료명</label>
                  <select
                    value={matdirForm.name}
                    onChange={(e) => handleMatdirNameChange(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800/60 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:border-blue-500"
                  >
                    <option value="">원료를 선택하세요</option>
                    {materialOptions.map((opt) => (
                      <option key={opt.name} value={opt.name}>
                        {opt.name} {opt.unit ? `(${opt.unit})` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                {/* 이하 기존 입력 필드 유지 */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">배출계수 <span className="text-xs text-red-400 ml-2">(수정 불가)</span></label>
                  <input type="number" step="0.000001" min="0" value={matdirForm.factor} readOnly className="w-full px-3 py-2 bg-gray-500 border border-gray-400 rounded-md text-gray-300 cursor-not-allowed" placeholder="Master Table에서 자동 설정됨" />
                  <div className="text-xs text-gray-400 mt-1">💡 배출계수는 원료 선택 시 자동 설정됩니다</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">투입된 원료량 <span className="text-xs text-red-400 ml-2">(수정 불가)</span></label>
                  <input type="number" step="0.000001" min="0" value={matdirForm.amount} readOnly className="w-full px-3 py-2 bg-gray-500 border border-gray-400 rounded-md text-gray-300 cursor-not-allowed" placeholder="원료 선택 시 자동 설정" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">산화계수</label>
                  <input type="number" step="0.0001" min="0" value={matdirForm.oxyfactor} onChange={(e) => setMatdirForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1.0000 }))} className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="1.0000" />
                </div>
                <button onClick={calculateMatdirEmission} disabled={isCalculating} className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors">{isCalculating ? '계산 중...' : '🧮 원료직접배출량 계산'}</button>
              </div>
            ) : (
              // 연료직접배출량: 더미 기반 드롭다운 선택
              <div className="space-y-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-300 mb-2">투입된 연료명</label>
                  <select
                    value={fueldirForm.name}
                    onChange={(e) => handleFuelDropdownChange(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800/60 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:border-blue-500"
                  >
                    <option value="">연료를 선택하세요</option>
                    {fuelOptions.map((opt) => (
                      <option key={opt.name} value={opt.name}>
                        {opt.name} {opt.unit ? `(${opt.unit})` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">배출계수 <span className="text-xs text-red-400 ml-2">(수정 불가)</span></label>
                  <input type="number" step="0.000001" min="0" value={fueldirForm.factor} readOnly className="w-full px-3 py-2 bg-gray-500 border border-gray-400 rounded-md text-gray-300 cursor-not-allowed" placeholder="Master Table에서 자동 설정됨" />
                  <div className="text-xs text-gray-400 mt-1">💡 배출계수는 Master Table의 값만 사용 가능합니다</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">투입된 연료량 <span className="text-xs text-red-400 ml-2">(수정 불가)</span></label>
                  <input type="number" step="0.000001" min="0" value={fueldirForm.amount} readOnly className="w-full px-3 py-2 bg-gray-500 border border-gray-400 rounded-md text-gray-300 cursor-not-allowed" placeholder="연료 선택 시 자동 설정" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">산화계수</label>
                  <input type="number" step="0.0001" min="0" value={fueldirForm.oxyfactor} onChange={(e) => setFueldirForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1.0000 }))} className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="1.0000" />
                </div>
                <button onClick={calculateFueldirEmission} disabled={isCalculating} className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors">{isCalculating ? '계산 중...' : '🧮 연료직접배출량 계산'}</button>
              </div>
            )}
          </div>

          {/* 오른쪽: 입력된 목록 */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-medium text-white">입력된 목록</h4>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">{inputResults.length}개</span>
                <button onClick={loadAllExistingData} disabled={isLoadingData} className="text-blue-400 hover:text-blue-300 text-sm disabled:text-gray-500">{isLoadingData ? '로딩 중...' : '🔄 새로고침'}</button>
              </div>
            </div>

            {isLoadingData ? (
              <div className="text-center text-gray-400 py-8">데이터를 불러오는 중...</div>
            ) : inputResults.length === 0 ? (
              <div className="text-center text-gray-400 py-8">입력된 데이터가 없습니다.</div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {inputResults.map((result) => (
                  <div key={result.id} className="bg-gray-600 rounded-lg p-3">
                    {editingResult && editingResult.id === result.id ? (
                      <div className="space-y-2">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs text-gray-300 mb-1">이름</label>
                            <input
                              type="text"
                              className="w-full px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white"
                              value={editForm.name}
                              onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-300 mb-1">배출계수</label>
                            <input
                              type="number"
                              step="0.000001"
                              className="w-full px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white"
                              value={editForm.factor}
                              onChange={(e) => setEditForm(prev => ({ ...prev, factor: parseFloat(e.target.value) || 0 }))}
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-300 mb-1">투입량</label>
                            <input
                              type="number"
                              step="0.000001"
                              className="w-full px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white"
                              value={editForm.amount}
                              onChange={(e) => setEditForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-300 mb-1">산화계수</label>
                            <input
                              type="number"
                              step="0.0001"
                              className="w-full px-2 py-1 bg-gray-700 border border-gray-500 rounded text-white"
                              value={editForm.oxyfactor}
                              onChange={(e) => setEditForm(prev => ({ ...prev, oxyfactor: parseFloat(e.target.value) || 1 }))}
                            />
                          </div>
                        </div>
                        <div className="flex gap-2 justify-end">
                          <button onClick={saveEdit} className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded">저장</button>
                          <button onClick={cancelEditing} className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded">취소</button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className={`text-xs px-2 py-0.5 rounded ${result.type === 'matdir' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' : 'bg-orange-500/20 text-orange-300 border border-orange-500/30'}`}>
                              {result.type === 'matdir' ? '원료직접' : '연료직접'}
                            </span>
                            <span className="text-white font-medium">{result.name}</span>
                          </div>
                          <div className="flex gap-2">
                            <button onClick={() => deleteResult(result)} className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded">삭제</button>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-200">
                          <div className="bg-gray-700 rounded p-2"><div className="text-gray-400">배출계수</div><div className="font-semibold">{result.factor}</div></div>
                          <div className="bg-gray-700 rounded p-2"><div className="text-gray-400">투입량</div><div className="font-semibold">{result.amount}</div></div>
                          <div className="bg-gray-700 rounded p-2"><div className="text-gray-400">산화계수</div><div className="font-semibold">{result.oxyfactor}</div></div>
                          <div className="bg-gray-700 rounded p-2"><div className="text-gray-400">계산결과</div><div className="font-semibold">{typeof result.emission === 'number' ? result.emission.toFixed(6) : result.emission}</div></div>
                        </div>
                        {result.calculation_formula && (
                          <div className="text-[11px] text-gray-300">{result.calculation_formula}</div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {inputResults.length > 0 && (
              <button onClick={saveAllData} className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors mt-4">💾 모든 데이터 저장</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
