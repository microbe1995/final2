'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axiosClient from '@/lib/axiosClient';
import { apiEndpoints } from '@/lib/axiosClient';
import { useMappingAPI, HSCNMappingResponse } from '@/hooks/useMappingAPI';

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
  product_hscode: string; // HS 코드 추가
  product_cncode: string;
  goods_name: string;
  aggrgoods_name: string;
  product_sell: number;
  product_eusell: number;
}

interface ProcessForm {
  process_name: string;
}

export default function InstallProductsPage() {
  const router = useRouter();
  const params = useParams();
  const installId = parseInt(params.id as string);

  const [products, setProducts] = useState<Product[]>([]);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [showProductForm, setShowProductForm] = useState(false);
  const [showProcessFormForProduct, setShowProcessFormForProduct] = useState<number | null>(null);

  const [productForm, setProductForm] = useState<ProductForm>({
    product_name: '',
    product_category: '단순제품',
    prostart_period: '',
    proend_period: '',
    product_amount: 0,
    product_hscode: '', // HS 코드 초기값 추가
    product_cncode: '',
    goods_name: '',
    aggrgoods_name: '',
    product_sell: 0,
    product_eusell: 0
  });

  // HS-CN 매핑 API 훅 사용
  const { lookupByHSCode, loading: mappingLoading } = useMappingAPI();
  const [cnCodeResults, setCnCodeResults] = useState<HSCNMappingResponse[]>([]);
  const [showCnCodeResults, setShowCnCodeResults] = useState(false);

  const [processForm, setProcessForm] = useState<ProcessForm>({
    process_name: ''
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

  // 제품별 프로세스 목록 조회
  const fetchProcesses = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      setProcesses(response.data);
    } catch (error: any) {
      console.error('❌ 프로세스 목록 조회 실패:', error);
    }
  };

  useEffect(() => {
    if (installId) {
      fetchProducts();
      fetchProcesses();
      setIsLoading(false);
    }
  }, [installId]);

  const handleProductInputChange = (field: keyof ProductForm, value: string | number) => {
    setProductForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleProcessInputChange = (field: keyof ProcessForm, value: string) => {
    setProcessForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // HS 코드 조회 함수
  const handleHSCodeLookup = async (hsCode: string) => {
    if (hsCode.length === 10) {
      try {
        const results = await lookupByHSCode(hsCode);
        setCnCodeResults(results);
        setShowCnCodeResults(true);
      } catch (error) {
        console.error('HS 코드 조회 실패:', error);
        setCnCodeResults([]);
        setShowCnCodeResults(false);
      }
    } else {
      setShowCnCodeResults(false);
    }
  };

  // CN 코드 선택 함수
  const handleSelectCNCode = (result: HSCNMappingResponse) => {
    setProductForm(prev => ({
      ...prev,
      product_cncode: result.cncode_total,
      goods_name: result.goods_name || '',
      aggrgoods_name: result.aggregoods_name || ''
    }));
    setShowCnCodeResults(false);
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
        product_hscode: '', // HS 코드 초기화 추가
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

  const handleProcessSubmit = async (e: React.FormEvent, productId: number) => {
    e.preventDefault();
    
    if (!processForm.process_name) {
      setToast({
        message: '공정명을 입력해주세요.',
        type: 'error'
      });
      return;
    }

    try {
      const processData = {
        process_name: processForm.process_name,
        product_ids: [productId]  // 다대다 관계를 위해 배열로 전송
      };

      console.log('🔍 전송할 공정 데이터:', processData);
      console.log('🔍 API 엔드포인트:', apiEndpoints.cbam.process.create);

      const response = await axiosClient.post(apiEndpoints.cbam.process.create, processData);
      console.log('✅ 프로세스 생성 성공:', response.data);
      
      setToast({
        message: '프로세스가 성공적으로 생성되었습니다.',
        type: 'success'
      });

      // 폼 초기화 및 숨기기
      setProcessForm({
        process_name: ''
      });
      setShowProcessFormForProduct(null);

      // 목록 새로고침
      fetchProcesses();
      console.log('🔄 공정 목록 새로고침 완료');
    } catch (error: any) {
      console.error('❌ 프로세스 생성 실패:', error);
      console.error('❌ 에러 응답 데이터:', error.response?.data);
      console.error('❌ 에러 상태 코드:', error.response?.status);
      setToast({
        message: `프로세스 생성에 실패했습니다: ${error.response?.data?.detail || error.message}`,
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
      fetchProcesses();
    } catch (error: any) {
      console.error('❌ 제품 삭제 실패:', error);
      setToast({
        message: `제품 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleDeleteProcess = async (processId: number, processName: string) => {
    if (!confirm(`"${processName}" 프로세스를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await axiosClient.delete(apiEndpoints.cbam.process.delete(processId));
      console.log('✅ 프로세스 삭제 성공');
      
      setToast({
        message: `"${processName}" 프로세스가 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchProcesses();
    } catch (error: any) {
      console.error('❌ 프로세스 삭제 실패:', error);
      setToast({
        message: `프로세스 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
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

                {/* HS 코드 입력 필드 */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">HS 코드 (10자리)</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={productForm.product_hscode}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '').slice(0, 10);
                        handleProductInputChange('product_hscode', value);
                        if (value.length === 10) {
                          handleHSCodeLookup(value);
                        } else {
                          setShowCnCodeResults(false);
                        }
                      }}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="예: 7208510000"
                      maxLength={10}
                    />
                    {mappingLoading && (
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                      </div>
                    )}
                  </div>
                  {productForm.product_hscode.length > 0 && productForm.product_hscode.length < 10 && (
                    <p className="text-yellow-400 text-xs mt-1">HS 코드는 10자리 숫자여야 합니다.</p>
                  )}
                </div>

                {/* CN 코드 결과 표시 */}
                {showCnCodeResults && cnCodeResults.length > 0 && (
                  <div className="bg-white/10 border border-white/20 rounded-md p-3">
                    <h4 className="text-sm font-medium text-white mb-2">🔍 CN 코드 검색 결과:</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {cnCodeResults.map((result, index) => (
                        <div
                          key={index}
                          onClick={() => handleSelectCNCode(result)}
                          className="p-2 bg-white/5 rounded cursor-pointer hover:bg-white/10 transition-colors"
                        >
                          <div className="text-sm text-blue-300 font-medium">{result.cncode_total}</div>
                          <div className="text-xs text-gray-300">{result.goods_name}</div>
                          <div className="text-xs text-gray-400">{result.aggregoods_name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* CN 코드 및 품목 정보 표시 */}
                {productForm.product_cncode && (
                  <div className="bg-green-500/10 border border-green-500/20 rounded-md p-3">
                    <h4 className="text-sm font-medium text-green-300 mb-2">✅ 선택된 CN 코드:</h4>
                    <div className="space-y-1">
                      <div className="text-sm text-white">CN 코드: <span className="font-medium">{productForm.product_cncode}</span></div>
                      {productForm.goods_name && (
                        <div className="text-xs text-gray-300">품목명: {productForm.goods_name}</div>
                      )}
                      {productForm.aggrgoods_name && (
                        <div className="text-xs text-gray-300">제품 대분류: {productForm.aggrgoods_name}</div>
                      )}
                    </div>
                  </div>
                )}

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
              <div className="space-y-6">
                {products.map((product) => {
                  // 다대다 관계에 맞게 제품과 연결된 공정들 필터링
                  const productProcesses = processes.filter((process: any) => 
                    process.products && process.products.some((p: any) => p.id === product.id)
                  );
                  console.log(`🔍 제품 ${product.product_name} (ID: ${product.id})의 공정들:`, productProcesses);
                  const isShowingProcessForm = showProcessFormForProduct === product.id;
                  
                  return (
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
                        <p className="text-gray-300 text-sm">공정 수: {productProcesses.length}개</p>
                        {product.product_cncode && (
                          <div className="mt-2 p-2 bg-blue-500/10 rounded border border-blue-500/20">
                            <p className="text-blue-300 text-sm">CN 코드: <span className="font-medium">{product.product_cncode}</span></p>
                            {product.goods_name && (
                              <p className="text-gray-300 text-xs">품목명: {product.goods_name}</p>
                            )}
                            {product.aggrgoods_name && (
                              <p className="text-gray-300 text-xs">제품 대분류: {product.aggrgoods_name}</p>
                            )}
                          </div>
                        )}
                      </div>

                      {/* 공정 목록 */}
                      {productProcesses.length > 0 && (
                        <div className="mb-4 p-3 bg-white/5 rounded-lg">
                          <h5 className="text-sm font-medium text-white mb-2">📋 등록된 공정:</h5>
                          <div className="space-y-2">
                            {productProcesses.map((process) => (
                              <div key={process.id} className="flex justify-between items-center p-2 bg-white/5 rounded">
                                <span className="text-gray-300 text-sm">{process.process_name}</span>
                                <div className="flex gap-1">
                                  <button
                                    onClick={() => router.push(`/cbam/process/process-input?process_id=${process.id}`)}
                                    className="px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded"
                                  >
                                    입력 데이터
                                  </button>
                                  <button
                                    onClick={() => handleDeleteProcess(process.id, process.process_name)}
                                    className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded"
                                  >
                                    삭제
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 공정 추가 폼 */}
                      {isShowingProcessForm && (
                        <div className="mb-4 p-4 bg-white/5 rounded-lg border border-purple-500/30">
                          <h5 className="text-sm font-medium text-white mb-3">🔄 공정 추가</h5>
                          <form onSubmit={(e) => handleProcessSubmit(e, product.id)} className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-300 mb-1">공정명 *</label>
                              <input
                                type="text"
                                value={processForm.process_name}
                                onChange={(e) => handleProcessInputChange('process_name', e.target.value)}
                                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                placeholder="예: 압연, 용해, 주조"
                                required
                              />
                            </div>
                            <div className="flex gap-2">
                              <button
                                type="submit"
                                className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                              >
                                🔄 공정 생성
                              </button>
                              <button
                                type="button"
                                onClick={() => setShowProcessFormForProduct(null)}
                                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                              >
                                취소
                              </button>
                            </div>
                          </form>
                        </div>
                      )}

                      <div className="flex gap-2">
                        <button
                          onClick={() => setShowProcessFormForProduct(isShowingProcessForm ? null : product.id)}
                          className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                        >
                          {isShowingProcessForm ? '공정 추가 취소' : '공정 추가'}
                        </button>
                        <button
                          onClick={() => handleDeleteProduct(product.id, product.product_name)}
                          className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                        >
                          삭제
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
