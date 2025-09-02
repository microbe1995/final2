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
  
  // 🔴 추가: 제품-공정 관계 설정 관련 상태
  const [activeTab, setActiveTab] = useState<'install' | 'product-process'>('install');
  const [products, setProducts] = useState<any[]>([]);
  const [processes, setProcesses] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [productProcessRelations, setProductProcessRelations] = useState<Map<number, any[]>>(new Map());

  // 사업장 목록 조회
  const fetchInstalls = async () => {
    try {
      setIsLoadingInstalls(true);
      
      // 🔴 추가: 상세 디버깅 로그
      console.log('🚀 Install 목록 조회 시작');
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
      console.log('📋 사업장 목록:', response.data);
      
    } catch (error: any) {
      console.error('❌❌ 사업장 목록 조회 실패:', {
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
        message: `사업장 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoadingInstalls(false);
    }
  };

  // 🔴 추가: 제품과 공정 데이터 조회 함수들
  const fetchProducts = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      setProducts(response.data);
      console.log('✅ 제품 목록 조회 성공:', response.data);
    } catch (error: any) {
      console.error('❌ 제품 목록 조회 실패:', error);
      setToast({
        message: `제품 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const fetchProcesses = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      setProcesses(response.data);
      console.log('✅ 공정 목록 조회 성공:', response.data);
    } catch (error: any) {
      console.error('❌ 공정 목록 조회 실패:', error);
      setToast({
        message: `공정 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const fetchProductProcessRelations = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.productProcess.list);
      const relations = new Map();
      response.data.forEach((relation: any) => {
        if (!relations.has(relation.product_id)) {
          relations.set(relation.product_id, []);
        }
        relations.get(relation.product_id).push(relation);
      });
      setProductProcessRelations(relations);
      console.log('✅ 제품-공정 관계 조회 성공:', relations);
    } catch (error: any) {
      console.error('❌ 제품-공정 관계 조회 실패:', error);
    }
  };

  useEffect(() => {
    fetchInstalls();
    fetchProducts();
    fetchProcesses();
    fetchProductProcessRelations();
  }, []);

  // 사업장 정렬
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

  // 사업장 클릭 시 제품 관리 페이지로 이동
  const handleInstallClick = (installId: number) => {
    router.push(`/cbam/install/${installId}/products`);
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
          message: '사업장명을 입력해주세요.',
          type: 'error'
        });
        setLoading(false);
        return;
      }

      if (editingInstall) {
        // 수정
        console.log('📤 사업장 수정 요청 데이터:', installForm);
        await axiosClient.put(apiEndpoints.cbam.install.update(editingInstall.id), installForm);
        console.log('✅ 사업장 수정 성공');
        setToast({
          message: '사업장이 성공적으로 수정되었습니다!',
          type: 'success'
        });
      } else {
        // 생성
        console.log('📤 사업장 생성 요청 데이터:', installForm);
        const response = await axiosClient.post(apiEndpoints.cbam.install.create, installForm);
        console.log('✅ 사업장 생성 성공:', response.data);
        setToast({
          message: '사업장이 성공적으로 생성되었습니다!',
          type: 'success'
        });
      }

      // 폼 초기화
      resetForm();

      // 사업장 목록 새로고침
      await fetchInstalls();

    } catch (error: any) {
      console.error('❌ 사업장 저장 실패:', error);
      
      setToast({
        message: `사업장 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // 사업장 삭제
  const handleDeleteInstall = async (id: number, install_name: string) => {
    if (!confirm(`"${install_name}" 사업장을 삭제하시겠습니까?\n\n⚠️ 주의: 이 사업장과 연결된 모든 제품, 프로세스, 입력 데이터가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      setLoading(true);
              await axiosClient.delete(apiEndpoints.cbam.install.delete(id));
      console.log('✅ 사업장 삭제 성공');
      
      setToast({
        message: `"${install_name}" 사업장이 성공적으로 삭제되었습니다.`,
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

  // 🔴 추가: 제품-공정 관계 관리 함수들
  const handleAddProcessToProduct = async (productId: number, processId: number) => {
    try {
      await axiosClient.post(apiEndpoints.cbam.productProcess.create, {
        product_id: productId,
        process_id: processId
      });
      
      setToast({
        message: '제품에 공정이 추가되었습니다.',
        type: 'success'
      });
      
      fetchProductProcessRelations();
    } catch (error: any) {
      console.error('❌ 공정 추가 실패:', error);
      setToast({
        message: `공정 추가에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleRemoveProcessFromProduct = async (productId: number, processId: number) => {
    try {
      // 제품-공정 관계 삭제
      const relations = productProcessRelations.get(productId) || [];
      const relation = relations.find((r: any) => r.process_id === processId);
      
      if (relation) {
        await axiosClient.delete(apiEndpoints.cbam.productProcess.delete(relation.id));
        
        setToast({
          message: '제품에서 공정이 제거되었습니다.',
          type: 'success'
        });
        
        fetchProductProcessRelations();
      }
    } catch (error: any) {
      console.error('❌ 공정 제거 실패:', error);
      setToast({
        message: `공정 제거에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
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

        {/* 탭 네비게이션 */}
        <div className="mb-6 flex gap-2 border-b border-white/10">
          <button
            onClick={() => setActiveTab('install')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'install'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            🏭 사업장 관리
          </button>
          <button
            onClick={() => setActiveTab('product-process')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'product-process'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            🔗 제품-공정 관계 설정
          </button>
        </div>

        {/* 사업장 관리 탭 */}
        {activeTab === 'install' && (
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
              {editingInstall ? '🏭 사업장 수정' : '🏭 사업장 생성'}
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
                {loading ? '저장 중...' : (editingInstall ? '수정' : '사업장 생성')}
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
                onChange={(e) => setSortBy(e.target.value as 'install_name' | 'id')}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
      )}

      {/* 제품-공정 관계 설정 탭 */}
      {activeTab === 'product-process' && (
        <div className="space-y-6">
          {/* 제품 선택 */}
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <h2 className="text-2xl font-semibold text-white mb-6">🔗 제품-공정 관계 설정</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                제품 선택
              </label>
              <select
                value={selectedProduct?.id || ''}
                onChange={(e) => {
                  const product = products.find(p => p.id === parseInt(e.target.value));
                  setSelectedProduct(product || null);
                }}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">제품을 선택하세요</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.product_name}
                  </option>
                ))}
              </select>
            </div>

            {/* 선택된 제품의 공정 관계 표시 */}
            {selectedProduct && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">
                  📋 {selectedProduct.product_name}의 공정 관계
                </h3>
                
                {/* 현재 연결된 공정들 */}
                <div className="bg-white/5 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-3">✅ 연결된 공정</h4>
                  {(() => {
                    const relations = productProcessRelations.get(selectedProduct.id) || [];
                    return relations.length > 0 ? (
                      <div className="space-y-2">
                        {relations.map((relation: any) => {
                          const process = processes.find(p => p.id === relation.process_id);
                          const install = installs.find(i => i.id === relation.install_id);
                          return process ? (
                            <div key={relation.id} className="flex justify-between items-center p-3 bg-white/10 rounded-lg">
                              <div>
                                <span className="text-white font-medium">{process.process_name}</span>
                                <span className="text-gray-400 ml-2">({install?.install_name || '알 수 없음'})</span>
                              </div>
                              <button
                                onClick={() => handleRemoveProcessFromProduct(selectedProduct.id, process.id)}
                                className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-md transition-colors duration-200"
                              >
                                제거
                              </button>
                            </div>
                          ) : null;
                        })}
                      </div>
                    ) : (
                      <p className="text-gray-400">연결된 공정이 없습니다.</p>
                    );
                  })()}
                </div>

                {/* 사용 가능한 공정 추가 */}
                <div className="bg-white/5 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-3">➕ 공정 추가</h4>
                  <div className="space-y-2">
                    {processes.map((process) => {
                      const relations = productProcessRelations.get(selectedProduct.id) || [];
                      const isAlreadyConnected = relations.some((r: any) => r.process_id === process.id);
                      const processInstall = installs.find(i => i.id === process.install_id);
                      
                      return (
                        <div key={process.id} className="flex justify-between items-center p-3 bg-white/10 rounded-lg">
                          <div>
                            <span className="text-white font-medium">{process.process_name}</span>
                            <span className="text-gray-400 ml-2">({processInstall?.install_name || '알 수 없음'})</span>
                          </div>
                          {isAlreadyConnected ? (
                            <span className="text-green-400 text-sm">✓ 연결됨</span>
                          ) : (
                            <button
                              onClick={() => handleAddProcessToProduct(selectedProduct.id, process.id)}
                              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-md transition-colors duration-200"
                            >
                              추가
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
