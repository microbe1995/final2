'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useRouter } from 'next/navigation';
import CbamLayout from '@/components/cbam/CbamLayout';
import InstallProductsPage from '@/app/(protected)/cbam/install/[id]/products/page';

// ============================================================================
// 🏭 시설군 관리 페이지
// ============================================================================

interface Install {
  id: number;
  install_name: string;
  reporting_year: number;
}

interface InstallForm {
  install_name: string;
  reporting_year: number;
}

export default function InstallPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const [installs, setInstalls] = useState<any[]>([]);
  const [isLoadingInstalls, setIsLoadingInstalls] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [sortBy, setSortBy] = useState<'install_name' | 'id'>('install_name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [editingInstall, setEditingInstall] = useState<Install | null>(null);
  const [installForm, setInstallForm] = useState<InstallForm>({
    install_name: '',
    reporting_year: new Date().getFullYear() // 현재 년도로 기본값 설정
  });
  // 제품 관리 인라인 표시 상태
  const [showProductManagerFor, setShowProductManagerFor] = useState<number | null>(null);
  
  // 탭/제품-공정 관계 설정은 제거

  // 시설군 목록 조회
  const fetchInstalls = async () => {
    try {
      setIsLoadingInstalls(true);
      
      // 🔴 추가: 상세 디버깅 로그
      console.log('🚀 시설군 목록 조회 시작');
      console.log('📍 API 엔드포인트:', apiEndpoints.cbam.install.list);
      console.log('🌐 Base URL:', process.env.NEXT_PUBLIC_API_BASE_URL || '환경변수 없음');
      console.log('🔑 인증 토큰:', localStorage.getItem('auth_token') ? '존재함' : '없음');
      
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      
      console.log('✅ API 응답 성공:', {
        status: response.status,
        statusText: response.statusText,
        dataLength: response.data?.length || 0,
        data: response.data
      });
      
      setInstalls(response.data);
      console.log('📋 시설군 목록:', response.data);
      
    } catch (error: any) {
      console.error('❌❌ 시설군 목록 조회 실패:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          baseURL: error.config?.baseURL,
          headers: error.config?.headers
        }
      });
      
      setToast({
        message: `시설군 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoadingInstalls(false);
    }
  };

  // 제품/공정/관계 로딩 로직 제거

  useEffect(() => {
    fetchInstalls();
  }, []);

  // 시설군 정렬
  const sortedInstalls = [...installs].sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'install_name':
        aValue = a.install_name.toLowerCase();
        bValue = b.install_name.toLowerCase();
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

  // 시설군 클릭 시 제품 관리 페이지로 이동 (산정경계설정과 유사한 전환 UX 적용)
  const handleInstallClick = (installId: number) => {
    // 동일 버튼 토글: 열려있으면 닫기
    if (showProductManagerFor === installId) {
      setShowProductManagerFor(null);
      return;
    }
    setShowProductManagerFor(installId);
  };

  // 폼 초기화
  const resetForm = () => {
    setInstallForm({
      install_name: '',
      reporting_year: new Date().getFullYear()
    });
    setEditingInstall(null);
  };

  // 수정 모드 시작
  const handleEdit = (install: Install) => {
    setEditingInstall(install);
    setInstallForm({
      install_name: install.install_name,
      reporting_year: install.reporting_year
    });
  };

  // 수정 취소
  const handleCancelEdit = () => {
    resetForm();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 데이터 검증
      if (!installForm.install_name.trim()) {
        setToast({
          message: '시설군명을 입력해주세요.',
          type: 'error'
        });
        setLoading(false);
        return;
      }

      if (editingInstall) {
        // 수정
        console.log('📤 시설군 수정 요청 데이터:', installForm);
        await axiosClient.put(apiEndpoints.cbam.install.update(editingInstall.id), installForm);
        console.log('✅ 시설군 수정 성공');
        setToast({
          message: '시설군이 성공적으로 수정되었습니다!',
          type: 'success'
        });
      } else {
        // 생성
        console.log('📤 시설군 생성 요청 데이터:', installForm);
        const response = await axiosClient.post(apiEndpoints.cbam.install.create, installForm);
        console.log('✅ 시설군 생성 성공:', response.data);
        setToast({
          message: '시설군이 성공적으로 생성되었습니다!',
          type: 'success'
        });
      }

      // 폼 초기화
      resetForm();

      // 시설군 목록 새로고침
      await fetchInstalls();

    } catch (error: any) {
      console.error('❌ 시설군 저장 실패:', error);
      
      setToast({
        message: `시설군 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // 시설군 삭제
  const handleDeleteInstall = async (id: number, install_name: string) => {
    if (!confirm(`"${install_name}" 시설군을 삭제하시겠습니까?\n\n⚠️ 주의: 이 시설군과 연결된 모든 제품, 프로세스, 입력 데이터가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      setLoading(true);
              await axiosClient.delete(apiEndpoints.cbam.install.delete(id));
      console.log('✅ 시설군 삭제 성공');
      
      setToast({
        message: `"${install_name}" 시설군이 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchInstalls();
    } catch (error: any) {
      console.error('❌ 시설군 삭제 실패:', error);
      setToast({
        message: `시설군 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // 관계 관리 UI/로직 제거

  return (
    <CbamLayout>
        <div
          className={`max-w-6xl mx-auto transition-all duration-200 ease-out ${
            isNavigating ? 'opacity-0 scale-[0.99]' : 'opacity-100 scale-100'
          }`}
        >
        
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

        {/* 탭 제거: 사업장 관리 단일 페이지 */}

        {/* 시설군 관리 */}
          <>
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
              {editingInstall ? '군 수정' : '군 생성'}
            </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 시설군명 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  시설군명 *
                </label>
                <Input
                  type="text"
                  placeholder="예: 포항제철소"
                  value={installForm.install_name}
                  onChange={(e) => handleInputChange('install_name', e.target.value)}
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
            <div className="flex justify-end gap-4 pt-6">
              {editingInstall && (
                <Button
                  type="button"
                  onClick={handleCancelEdit}
                  className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors duration-200"
                >
                  취소
                </Button>
              )}
              <Button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 disabled:opacity-50"
              >
                {loading ? '저장 중...' : (editingInstall ? '수정' : '시설군 생성')}
              </Button>
            </div>
          </form>
        </div>

        {/* 시설군 목록 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-white">📋 등록된 시설군 목록 ({installs.length}개)</h3>
            <div className="flex gap-2">
              {/* 정렬 옵션 */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'install_name' | 'id')}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 [&>option]:bg-slate-800 [&>option]:text-white"
              >
                <option value="install_name">이름순</option>
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
              <p className="text-gray-300 mt-2">시설군 목록을 불러오는 중...</p>
            </div>
          ) : sortedInstalls.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sortedInstalls.map((install) => (
                <div
                  key={install.id}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 hover:bg-white/20 transition-all duration-200"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-white font-semibold text-lg">{install.install_name}</h4>
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
                      onClick={() => handleEdit(install)}
                      disabled={loading}
                      className="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-md transition-colors duration-200 disabled:opacity-50"
                    >
                      수정
                    </button>
                    <button
                      onClick={() => handleDeleteInstall(install.id, install.install_name)}
                      disabled={loading}
                      className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200 disabled:opacity-50"
                    >
                      삭제
                    </button>
                  </div>

                  {/* 버튼만 유지; 모달은 카드 외부에서 렌더링 */}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-300">등록된 시설군이 없습니다.</p>
              <p className="text-gray-400 text-sm mt-1">위에서 시설군을 등록해보세요.</p>
            </div>
          )}
        </div>

        {/* 제품 관리 모달 */}
        {showProductManagerFor !== null && (
          <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center">
            <div className="max-w-6xl w-full mx-4 bg-gray-900 border border-gray-700 rounded-lg shadow-xl overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-gray-700">
                <h4 className="text-white font-semibold">제품 관리</h4>
                <button
                  onClick={() => setShowProductManagerFor(null)}
                  className="text-gray-300 hover:text-white"
                >
                  ✕
                </button>
              </div>
              <div className="h-[70vh] overflow-y-auto">
                <InstallProductsPage overrideInstallId={showProductManagerFor as number} />
              </div>
            </div>
          </div>
        )}
          </>
        </div>
      </CbamLayout>
  );
}
