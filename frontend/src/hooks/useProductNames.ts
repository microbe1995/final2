import { useState, useEffect, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

export const useProductNames = () => {
  const [productNames, setProductNames] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProductNames = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Railway DB의 dummy 테이블에서 고유한 제품명 목록을 가져오는 API 호출
      const response = await axiosClient.get(apiEndpoints.cbam.dummy.productNames);
      
      // API 응답이 배열인지 확인
      if (Array.isArray(response.data)) {
        // 제품명만 추출하여 설정
        const names = response.data.map((item: any) => {
          // item이 문자열이면 그대로 사용, 객체면 생산품명 필드 추출
          return typeof item === 'string' ? item : item.생산품명 || item.product_name || item;
        }).filter(Boolean); // 빈 값 제거
        
        setProductNames(names);
        console.log('✅ 제품명 목록 조회 성공:', names.length, '개');
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
  }, []);

  const fetchProductNamesByPeriod = useCallback(async (startDate?: string, endDate?: string) => {
    console.log('🚀 fetchProductNamesByPeriod 호출됨:', { startDate, endDate });
    
    try {
      setLoading(true);
      setError(null);
      console.log('⏳ 로딩 상태 시작');
      
      // 기간별 제품명 목록을 가져오는 API 호출
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const apiUrl = `${apiEndpoints.cbam.dummy.productNamesByPeriod}?${params.toString()}`;
      console.log('🌐 API 호출 URL:', apiUrl);
      
      const response = await axiosClient.get(apiUrl);
      console.log('📡 API 응답 받음:', response);
      
      // API 응답이 배열인지 확인
      if (Array.isArray(response.data)) {
        console.log('✅ 응답 데이터가 배열임:', response.data);
        
        // 제품명만 추출하여 설정
        const names = response.data.map((item: any) => {
          // item이 문자열이면 그대로 사용, 객체면 생산품명 필드 추출
          return typeof item === 'string' ? item : item.생산품명 || item.product_name || item;
        }).filter(Boolean); // 빈 값 제거
        
        setProductNames(names);
        console.log('✅ 기간별 제품명 목록 조회 성공:', names.length, '개');
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
      console.log('⏹️ 로딩 상태 종료');
    }
  }, []);

  const refreshProductNames = useCallback(() => {
    fetchProductNames();
  }, [fetchProductNames]);

  // 초기 로딩은 수동으로만 실행 (자동 실행 방지)
  // useEffect(() => {
  //   fetchProductNames();
  // }, []);

  return {
    productNames,
    loading,
    error,
    refreshProductNames,
    fetchProductNamesByPeriod
  };
};
