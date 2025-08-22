'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
import axiosClient from '@/lib/axiosClient';

// ============================================================================
// 📦 제품 관리 페이지
// ============================================================================

interface ProductForm {
  name: string;
  cn_code: string;
  period_start: string;
  period_end: string;
  production_qty: number;
  sales_qty: number;
  export_qty: number;
  inventory_qty: number;
  defect_rate: number;
}

export default function ProductPage() {
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [productForm, setProductForm] = useState<ProductForm>({
    name: '',
    cn_code: '',
    period_start: '',
    period_end: '',
    production_qty: 0,
    sales_qty: 0,
    export_qty: 0,
    inventory_qty: 0,
    defect_rate: 0
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
      const response = await axiosClient.post('/api/v1/boundary/product', productForm);
      
      setToast({
        message: '제품이 성공적으로 생성되었습니다!',
        type: 'success'
      });

      // 폼 초기화
      setProductForm({
        name: '',
        cn_code: '',
        period_start: '',
        period_end: '',
        production_qty: 0,
        sales_qty: 0,
        export_qty: 0,
        inventory_qty: 0,
        defect_rate: 0
      });

    } catch (error) {
      console.error('제품 생성 실패:', error);
      setToast({
        message: '제품 생성에 실패했습니다.',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">📦 제품 관리</h1>
          <p className="text-gray-300">
            제품 정보를 생성하고 관리합니다
          </p>
        </div>

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
                  placeholder="예: 철강 제품"
                  value={productForm.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required
                />
              </div>

              {/* CN 코드 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  CN 코드
                </label>
                <Input
                  type="text"
                  placeholder="예: 7208"
                  value={productForm.cn_code}
                  onChange={(e) => handleInputChange('cn_code', e.target.value)}
                />
              </div>

              {/* 시작일 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  시작일 *
                </label>
                <Input
                  type="date"
                  value={productForm.period_start}
                  onChange={(e) => handleInputChange('period_start', e.target.value)}
                  required
                />
              </div>

              {/* 종료일 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  종료일 *
                </label>
                <Input
                  type="date"
                  value={productForm.period_end}
                  onChange={(e) => handleInputChange('period_end', e.target.value)}
                  required
                />
              </div>

              {/* 생산량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  생산량 (톤)
                </label>
                <Input
                  type="number"
                  placeholder="0"
                  value={productForm.production_qty}
                  onChange={(e) => handleInputChange('production_qty', parseFloat(e.target.value) || 0)}
                />
              </div>

              {/* 외부판매량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  외부판매량 (톤)
                </label>
                <Input
                  type="number"
                  placeholder="0"
                  value={productForm.sales_qty}
                  onChange={(e) => handleInputChange('sales_qty', parseFloat(e.target.value) || 0)}
                />
              </div>

              {/* 수출량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  수출량 (톤)
                </label>
                <Input
                  type="number"
                  placeholder="0"
                  value={productForm.export_qty}
                  onChange={(e) => handleInputChange('export_qty', parseFloat(e.target.value) || 0)}
                />
              </div>

              {/* 재고량 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  재고량 (톤)
                </label>
                <Input
                  type="number"
                  placeholder="0"
                  value={productForm.inventory_qty}
                  onChange={(e) => handleInputChange('inventory_qty', parseFloat(e.target.value) || 0)}
                />
              </div>

              {/* 불량률 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  불량률 (%)
                </label>
                <Input
                  type="number"
                  placeholder="0"
                  step="0.01"
                  value={productForm.defect_rate}
                  onChange={(e) => handleInputChange('defect_rate', parseFloat(e.target.value) || 0)}
                />
              </div>
            </div>

            {/* 제출 버튼 */}
            <div className="flex justify-end">
              <Button
                type="submit"
                loading={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {loading ? '생성 중...' : '제품 생성'}
              </Button>
            </div>
          </form>
        </div>

        {/* Toast */}
        {toast && (
          <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            toast.type === 'success' ? 'bg-green-600' :
            toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
          } text-white`}>
            <div className="flex items-center justify-between">
              <span>{toast.message}</span>
              <button
                onClick={() => setToast(null)}
                className="ml-2 text-white hover:text-gray-200"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
