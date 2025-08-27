'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

interface ProcessForm {
  product_id: number;
  process_name: string;
  start_period: string;
  end_period: string;
}

interface Product {
  id: number;
  product_name: string;
  product_category: string;
}

export default function ProcessPage() {
  const [processForm, setProcessForm] = useState<ProcessForm>({
    product_id: 1,
    process_name: '',
    start_period: '',
    end_period: ''
  });
  
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  // 제품 목록 조회
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axiosClient.get(apiEndpoints.cbam.product.list);
        setProducts(response.data);
        console.log('📋 제품 목록:', response.data);
      } catch (error) {
        console.error('❌ 제품 목록 조회 실패:', error);
        setMessage('제품 목록을 불러오는데 실패했습니다.');
      }
    };

    fetchProducts();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      // 데이터 검증
      if (!processForm.process_name.trim()) {
        setMessage('프로세스명을 입력해주세요.');
        return;
      }
      if (!processForm.start_period) {
        setMessage('시작일을 입력해주세요.');
        return;
      }
      if (!processForm.end_period) {
        setMessage('종료일을 입력해주세요.');
        return;
      }
      if (processForm.product_id <= 0) {
        setMessage('유효한 제품을 선택해주세요.');
        return;
      }

      const requestData = {
        ...processForm,
        start_period: new Date(processForm.start_period),
        end_period: new Date(processForm.end_period)
      };
      
      console.log('📤 프로세스 생성 요청 데이터:', requestData);
      const response = await axiosClient.post(apiEndpoints.cbam.process.create, requestData);
      
      console.log('✅ 프로세스 생성 성공:', response.data);
      setMessage('프로세스가 성공적으로 생성되었습니다!');
      
      // 폼 초기화
      setProcessForm({
        product_id: 1,
        process_name: '',
        start_period: '',
        end_period: ''
      });
      
    } catch (error: any) {
      console.error('❌ 프로세스 생성 실패:', error);
      const errorMessage = error.response?.data?.detail || '프로세스 생성에 실패했습니다.';
      setMessage(`오류: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProcessForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">프로세스 관리</h1>
          
          {/* 메시지 표시 */}
          {message && (
            <div className={`mb-6 p-4 rounded-md ${
              message.includes('성공') 
                ? 'bg-green-50 text-green-800 border border-green-200' 
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {message}
            </div>
          )}

          {/* 프로세스 생성 폼 */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">새 프로세스 생성</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* 제품 선택 */}
              <div>
                <label htmlFor="product_id" className="block text-sm font-medium text-gray-700 mb-2">
                  제품 선택 *
                </label>
                <select
                  id="product_id"
                  name="product_id"
                  value={processForm.product_id}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {products.map(product => (
                    <option key={product.id} value={product.id}>
                      {product.product_name} ({product.product_category})
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-gray-500">
                  프로세스가 속할 제품을 선택하세요.
                </p>
              </div>

              {/* 프로세스명 */}
              <div>
                <label htmlFor="process_name" className="block text-sm font-medium text-gray-700 mb-2">
                  프로세스명 *
                </label>
                <input
                  type="text"
                  id="process_name"
                  name="process_name"
                  value={processForm.process_name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="예: 철광석 선별 공정"
                  required
                />
              </div>

              {/* 시작일 */}
              <div>
                <label htmlFor="start_period" className="block text-sm font-medium text-gray-700 mb-2">
                  시작일 *
                </label>
                <input
                  type="date"
                  id="start_period"
                  name="start_period"
                  value={processForm.start_period}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              {/* 종료일 */}
              <div>
                <label htmlFor="end_period" className="block text-sm font-medium text-gray-700 mb-2">
                  종료일 *
                </label>
                <input
                  type="date"
                  id="end_period"
                  name="end_period"
                  value={processForm.end_period}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              {/* 제출 버튼 */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`px-6 py-2 rounded-md text-white font-medium ${
                    isLoading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  }`}
                >
                  {isLoading ? '생성 중...' : '프로세스 생성'}
                </button>
              </div>
            </form>
          </div>

          {/* 현재 제품 목록 */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">현재 제품 목록</h2>
            {products.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        제품명
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        카테고리
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {products.map(product => (
                      <tr key={product.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {product.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {product.product_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {product.product_category}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">등록된 제품이 없습니다.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
