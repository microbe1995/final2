import { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

export const useProductNames = () => {
  const [productNames, setProductNames] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProductNames = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Railway DB의 dummy 테이블에서 고유한 제품명 목록을 가져오는 API 호출
      const response = await axiosClient.get(apiEndpoints.cbam.dummy.productNames);
      
      // API 응답이 배열인지 확인
      if (Array.isArray(response.data)) {
        setProductNames(response.data);
        console.log('✅ 제품명 목록 조회 성공:', response.data.length, '개');
      } else {
        console.warn('⚠️ API 응답이 배열이 아닙니다:', response.data);
        setProductNames([]);
        setError('제품명 목록을 가져오는데 실패했습니다.');
      }
    } catch (err) {
      console.error('❌ 제품명 목록 조회 실패:', err);
      setError('제품명 목록을 불러오는데 실패했습니다.');
      setProductNames([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchProductNamesByPeriod = async (startDate?: string, endDate?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // 기간별 제품명 목록을 가져오는 API 호출
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await axiosClient.get(`${apiEndpoints.cbam.dummy.productNamesByPeriod}?${params.toString()}`);
      
      // API 응답이 배열인지 확인
      if (Array.isArray(response.data)) {
        setProductNames(response.data);
        console.log('✅ 기간별 제품명 목록 조회 성공:', response.data.length, '개');
      } else {
        console.warn('⚠️ API 응답이 배열이 아닙니다:', response.data);
        setProductNames([]);
        setError('기간별 제품명 목록을 가져오는데 실패했습니다.');
      }
    } catch (err) {
      console.error('❌ 기간별 제품명 목록 조회 실패:', err);
      setError('기간별 제품명 목록을 불러오는데 실패했습니다.');
      setProductNames([]);
    } finally {
      setLoading(false);
    }
  };

  const refreshProductNames = () => {
    fetchProductNames();
  };

  useEffect(() => {
    fetchProductNames();
  }, []);

  return {
    productNames,
    loading,
    error,
    refreshProductNames,
    fetchProductNamesByPeriod
  };
};
