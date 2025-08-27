'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

// ============================================================================
// 📦 CBAM 제품 관리 페이지
// ============================================================================

interface Product {
  id: number;
  name: string;
  install_id: number;
  install_name?: string;
}

interface ProductForm {
  name: string;
  install_id: number;
}

interface Install {
  id: number;
  name: string;
  reporting_year: number;
}

export default function CalculationPage() {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [installs, setInstalls] = useState<Install[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [isLoadingInstalls, setIsLoadingInstalls] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [sortBy, setSortBy] = useState<'name' | 'id'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [productForm, setProductForm] = useState<ProductForm>({
    name: '',
    install_id: 0
  });

  // 제품 목록 조회
  const fetchProducts = async () => {
    try {
      setIsLoadingProducts(true);
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      setProducts(response.data);
      console.log('📋 제품 목록:', response.data);
    } catch (error: any) {
      console.error('❌ 제품 목록 조회 실패:', error);
      setToast({
        message: `제품 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoadingProducts(false);
    }
  };

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
    fetchProducts();
    fetchInstalls();
  }, []);

  // 제품 정렬
  const sortedProducts = [...products].sort((a, b) => {
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

  const handleInputChange = (field: keyof ProductForm, value: string) => {
    setProductForm(prev => ({
      ...prev,
      [field]: field === 'install_id' ? parseInt(value) || 0 : value
    }));
  };

  // 사업장명 가져오기
  const getInstallName = (installId: number) => {
    const install = installs.find(i => i.id === installId);
    return install ? install.name : '알 수 없음';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 데이터 검증
      if (!productForm.name.trim()) {
        setToast({
          message: '제품명을 입력해주세요.',
          type: 'error'
        });
        setLoading(false);
        return;
      }

      if (!productForm.install_id) {
        setToast({
          message: '사업장을 선택해주세요.',
          type: 'error'
        });
        setLoading(false);
        return;
      }

      console.log('📤 제품 생성 요청 데이터:', productForm);
      
      const response = await axiosClient.post(apiEndpoints.cbam.product.create, productForm);
      
      console.log('✅ 제품 생성 성공:', response.data);
      
      setToast({
        message: '제품이 성공적으로 생성되었습니다!',
        type: 'success'
      });

      // 폼 초기화
      setProductForm({
        name: '',
        install_id: 0
      });

      // 제품 목록 새로고침
      await fetchProducts();

    } catch (error: any) {
      console.error('❌ 제품 생성 실패:', error);
      
      setToast({
        message: `제품 생성에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // 제품 삭제
  const handleDeleteProduct = async (id: number, name: string) => {
    if (!confirm(`"${name}" 제품을 삭제하시겠습니까?\n\n⚠️ 주의: 이 제품과 연결된 모든 프로세스가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      setLoading(true);
      await axiosClient.delete(apiEndpoints.cbam.product.delete(id));
      console.log('✅ 제품 삭제 성공');
      
      setToast({
        message: `"${name}" 제품이 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchProducts();
    } catch (error: any) {
      console.error('❌ 제품 삭제 실패:', error);
      setToast({
        message: `제품 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
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
          <h1 className="text-4xl font-bold text-white mb-2">📦 CBAM 제품 관리</h1>
          <p className="text-gray-300">
            CBAM 적용 대상 제품 정보를 생성하고 관리합니다
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

        {/* 제품 생성 폼 */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
            📦 제품 생성
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 제품명 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품명 *
                </label>
                <Input
                  type="text"
                  placeholder="예: 철근"
                  value={productForm.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required
                />
              </div>
              {/* 사업장 선택 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  사업장 *
                </label>
                <select
                  value={productForm.install_id}
                  onChange={(e) => handleInputChange('install_id', e.target.value)}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value={0}>사업장을 선택하세요</option>
                  {installs.map((install) => (
                    <option key={install.id} value={install.id}>
                      {install.name} ({install.reporting_year}년)
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* 제출 버튼 */}
            <div className="flex justify-end pt-6">
              <Button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 disabled:opacity-50"
              >
                {loading ? '생성 중...' : '제품 생성'}
              </Button>
            </div>
          </form>
        </div>

        {/* 제품 목록 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-white">📋 등록된 제품 목록 ({products.length}개)</h3>
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
                onClick={fetchProducts}
                disabled={isLoadingProducts}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200 disabled:opacity-50 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                새로고침
              </button>
            </div>
          </div>
          
          {isLoadingProducts ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
              <p className="text-gray-300 mt-2">제품 목록을 불러오는 중...</p>
            </div>
          ) : sortedProducts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sortedProducts.map((product) => (
                <div
                  key={product.id}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 hover:bg-white/20 transition-all duration-200"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-white font-semibold text-lg">{product.name}</h4>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-300">
                      ID: {product.id}
                    </span>
                  </div>
                  <div className="space-y-1 mb-3">
                    <p className="text-gray-300 text-sm">사업장: {getInstallName(product.install_id)}</p>
                  </div>
                  <div className="mt-3 pt-3 border-t border-white/10 flex gap-2">
                    <button
                      onClick={() => handleDeleteProduct(product.id, product.name)}
                      disabled={loading}
                      className="w-full px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200 disabled:opacity-50"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-300">등록된 제품이 없습니다.</p>
              <p className="text-gray-400 text-sm mt-1">위에서 제품을 등록해보세요.</p>
            </div>
          )}
        </div>

        {/* 디버그 정보 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">🔍 디버그 정보</h3>
          <div className="bg-black/20 p-4 rounded-lg">
            <pre className="text-sm text-gray-300 overflow-auto">
              {JSON.stringify(productForm, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
