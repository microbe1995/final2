'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
import axiosClient from '@/lib/axiosClient';

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
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
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

  const handleInputChange = (field: keyof ProductForm, value: string | number) => {
    setProductForm(prev => ({
      ...prev,
      [field]: value
    }));
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
                  onChange={(e) => {
                    const value = parseInt(e.target.value);
                    handleInputChange('install_id', isNaN(value) || value <= 0 ? 1 : value);
                  }}
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
