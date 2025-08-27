'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

interface Process {
  id: number;
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

export default function ProcessListPage() {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // 프로세스 목록과 제품 목록을 병렬로 조회
        const [processesResponse, productsResponse] = await Promise.all([
          axiosClient.get(apiEndpoints.cbam.process.list),
          axiosClient.get(apiEndpoints.cbam.product.list)
        ]);

        setProcesses(processesResponse.data);
        setProducts(productsResponse.data);
        
        console.log('📋 프로세스 목록:', processesResponse.data);
        console.log('📋 제품 목록:', productsResponse.data);
        
      } catch (error: any) {
        console.error('❌ 데이터 조회 실패:', error);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // 제품명 조회 헬퍼 함수
  const getProductName = (productId: number) => {
    const product = products.find(p => p.id === productId);
    return product ? product.product_name : `제품 ID: ${productId}`;
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg p-6">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">프로세스 목록</h1>
            <a
              href="/cbam/process"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
            >
              새 프로세스 생성
            </a>
          </div>

          {processes.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      제품
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      프로세스명
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      시작일
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      종료일
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      기간
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {processes.map(process => {
                    const startDate = new Date(process.start_period);
                    const endDate = new Date(process.end_period);
                    const durationDays = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
                    
                    return (
                      <tr key={process.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {process.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {getProductName(process.product_id)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {process.process_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(process.start_period)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(process.end_period)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {durationDays}일
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">📋</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">등록된 프로세스가 없습니다</h3>
              <p className="text-gray-500 mb-6">
                첫 번째 프로세스를 생성해보세요.
              </p>
              <a
                href="/cbam/process"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium"
              >
                프로세스 생성하기
              </a>
            </div>
          )}

          {/* 통계 정보 */}
          {processes.length > 0 && (
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-lg font-medium text-blue-900 mb-2">📊 통계 정보</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{processes.length}</div>
                  <div className="text-sm text-blue-700">총 프로세스 수</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {new Set(processes.map(p => p.product_id)).size}
                  </div>
                  <div className="text-sm text-blue-700">관련 제품 수</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {Math.round(processes.reduce((acc, p) => {
                      const start = new Date(p.start_period);
                      const end = new Date(p.end_period);
                      return acc + (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
                    }, 0) / processes.length)}일
                  </div>
                  <div className="text-sm text-blue-700">평균 기간</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
