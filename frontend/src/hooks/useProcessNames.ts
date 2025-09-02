import { useState, useEffect, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

export const useProcessNames = () => {
  const [processNames, setProcessNames] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProcessNames = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Railway DB의 dummy 테이블에서 고유한 공정명 목록을 가져오는 API 호출
      const response = await axiosClient.get(apiEndpoints.cbam.dummy.processNames);
      
      // API 응답이 배열인지 확인
      if (Array.isArray(response.data)) {
        // 공정명만 추출하여 설정
        const names = response.data.map((item: any) => {
          // item이 문자열이면 그대로 사용, 객체면 공정 필드 추출
          return typeof item === 'string' ? item : item.공정 || item.process_name || item;
        }).filter(Boolean); // 빈 값 제거
        
        setProcessNames(names);
        console.log('✅ 공정명 목록 조회 성공:', names.length, '개');
      } else {
        console.warn('⚠️ API 응답이 배열이 아닙니다:', response.data);
        setProcessNames([]);
        setError('공정명 목록을 가져오는데 실패했습니다.');
      }
    } catch (err) {
      console.error('❌ 공정명 목록 조회 실패:', err);
      setError('공정명 목록을 불러오는데 실패했습니다.');
      setProcessNames([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchProcessNamesByPeriod = useCallback(async (startDate?: string, endDate?: string) => {
    console.log('🚀 fetchProcessNamesByPeriod 호출됨:', { startDate, endDate });
    
    try {
      setLoading(true);
      setError(null);
      console.log('⏳ 로딩 상태 시작');
      
      // 기간별 공정명 목록을 가져오는 API 호출
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const apiUrl = `${apiEndpoints.cbam.dummy.processNamesByPeriod}?${params.toString()}`;
      console.log('🌐 API 호출 URL:', apiUrl);
      
      const response = await axiosClient.get(apiUrl);
      console.log('📡 API 응답 받음:', response);
      
      // API 응답이 배열인지 확인
      if (Array.isArray(response.data)) {
        console.log('✅ 응답 데이터가 배열임:', response.data);
        
        // 공정명만 추출하여 설정
        const names = response.data.map((item: any) => {
          // item이 문자열이면 그대로 사용, 객체면 공정 필드 추출
          return typeof item === 'string' ? item : item.공정 || item.process_name || item;
        }).filter(Boolean); // 빈 값 제거
        
        setProcessNames(names);
        console.log('✅ 기간별 공정명 목록 조회 성공:', names.length, '개');
      } else {
        console.warn('⚠️ API 응답이 배열이 아닙니다:', response.data);
        setProcessNames([]);
        setError('기간별 공정명 목록을 가져오는데 실패했습니다.');
      }
    } catch (err) {
      console.error('❌ 기간별 공정명 목록 조회 실패:', err);
      setError('기간별 공정명 목록을 불러오는데 실패했습니다.');
      setProcessNames([]);
    } finally {
      setLoading(false);
      console.log('⏹️ 로딩 상태 종료');
    }
  }, []);

  const refreshProcessNames = useCallback(async () => {
    await fetchProcessNames();
  }, [fetchProcessNames]);

  return {
    processNames,
    loading,
    error,
    fetchProcessNames,
    fetchProcessNamesByPeriod,
    refreshProcessNames
  };
};
