'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axiosClient from '@/lib/axiosClient';
import { apiEndpoints } from '@/lib/axiosClient';

interface ProcessInput {
  id: number;
  process_id: number;
  input_type: string;
  input_name: string;
  amount: number;
  factor?: number;
  oxy_factor?: number;
  direm_emission?: number;
  indirem_emission?: number;
  created_at?: string;
  updated_at?: string;
}

interface Process {
  id: number;
  process_name: string;
  product_id: number;
}

interface ProcessInputForm {
  process_id: number;
  input_type: string;
  input_name: string;
  amount: number;
  factor: number;
  oxy_factor: number;
}

export default function ProcessInputPage() {
  const router = useRouter();
  const searchParams = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '');
  const processIdFromUrl = searchParams.get('process_id');
  
  const [processInputs, setProcessInputs] = useState<ProcessInput[]>([]);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [sortBy, setSortBy] = useState<'input_name' | 'input_type' | 'amount' | 'process_id'>('input_name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [selectedProcessId, setSelectedProcessId] = useState<number>(processIdFromUrl ? parseInt(processIdFromUrl) : 0);

  const [processInputForm, setProcessInputForm] = useState<ProcessInputForm>({
    process_id: 0,
    input_type: 'material',
    input_name: '',
    amount: 0,
    factor: 0,
    oxy_factor: 1.0
  });

  // 프로세스 입력 목록 조회
  const fetchProcessInputs = async () => {
    try {
      setIsLoading(true);
      const response = await axiosClient.get(apiEndpoints.cbam.processInput.list);
      setProcessInputs(response.data);
      console.log('📋 프로세스 입력 목록:', response.data);
    } catch (error: any) {
      console.error('❌ 프로세스 입력 목록 조회 실패:', error);
      setToast({
        message: `프로세스 입력 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 프로세스 목록 조회
  const fetchProcesses = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      setProcesses(response.data);
      console.log('📋 프로세스 목록:', response.data);
    } catch (error: any) {
      console.error('❌ 프로세스 목록 조회 실패:', error);
    }
  };

  useEffect(() => {
    fetchProcessInputs();
    fetchProcesses();
    
    // URL에서 process_id가 있으면 해당 프로세스로 설정
    if (processIdFromUrl) {
      setSelectedProcessId(parseInt(processIdFromUrl));
    }
  }, [processIdFromUrl]);

  // 프로세스명 조회 헬퍼 함수
  const getProcessName = (processId: number) => {
    const process = processes.find(p => p.id === processId);
    return process ? process.process_name : `프로세스 ID: ${processId}`;
  };

  const handleInputChange = (field: keyof ProcessInputForm, value: string | number) => {
    setProcessInputForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!processInputForm.process_id || !processInputForm.input_name || processInputForm.amount <= 0) {
      setToast({
        message: '필수 필드를 모두 입력해주세요.',
        type: 'error'
      });
      return;
    }

    try {
      const response = await axiosClient.post(apiEndpoints.cbam.processInput.create, processInputForm);
      console.log('✅ 프로세스 입력 생성 성공:', response.data);
      
      setToast({
        message: '프로세스 입력이 성공적으로 생성되었습니다.',
        type: 'success'
      });

      // 폼 초기화
      setProcessInputForm({
        process_id: 0,
        input_type: 'material',
        input_name: '',
        amount: 0,
        factor: 0,
        oxy_factor: 1.0
      });

      // 목록 새로고침
      fetchProcessInputs();
    } catch (error: any) {
      console.error('❌ 프로세스 입력 생성 실패:', error);
      setToast({
        message: `프로세스 입력 생성에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleDeleteProcessInput = async (id: number, inputName: string) => {
    if (!confirm(`"${inputName}" 프로세스 입력을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await axiosClient.delete(apiEndpoints.cbam.processInput.delete(id));
      console.log('✅ 프로세스 입력 삭제 성공');
      
      setToast({
        message: '프로세스 입력이 성공적으로 삭제되었습니다.',
        type: 'success'
      });

      fetchProcessInputs();
    } catch (error: any) {
      console.error('❌ 프로세스 입력 삭제 실패:', error);
      setToast({
        message: `프로세스 입력 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleCalculateEmission = async (processId: number) => {
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.emission.calculateProcess(processId));
      console.log('✅ 배출량 계산 성공:', response.data);
      
      setToast({
        message: `배출량 계산이 완료되었습니다. 총 배출량: ${response.data.total_emission.toFixed(2)}`,
        type: 'success'
      });

      fetchProcessInputs(); // 배출량이 업데이트되었으므로 목록 새로고침
    } catch (error: any) {
      console.error('❌ 배출량 계산 실패:', error);
      setToast({
        message: `배출량 계산에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  // 정렬된 프로세스 입력 목록
  const sortedProcessInputs = [...processInputs].sort((a, b) => {
    let aValue: any, bValue: any;
    
    switch (sortBy) {
      case 'input_name':
        aValue = a.input_name.toLowerCase();
        bValue = b.input_name.toLowerCase();
        break;
      case 'input_type':
        aValue = a.input_type;
        bValue = b.input_type;
        break;
      case 'amount':
        aValue = parseFloat(a.amount.toString()) || 0;
        bValue = parseFloat(b.amount.toString()) || 0;
        break;
      case 'process_id':
        aValue = a.process_id;
        bValue = b.process_id;
        break;
      default:
        return 0;
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  // 필터링된 프로세스 입력 목록
  const filteredProcessInputs = selectedProcessId > 0 
    ? sortedProcessInputs.filter(input => input.process_id === selectedProcessId)
    : sortedProcessInputs;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">📥 프로세스 입력 관리</h1>
          <p className="text-gray-300">
            CBAM 프로세스별 입력 데이터를 관리하고 배출량을 계산합니다.
          </p>
        </div>

        {/* 토스트 메시지 */}
        {toast && (
          <div className={`mb-4 p-4 rounded-lg ${
            toast.type === 'success' ? 'bg-green-600' : 
            toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
          }`}>
            {toast.message}
          </div>
        )}

        {/* 프로세스 입력 생성 폼 */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">📝 프로세스 입력 생성</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">프로세스 선택</label>
              <select
                value={processInputForm.process_id}
                onChange={(e) => handleInputChange('process_id', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value={0}>프로세스를 선택하세요</option>
                {processes.map(process => (
                  <option key={process.id} value={process.id}>
                    {process.process_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">입력 타입</label>
              <select
                value={processInputForm.input_type}
                onChange={(e) => handleInputChange('input_type', e.target.value)}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="material">원료 (Material)</option>
                <option value="fuel">연료 (Fuel)</option>
                <option value="electricity">전력 (Electricity)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">입력명</label>
              <input
                type="text"
                value={processInputForm.input_name}
                onChange={(e) => handleInputChange('input_name', e.target.value)}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="예: 석탄, 전력, 철광석"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">수량</label>
              <input
                type="number"
                step="0.01"
                value={processInputForm.amount}
                onChange={(e) => handleInputChange('amount', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">배출계수</label>
              <input
                type="number"
                step="0.0001"
                value={processInputForm.factor}
                onChange={(e) => handleInputChange('factor', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.0000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">산화계수</label>
              <input
                type="number"
                step="0.01"
                value={processInputForm.oxy_factor}
                onChange={(e) => handleInputChange('oxy_factor', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1.00"
              />
            </div>

            <div className="md:col-span-2 lg:col-span-3">
              <button
                type="submit"
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200"
              >
                📥 프로세스 입력 생성
              </button>
            </div>
          </form>
        </div>

        {/* 필터 및 정렬 */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex gap-4 items-center">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">프로세스 필터</label>
                <select
                  value={selectedProcessId}
                  onChange={(e) => setSelectedProcessId(parseInt(e.target.value))}
                  className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={0}>모든 프로세스</option>
                  {processes.map(process => (
                    <option key={process.id} value={process.id}>
                      {process.process_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">정렬 기준</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="input_name">입력명순</option>
                  <option value="input_type">타입순</option>
                  <option value="amount">수량순</option>
                  <option value="process_id">프로세스순</option>
                </select>
              </div>

              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-3 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-md text-white text-sm transition-colors duration-200"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            <button
              onClick={fetchProcessInputs}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors duration-200"
            >
              🔄 새로고침
            </button>
          </div>
        </div>

        {/* 프로세스 입력 목록 */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h2 className="text-xl font-semibold text-white mb-4">📋 프로세스 입력 목록</h2>
          
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-300 mt-4">데이터를 불러오는 중...</p>
            </div>
          ) : filteredProcessInputs.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-300">등록된 프로세스 입력이 없습니다.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredProcessInputs.map((processInput) => (
                <div key={processInput.id} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-white font-semibold text-lg">{processInput.input_name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      processInput.input_type === 'material' ? 'bg-blue-500/20 text-blue-300' :
                      processInput.input_type === 'fuel' ? 'bg-red-500/20 text-red-300' :
                      'bg-green-500/20 text-green-300'
                    }`}>
                      {processInput.input_type}
                    </span>
                  </div>
                  
                  {/* 프로세스 정보 */}
                  <div className="mb-3">
                    <div className="text-sm text-gray-300">
                      🔄 {getProcessName(processInput.process_id)}
                    </div>
                  </div>

                  <div className="space-y-1 mb-3">
                    <p className="text-gray-300 text-sm">수량: {processInput.amount.toLocaleString()}</p>
                    {processInput.factor && <p className="text-gray-300 text-sm">배출계수: {processInput.factor}</p>}
                    {processInput.oxy_factor && <p className="text-gray-300 text-sm">산화계수: {processInput.oxy_factor}</p>}
                    {processInput.direm_emission && <p className="text-green-300 text-sm">직접배출: {processInput.direm_emission.toFixed(2)}</p>}
                    {processInput.indirem_emission && <p className="text-blue-300 text-sm">간접배출: {processInput.indirem_emission.toFixed(2)}</p>}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleCalculateEmission(processInput.process_id)}
                      className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                    >
                      🧮 배출량 계산
                    </button>
                    <button
                      onClick={() => handleDeleteProcessInput(processInput.id, processInput.input_name)}
                      className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 디버그 정보 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">🔍 디버그 정보</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white/10 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">{processes.length}</div>
              <div className="text-sm text-gray-300">등록된 프로세스</div>
            </div>
            <div className="p-4 bg-white/10 rounded-lg">
              <div className="text-2xl font-bold text-green-400">{processInputs.length}</div>
              <div className="text-sm text-gray-300">등록된 프로세스 입력</div>
            </div>
            <div className="p-4 bg-white/10 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">
                {processInputs.filter(pi => pi.direm_emission || pi.indirem_emission).length}
              </div>
              <div className="text-sm text-gray-300">배출량 계산 완료</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
