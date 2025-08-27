'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useRouter } from 'next/navigation';

// ============================================================================
// 🏭 사업장 관리 페이지
// ============================================================================

interface Install {
  id: number;
  name: string;
  reporting_year: number;
}

interface InstallForm {
  name: string;
  reporting_year: number;
}

export default function InstallPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [installs, setInstalls] = useState<any[]>([]);
  const [isLoadingInstalls, setIsLoadingInstalls] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [sortBy, setSortBy] = useState<'name' | 'id'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [installForm, setInstallForm] = useState<InstallForm>({
    name: '',
    reporting_year: new Date().getFullYear() // 현재 년도로 기본값 설정
  });

  // 사업장 목록 조회
  const fetchInstalls = async () => {
    try {
      setIsLoadingInstalls(true);
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      setInstalls(response.data);
      console.log('📋 사업장 목록:', response.data);
    } catch (error: any) {
      console.error('❌ 사업장 목록 조회 실패:', error);
      setToast({
        message: `사업장 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoadingInstalls(false);
    }
  };

  useEffect(() => {
    fetchInstalls();
  }, []);

  // 사업장 정렬
  const sortedInstalls = [...installs].sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'name':
        aValue = a.name.toLowerCase();
        bValue = b.name.toLowerCase();
        break;
      case 'id':
        aValue = a.id;
        bValue = b.id;
        break;
      default:
        return 0;
    }
    
    if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  const handleInputChange = (field: keyof InstallForm, value: string) => {
    setInstallForm(prev => ({
      ...prev,
      [field]: field === 'reporting_year' ? parseInt(value) || new Date().getFullYear() : value
    }));
  };

  // 사업장 클릭 시 제품 관리 페이지로 이동
  const handleInstallClick = (installId: number) => {
    router.push(`/cbam/install/${installId}/products`);
  };

  // 제품 관리 페이지로 이동
  const handleProductManagement = () => {
    router.push('/cbam/calculation');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 데이터 검증
      if (!installForm.name.trim()) {
        setToast({
          message: '사업장명을 입력해주세요.',
          type: 'error'
        });
        setLoading(false);
        return;
      }

      console.log('📤 사업장 생성 요청 데이터:', installForm);
      
      const response = await axiosClient.post(apiEndpoints.cbam.install.create, installForm);
      
      console.log('✅ 사업장 생성 성공:', response.data);
      
      setToast({
        message: '사업장이 성공적으로 생성되었습니다!',
        type: 'success'
      });

      // 폼 초기화
      setInstallForm({
        name: '',
        reporting_year: new Date().getFullYear()
      });

      // 사업장 목록 새로고침
      await fetchInstalls();

    } catch (error: any) {
      console.error('❌ 사업장 생성 실패:', error);
      
      setToast({
        message: `사업장 생성에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // 사업장 삭제
  const handleDeleteInstall = async (id: number, name: string) => {
    if (!confirm(`"${name}" 사업장을 삭제하시겠습니까?\n\n⚠️ 주의: 이 사업장과 연결된 모든 제품, 프로세스, 입력 데이터가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      setLoading(true);
      await axiosClient.delete(apiEndpoints.cbam.install.delete(id));
      console.log('✅ 사업장 삭제 성공');
      
      setToast({
        message: `"${name}" 사업장이 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchInstalls();
    } catch (error: any) {
      console.error('❌ 사업장 삭제 실패:', error);
      setToast({
        message: `사업장 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🏭 사업장 관리</h1>
          <p className="text-gray-300">
            CBAM 적용 대상 사업장 정보를 생성하고 관리합니다
          </p>
        </div>

        {/* Toast 메시지 */}
        {toast && (
          <div className={`mb-6 p-4 rounded-lg ${
            toast.type === 'success' ? 'bg-green-500/20 border border-green-500/50 text-green-300' :
            toast.type === 'error' ? 'bg-red-500/20 border border-red-500/50 text-red-300' :
            'bg-blue-500/20 border border-blue-500/50 text-blue-300'
          }`}>
            {toast.message}
          </div>
        )}

        {/* 사업장 생성 폼 */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
            🏭 사업장 생성
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 사업장명 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  사업장명 *
                </label>
                <Input
                  type="text"
                  placeholder="예: 포항제철소"
                  value={installForm.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required
                />
              </div>
              {/* 보고기간 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  보고기간 *
                </label>
                <Input
                  type="number"
                  placeholder="예: 2023"
                  value={installForm.reporting_year}
                  onChange={(e) => handleInputChange('reporting_year', e.target.value)}
                  required
                  min="2000"
                  max="2100"
                />
              </div>
            </div>

            {/* 제출 버튼 */}
            <div className="flex justify-end pt-6">
              <Button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 disabled:opacity-50"
              >
                {loading ? '생성 중...' : '사업장 생성'}
              </Button>
            </div>
          </form>
        </div>

        {/* 사업장 목록 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-white">📋 등록된 사업장 목록 ({installs.length}개)</h3>
            <div className="flex gap-2">
              {/* 정렬 옵션 */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'id')}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="name">이름순</option>
                <option value="id">ID순</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm hover:bg-white/20 transition-colors duration-200"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
              <button
                onClick={fetchInstalls}
                disabled={isLoadingInstalls}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200 disabled:opacity-50 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                새로고침
              </button>
            </div>
          </div>
          
          {isLoadingInstalls ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
              <p className="text-gray-300 mt-2">사업장 목록을 불러오는 중...</p>
            </div>
          ) : sortedInstalls.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sortedInstalls.map((install) => (
                <div
                  key={install.id}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 hover:bg-white/20 transition-all duration-200"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-white font-semibold text-lg">{install.name}</h4>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-300">
                      ID: {install.id}
                    </span>
                  </div>
                  <div className="space-y-1 mb-3">
                    <p className="text-gray-300 text-sm">보고기간: {install.reporting_year}년</p>
                  </div>
                  <div className="mt-3 pt-3 border-t border-white/10 flex gap-2">
                    <button
                      onClick={() => handleInstallClick(install.id)}
                      className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                    >
                      제품 관리
                    </button>
                    <button
                      onClick={() => handleDeleteInstall(install.id, install.name)}
                      disabled={loading}
                      className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200 disabled:opacity-50"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-300">등록된 사업장이 없습니다.</p>
              <p className="text-gray-400 text-sm mt-1">위에서 사업장을 등록해보세요.</p>
            </div>
          )}
        </div>

        {/* 전체 제품 관리 버튼 */}
        <div className="mt-6 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">📦 전체 제품 관리</h3>
          <p className="text-gray-300 mb-4">
            모든 사업장의 제품을 한 번에 관리할 수 있습니다.
          </p>
          <button
            onClick={handleProductManagement}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
          >
            📦 전체 제품 관리 페이지로 이동
          </button>
        </div>

        {/* 디버그 정보 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">🔍 디버그 정보</h3>
          <div className="bg-black/20 p-4 rounded-lg">
            <pre className="text-sm text-gray-300 overflow-auto">
              {JSON.stringify(installForm, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
