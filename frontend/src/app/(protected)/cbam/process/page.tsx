'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useRouter, useSearchParams } from 'next/navigation';

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
  product_amount: number;
  prostart_period: string;
  proend_period: string;
}

export default function ProcessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const productId = searchParams.get('product_id');
  
  const [processForm, setProcessForm] = useState<ProcessForm>({
    product_id: productId ? parseInt(productId) : 1,
    process_name: '',
    start_period: '',
    end_period: ''
  });
  
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  // 선택된 제품 정보 조회
  useEffect(() => {
    const fetchSelectedProduct = async () => {
      if (!productId) {
        setMessage('제품 ID가 없습니다. 제품 목록에서 제품을 선택해주세요.');
        router.push('/cbam/calculation');
        return;
      }

      try {
        console.log('🔍 선택된 제품 조회 시작:', productId);
        const response = await axiosClient.get(apiEndpoints.cbam.product.get(parseInt(productId)));
        console.log('📋 선택된 제품 응답:', response);
        setSelectedProduct(response.data);
        console.log('📋 선택된 제품 데이터:', response.data);
      } catch (error: any) {
        console.error('❌ 선택된 제품 조회 실패:', error);
        console.error('❌ 에러 상세:', error.response?.data);
        console.error('❌ 에러 상태:', error.response?.status);
        setMessage(`제품 정보를 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`);
        
        // 제품을 찾을 수 없으면 제품 목록으로 리다이렉트
        if (error.response?.status === 404) {
          setTimeout(() => {
            router.push('/cbam/calculation');
          }, 2000);
        }
      }
    };

    fetchSelectedProduct();
  }, [productId, router]);

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
              {/* 선택된 제품 정보 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  선택된 제품
                </label>
                {selectedProduct ? (
                  <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{selectedProduct.product_name}</h3>
                        <p className="text-sm text-gray-600">카테고리: {selectedProduct.product_category}</p>
                        <p className="text-sm text-gray-600">수량: {selectedProduct.product_amount}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        selectedProduct.product_category === '단순제품' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {selectedProduct.product_category}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                    <p className="text-gray-500">제품 정보를 불러오는 중...</p>
                  </div>
                )}
                <p className="mt-1 text-sm text-gray-500">
                  이 제품에 대한 프로세스를 관리합니다.
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

                     {/* 제품으로 돌아가기 */}
           <div className="bg-gray-50 rounded-lg p-6">
             <h2 className="text-xl font-semibold text-gray-900 mb-6">제품 관리</h2>
             <div className="flex justify-between items-center">
               <p className="text-gray-600">
                 다른 제품을 관리하거나 제품 목록으로 돌아가세요.
               </p>
               <button
                 onClick={() => router.push('/cbam/calculation')}
                 className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors duration-200"
               >
                 제품 목록으로 돌아가기
               </button>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}
