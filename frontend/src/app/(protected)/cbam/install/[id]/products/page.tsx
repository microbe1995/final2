'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axiosClient from '@/lib/axiosClient';
import { apiEndpoints } from '@/lib/axiosClient';

interface Install {
  id: number;
  install_name: string;
}

interface Product {
  id: number;
  install_id: number;
  product_name: string;
  product_category: string;
  prostart_period: string;
  proend_period: string;
  product_amount: number;
  product_cncode?: string;
  goods_name?: string;
  aggrgoods_name?: string;
  product_sell: number;
  product_eusell: number;
  created_at?: string;
  updated_at?: string;
}

interface Process {
  id: number;
  product_id: number;
  process_name: string;
  start_period: string;
  end_period: string;
  created_at?: string;
  updated_at?: string;
}

interface ProductForm {
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

interface ProcessForm {
  process_name: string;
  start_period: string;
  end_period: string;
}

export default function InstallProductsPage() {
  const router = useRouter();
  const params = useParams();
  const installId = parseInt(params.id as string);

  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [showProductForm, setShowProductForm] = useState(false);

  const [productForm, setProductForm] = useState<ProductForm>({
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

  // 사업장별 제품 목록 조회
  const fetchProducts = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      // 현재 사업장의 제품들만 필터링
      const filteredProducts = response.data.filter((product: Product) => product.install_id === installId);
      setProducts(filteredProducts);
    } catch (error: any) {
      console.error('❌ 제품 목록 조회 실패:', error);
    }
  };

  useEffect(() => {
    if (installId) {
      fetchProducts();
      setIsLoading(false);
    }
  }, [installId]);

  const handleProductInputChange = (field: keyof ProductForm, value: string | number) => {
    setProductForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleProductSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!productForm.product_name || !productForm.prostart_period || !productForm.proend_period) {
      setToast({
        message: '필수 필드를 모두 입력해주세요.',
        type: 'error'
      });
      return;
    }

    try {
      const productData = {
        ...productForm,
        install_id: installId
      };

      const response = await axiosClient.post(apiEndpoints.cbam.product.create, productData);
      console.log('✅ 제품 생성 성공:', response.data);
      
      setToast({
        message: '제품이 성공적으로 생성되었습니다.',
        type: 'success'
      });

      // 폼 초기화 및 숨기기
      setProductForm({
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
      setShowProductForm(false);

      // 목록 새로고침
      fetchProducts();
    } catch (error: any) {
      console.error('❌ 제품 생성 실패:', error);
      setToast({
        message: `제품 생성에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleDeleteProduct = async (productId: number, productName: string) => {
    if (!confirm(`"${productName}" 제품을 삭제하시겠습니까?\n\n⚠️ 주의: 이 제품과 연결된 모든 프로세스가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      await axiosClient.delete(apiEndpoints.cbam.product.delete(productId));
      console.log('✅ 제품 삭제 성공');
      
      setToast({
        message: `"${productName}" 제품이 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchProducts();
    } catch (error: any) {
      console.error('❌ 제품 삭제 실패:', error);
      setToast({
        message: `제품 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-300 mt-4">데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* 토스트 메시지 */}
        {toast && (
          <div className={`mb-4 p-4 rounded-lg ${
            toast.type === 'success' ? 'bg-green-600' : 
            toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
          }`}>
            {toast.message}
          </div>
        )}

        {/* 제품 관리 섹션 */}
        <div className="space-y-6">
          {/* 제품 생성 폼 */}
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">📦 제품 관리</h2>
              <button
                onClick={() => setShowProductForm(!showProductForm)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors duration-200"
              >
                {showProductForm ? '취소' : '제품 추가'}
              </button>
            </div>

            {showProductForm && (
              <form onSubmit={handleProductSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">제품명 *</label>
                  <input
                    type="text"
                    value={productForm.product_name}
                    onChange={(e) => handleProductInputChange('product_name', e.target.value)}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="예: 철강, 알루미늄"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">제품 카테고리</label>
                  <select
                    value={productForm.product_category}
                    onChange={(e) => handleProductInputChange('product_category', e.target.value as '단순제품' | '복합제품')}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="단순제품">단순제품</option>
                    <option value="복합제품">복합제품</option>
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">기간 시작일 *</label>
                    <input
                      type="date"
                      value={productForm.prostart_period}
                      onChange={(e) => handleProductInputChange('prostart_period', e.target.value)}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">기간 종료일 *</label>
                    <input
                      type="date"
                      value={productForm.proend_period}
                      onChange={(e) => handleProductInputChange('proend_period', e.target.value)}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
                >
                  📦 제품 생성
                </button>
              </form>
            )}
          </div>

          {/* 제품 목록 */}
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">📋 등록된 제품 목록 ({products.length}개)</h3>
            
            {products.length === 0 ? (
              <p className="text-gray-300 text-center py-4">등록된 제품이 없습니다.</p>
            ) : (
              <div className="space-y-3">
                {products.map((product) => (
                  <div key={product.id} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="text-white font-semibold text-lg">{product.product_name}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        product.product_category === '단순제품' ? 'bg-green-500/20 text-green-300' : 'bg-blue-500/20 text-blue-300'
                      }`}>
                        {product.product_category}
                      </span>
                    </div>
                    
                    <div className="space-y-1 mb-3">
                      <p className="text-gray-300 text-sm">기간: {product.prostart_period} ~ {product.proend_period}</p>
                      <p className="text-gray-300 text-sm">수량: {product.product_amount.toLocaleString()}</p>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDeleteProduct(product.id, product.product_name)}
                        className="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                      >
                        삭제
                      </button>
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
