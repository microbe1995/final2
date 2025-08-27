'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useRouter } from 'next/navigation';

// ============================================================================
// 📦 제품 관리 페이지
// ============================================================================

interface ProductForm {
  install_id: number;
  product_name: string;
  product_category: '단순제품' | '복합제품';
  prostart_period: string;
  proend_period: string;
  product_amount: number;
  product_cncode: string;
  goods_name: string;
  aggrgoods_name: string;
  product_sell: number;
  product_eusell: number;
}

export default function ProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [sortBy, setSortBy] = useState<'name' | 'category' | 'amount' | 'date'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [productForm, setProductForm] = useState<ProductForm>({
    install_id: 1, // 기본값으로 1 설정
    product_name: '',
    product_category: '단순제품',
    prostart_period: '',
    proend_period: '',
    product_amount: 0,
    product_cncode: '',
    goods_name: '',
    aggrgoods_name: '',
    product_sell: 0,
    product_eusell: 0
  });
  const [installs, setInstalls] = useState<any[]>([]); // 사업장 목록 상태

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
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      setInstalls(response.data);
      console.log('📋 사업장 목록:', response.data);
    } catch (error: any) {
      console.error('❌ 사업장 목록 조회 실패:', error);
    }
  };

  useEffect(() => {
    fetchProducts();
    fetchInstalls();
  }, []);

  // 사업장명 조회 헬퍼 함수
  const getInstallName = (installId: number) => {
    const install = installs.find((i: any) => i.id === installId);
    return install ? install.name : `사업장 ID: ${installId}`;
  };

  const handleInputChange = (field: keyof ProductForm, value: string | number) => {
    setProductForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 제품 클릭 시 프로세스 관리 페이지로 이동
  const handleProductClick = (productId: number) => {
    router.push(`/cbam/process?product_id=${productId}`);
  };

  // 제품 삭제
  const handleDeleteProduct = async (productId: number, productName: string) => {
    if (!confirm(`정말로 "${productName}" 제품을 삭제하시겠습니까?\n\n이 제품과 연결된 모든 프로세스도 함께 삭제됩니다.`)) {
      return;
    }

    try {
      setLoading(true);
      console.log('🗑️ 제품 삭제 요청:', productId);
      
      const response = await axiosClient.delete(apiEndpoints.cbam.product.delete(productId));
      console.log('✅ 제품 삭제 응답:', response);
      
      setToast({
        message: `"${productName}" 제품이 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      // 제품 목록 새로고침
      await fetchProducts();
    } catch (error: any) {
      console.error('❌ 제품 삭제 실패:', error);
      console.error('❌ 에러 상세:', error.response?.data);
      console.error('❌ 에러 상태:', error.response?.status);
      
      let errorMessage = '제품 삭제에 실패했습니다.';
      if (error.response?.data?.detail) {
        errorMessage += ` ${error.response.data.detail}`;
      } else if (error.message) {
        errorMessage += ` ${error.message}`;
      }
      
      setToast({
        message: errorMessage,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 데이터 검증
      if (!productForm.install_id || productForm.install_id <= 0) {
        setToast({
          message: '사업장 ID는 1 이상이어야 합니다.',
          type: 'error'
        });
        setLoading(false);
        return;
      }

      // 날짜 형식 변환
      const requestData = {
        ...productForm,
        prostart_period: new Date(productForm.prostart_period),
        proend_period: new Date(productForm.proend_period)
      };

      console.log('📤 제품 생성 요청 데이터:', requestData);
      
      const response = await axiosClient.post('/api/v1/boundary/product', requestData);
      
      console.log('✅ 제품 생성 성공:', response.data);
      
      setToast({
        message: '제품이 성공적으로 생성되었습니다!',
        type: 'success'
      });

      // 폼 초기화
      setProductForm({
        install_id: 1,
        product_name: '',
        product_category: '단순제품',
        prostart_period: '',
        proend_period: '',
        product_amount: 0,
        product_cncode: '',
        goods_name: '',
        aggrgoods_name: '',
        product_sell: 0,
        product_eusell: 0
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

  // 제품 정렬
  const sortedProducts = [...products].sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'name':
        aValue = a.product_name.toLowerCase();
        bValue = b.product_name.toLowerCase();
        break;
      case 'category':
        aValue = a.product_category;
        bValue = b.product_category;
        break;
      case 'amount':
        aValue = parseFloat(a.product_amount) || 0;
        bValue = parseFloat(b.product_amount) || 0;
        break;
      case 'date':
        aValue = new Date(a.prostart_period);
        bValue = new Date(b.prostart_period);
        break;
      default:
        return 0;
    }
    
    if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">📦 제품 관리</h1>
          <p className="text-gray-300">
            제품 정보를 생성하고 관리합니다
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* 사업장 ID */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  사업장 ID *
                </label>
                <Input
                  type="number"
                  placeholder="1"
                  value={productForm.install_id}
                  onChange={(e) => handleInputChange('install_id', parseInt(e.target.value) || 1)}
                  required
                />
              </div>

              {/* 제품명 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품명 *
                </label>
                <Input
                  type="text"
                  placeholder="예: 철강 제품"
                  value={productForm.product_name}
                  onChange={(e) => handleInputChange('product_name', e.target.value)}
                  required
                />
              </div>

              {/* 제품 카테고리 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품 카테고리 *
                </label>
                <select
                  value={productForm.product_category}
                  onChange={(e) => handleInputChange('product_category', e.target.value as '단순제품' | '복합제품')}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="단순제품">단순제품</option>
                  <option value="복합제품">복합제품</option>
                </select>
              </div>

              {/* 시작일 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  기간 시작일 *
                </label>
                <Input
                  type="date"
                  value={productForm.prostart_period}
                  onChange={(e) => handleInputChange('prostart_period', e.target.value)}
                  required
                />
              </div>

              {/* 종료일 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  기간 종료일 *
                </label>
                <Input
                  type="date"
                  value={productForm.proend_period}
                  onChange={(e) => handleInputChange('proend_period', e.target.value)}
                  required
                />
              </div>

              {/* 제품 수량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품 수량 *
                </label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={productForm.product_amount}
                  onChange={(e) => handleInputChange('product_amount', parseFloat(e.target.value) || 0)}
                  required
                />
              </div>

              {/* 제품 CN 코드 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품 CN 코드
                </label>
                <Input
                  type="text"
                  placeholder="예: 7208"
                  value={productForm.product_cncode}
                  onChange={(e) => handleInputChange('product_cncode', e.target.value)}
                />
              </div>

              {/* 상품명 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  상품명
                </label>
                <Input
                  type="text"
                  placeholder="상품명을 입력하세요"
                  value={productForm.goods_name}
                  onChange={(e) => handleInputChange('goods_name', e.target.value)}
                />
              </div>

              {/* 집계 상품명 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  집계 상품명
                </label>
                <Input
                  type="text"
                  placeholder="집계 상품명을 입력하세요"
                  value={productForm.aggrgoods_name}
                  onChange={(e) => handleInputChange('aggrgoods_name', e.target.value)}
                />
              </div>

              {/* 제품 판매량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품 판매량
                </label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={productForm.product_sell}
                  onChange={(e) => handleInputChange('product_sell', parseFloat(e.target.value) || 0)}
                />
              </div>

              {/* 제품 EU 판매량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  제품 EU 판매량
                </label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={productForm.product_eusell}
                  onChange={(e) => handleInputChange('product_eusell', parseFloat(e.target.value) || 0)}
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
                onChange={(e) => setSortBy(e.target.value as 'name' | 'category' | 'amount' | 'date')}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="name">이름순</option>
                <option value="category">카테고리순</option>
                <option value="amount">수량순</option>
                <option value="date">날짜순</option>
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
                    <h4 className="text-white font-semibold text-lg">{product.product_name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      product.product_category === '단순제품' 
                        ? 'bg-green-500/20 text-green-300' 
                        : 'bg-blue-500/20 text-blue-300'
                    }`}>
                      {product.product_category}
                    </span>
                  </div>
                  
                  {/* 사업장 정보 */}
                  <div className="mb-3">
                    <div className="text-sm text-gray-300">
                      🏭 {getInstallName(product.install_id)}
                    </div>
                  </div>

                  <div className="space-y-1 mb-3">
                    <p className="text-gray-300 text-sm">수량: {product.product_amount.toLocaleString()}</p>
                    <p className="text-gray-300 text-sm">기간: {product.prostart_period} ~ {product.proend_period}</p>
                    {product.product_cncode && (
                      <p className="text-gray-300 text-sm">CN 코드: {product.product_cncode}</p>
                    )}
                    {product.goods_name && (
                      <p className="text-gray-300 text-sm">상품명: {product.goods_name}</p>
                    )}
                    {product.aggrgoods_name && (
                      <p className="text-gray-300 text-sm">집계상품명: {product.aggrgoods_name}</p>
                    )}
                    {product.product_sell > 0 && (
                      <p className="text-gray-300 text-sm">판매량: {product.product_sell.toLocaleString()}</p>
                    )}
                    {product.product_eusell > 0 && (
                      <p className="text-gray-300 text-sm">EU 판매량: {product.product_eusell.toLocaleString()}</p>
                    )}
                  </div>
                  <div className="mt-3 pt-3 border-t border-white/10 flex gap-2">
                    <button
                      onClick={() => handleProductClick(product.id)}
                      className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                    >
                      프로세스 관리
                    </button>
                    <button
                      onClick={() => handleDeleteProduct(product.id, product.product_name)}
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
