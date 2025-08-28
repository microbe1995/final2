'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { useRouter } from 'next/navigation';

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

interface ProductName {
  id: number;
  product_name: string;
}

export default function ProcessPage() {
  const router = useRouter();
  const [productId, setProductId] = useState<string | null>(null);
  
  const [processForm, setProcessForm] = useState<ProcessForm>({
    product_id: 0,
    process_name: '',
    start_period: '',
    end_period: ''
  });
  
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [productNames, setProductNames] = useState<ProductName[]>([]);
  const [processes, setProcesses] = useState<any[]>([]);
  const [editingProcess, setEditingProcess] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [isLoadingProcesses, setIsLoadingProcesses] = useState(false);
  const [message, setMessage] = useState('');

  // 공정 목록 조회
  const fetchProcesses = async () => {
    setIsLoadingProcesses(true);
    try {
      console.log('🔍 공정 목록 조회 시작');
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      console.log('📋 공정 목록 응답:', response);
      setProcesses(response.data);
      console.log('📋 공정 목록 데이터:', response.data);
    } catch (error: any) {
      console.error('❌ 공정 목록 조회 실패:', error);
      setMessage(`공정 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoadingProcesses(false);
    }
  };

  // 폼 초기화
  const resetForm = () => {
    setProcessForm({
      product_id: 0,
      process_name: '',
      start_period: '',
      end_period: ''
    });
    setEditingProcess(null);
  };

  // 수정 모드 시작
  const handleEdit = (process: any) => {
    setEditingProcess(process);
    setProcessForm({
      product_id: process.product_id || 0,
      process_name: process.process_name,
      start_period: process.start_period || '',
      end_period: process.end_period || ''
    });
  };

  // 수정 취소
  const handleCancelEdit = () => {
    resetForm();
  };

  // 공정 삭제
  const handleDelete = async (processId: number) => {
    if (!confirm('정말로 이 공정을 삭제하시겠습니까?')) return;

    try {
      setIsLoading(true);
      await axiosClient.delete(apiEndpoints.cbam.process.delete(processId));
      console.log('✅ 공정 삭제 성공');
      setMessage('공정이 성공적으로 삭제되었습니다!');
      fetchProcesses();
    } catch (error: any) {
      console.error('❌ 공정 삭제 실패:', error);
      setMessage(`공정 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 제품명 목록 조회
  useEffect(() => {
    const fetchProductNames = async () => {
      setIsLoadingProducts(true);
      try {
        console.log('🔍 제품명 목록 조회 시작');
        const response = await axiosClient.get(apiEndpoints.cbam.product.names);
        console.log('📋 제품명 목록 응답:', response);
        setProductNames(response.data);
        console.log('📋 제품명 목록 데이터:', response.data);
      } catch (error: any) {
        console.error('❌ 제품명 목록 조회 실패:', error);
        setMessage(`제품명 목록을 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`);
      } finally {
        setIsLoadingProducts(false);
      }
    };

    fetchProductNames();
    fetchProcesses();
  }, []);

  // URL에서 product_id 파라미터 읽어오기
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const id = urlParams.get('product_id');
      setProductId(id);
      if (id) {
        setProcessForm(prev => ({
          ...prev,
          product_id: parseInt(id)
        }));
      }
    }
  }, []);

  // 선택된 제품 정보 조회
  useEffect(() => {
    const fetchSelectedProduct = async () => {
      if (!processForm.product_id) {
        return;
      }

      try {
        console.log('🔍 선택된 제품 조회 시작:', processForm.product_id);
        const response = await axiosClient.get(apiEndpoints.cbam.product.get(processForm.product_id));
        console.log('📋 선택된 제품 응답:', response);
        setSelectedProduct(response.data);
        console.log('📋 선택된 제품 데이터:', response.data);
      } catch (error: any) {
        console.error('❌ 선택된 제품 조회 실패:', error);
        console.error('❌ 에러 상세:', error.response?.data);
        console.error('❌ 에러 상태:', error.response?.status);
        setMessage(`제품 정보를 불러오는데 실패했습니다: ${error.response?.data?.detail || error.message}`);
      }
    };

    if (processForm.product_id) {
      fetchSelectedProduct();
    }
  }, [processForm.product_id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      // 데이터 검증
      if (!processForm.product_id) {
        setMessage('제품을 선택해주세요.');
        return;
      }
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

      const requestData = {
        ...processForm,
        start_period: new Date(processForm.start_period),
        end_period: new Date(processForm.end_period)
      };
      
      if (editingProcess) {
        // 수정
        console.log('📤 프로세스 수정 요청 데이터:', requestData);
        await axiosClient.put(apiEndpoints.cbam.process.update(editingProcess.id), requestData);
        console.log('✅ 프로세스 수정 성공');
        setMessage('프로세스가 성공적으로 수정되었습니다!');
      } else {
        // 생성
        console.log('📤 프로세스 생성 요청 데이터:', requestData);
        const response = await axiosClient.post(apiEndpoints.cbam.process.create, requestData);
        console.log('✅ 프로세스 생성 성공:', response.data);
        setMessage('프로세스가 성공적으로 생성되었습니다!');
      }
      
      // 폼 초기화
      resetForm();
      setSelectedProduct(null);
      
      // 공정 목록 새로고침
      await fetchProcesses();
      
    } catch (error: any) {
      console.error('❌ 프로세스 저장 실패:', error);
      const errorMessage = error.response?.data?.detail || '프로세스 저장에 실패했습니다.';
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

          {/* 프로세스 생성/수정 폼 */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              {editingProcess ? '프로세스 수정' : '새 프로세스 생성'}
            </h2>
            
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
                  <option value="">제품을 선택해주세요</option>
                  {isLoadingProducts ? (
                    <option disabled>제품 목록을 불러오는 중...</option>
                  ) : (
                    productNames.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.product_name}
                      </option>
                    ))
                  )}
                </select>
              </div>

              {/* 선택된 제품 정보 */}
              {selectedProduct && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    선택된 제품 정보
                  </label>
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
                  <p className="mt-1 text-sm text-gray-500">
                    이 제품에 대한 프로세스를 관리합니다.
                  </p>
                </div>
              )}

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
              <div className="flex justify-end gap-4">
                {editingProcess && (
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-md transition-colors duration-200"
                  >
                    취소
                  </button>
                )}
                <button
                  type="submit"
                  disabled={isLoading || !processForm.product_id}
                  className={`px-6 py-2 rounded-md text-white font-medium ${
                    isLoading || !processForm.product_id
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                  }`}
                >
                  {isLoading ? '저장 중...' : (editingProcess ? '수정' : '프로세스 생성')}
                </button>
              </div>
            </form>
          </div>

          {/* 공정 목록 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">등록된 공정 목록</h2>
            
            {isLoadingProcesses ? (
              <div className="text-center py-8">
                <div className="text-gray-500">공정 목록을 불러오는 중...</div>
              </div>
            ) : processes.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500">등록된 공정이 없습니다.</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="border-b border-gray-200">
                    <tr>
                      <th className="py-3 px-4 text-gray-700 font-semibold">ID</th>
                      <th className="py-3 px-4 text-gray-700 font-semibold">공정명</th>
                      <th className="py-3 px-4 text-gray-700 font-semibold">시작일</th>
                      <th className="py-3 px-4 text-gray-700 font-semibold">종료일</th>
                      <th className="py-3 px-4 text-gray-700 font-semibold">작업</th>
                    </tr>
                  </thead>
                  <tbody>
                    {processes.map((process) => (
                      <tr key={process.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-gray-900">{process.id}</td>
                        <td className="py-3 px-4 text-gray-900">{process.process_name}</td>
                        <td className="py-3 px-4 text-gray-600">
                          {process.start_period ? new Date(process.start_period).toLocaleDateString() : '-'}
                        </td>
                        <td className="py-3 px-4 text-gray-600">
                          {process.end_period ? new Date(process.end_period).toLocaleDateString() : '-'}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleEdit(process)}
                              className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded transition-colors duration-200"
                            >
                              수정
                            </button>
                            <button
                              onClick={() => handleDelete(process.id)}
                              className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors duration-200"
                            >
                              삭제
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
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
