import { useState, useCallback } from 'react';
import axiosClient from '@/lib/axiosClient';

export interface DummyData {
  id: number;
  로트번호: string;
  생산품명: string;
  생산수량: number; // 🔴 수정: int 타입으로 변경
  투입일: string | null;
  종료일: string | null;
  공정: string;
  투입물명: string | null;
  수량: number; // 🔴 수정: int 타입으로 변경
  단위: string;
  created_at: string;
  updated_at: string;
}

export const useDummyData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 제품별 공정 목록 조회
  const getProcessesByProduct = useCallback(async (productName: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // 🔴 수정: 올바른 API 경로 사용 (/api/v1/cbam/dummy/...)
      const response = await axiosClient.get(`/api/v1/cbam/dummy/products/${encodeURIComponent(productName)}/processes`);
      return response.data.data.processes || [];
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '공정 목록 조회에 실패했습니다.';
      setError(errorMessage);
      console.error('❌ 제품별 공정 목록 조회 실패:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // 🔴 추가: 생산품명별 기간 계산 함수
  const getProductPeriods = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 전체 더미 데이터 조회
      const response = await axiosClient.get('/api/v1/cbam/dummy/');
      const dummyData = response.data.data || [];
      
      // 생산품명별로 그룹화하여 기간 계산
      const productPeriods = new Map<string, { startDate: string; endDate: string }>();
      
      dummyData.forEach((item: DummyData) => {
        if (!item.생산품명 || !item.투입일 || !item.종료일) return;
        
        const existing = productPeriods.get(item.생산품명);
        
        if (existing) {
          // 기존 데이터가 있으면 최소/최대 날짜로 업데이트
          const currentStart = new Date(item.투입일);
          const currentEnd = new Date(item.종료일);
          const existingStart = new Date(existing.startDate);
          const existingEnd = new Date(existing.endDate);
          
          productPeriods.set(item.생산품명, {
            startDate: currentStart < existingStart ? item.투입일 : existing.startDate,
            endDate: currentEnd > existingEnd ? item.종료일 : existing.endDate
          });
        } else {
          // 새로운 생산품명이면 첫 번째 데이터로 설정
          productPeriods.set(item.생산품명, {
            startDate: item.투입일,
            endDate: item.종료일
          });
        }
      });
      
      return productPeriods;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '기간 계산에 실패했습니다.';
      setError(errorMessage);
      console.error('❌ 생산품명별 기간 계산 실패:', err);
      return new Map();
    } finally {
      setLoading(false);
    }
  }, []);

  // 🔴 추가: 특정 생산품명의 기간 조회
  const getProductPeriod = useCallback(async (productName: string) => {
    const allPeriods = await getProductPeriods();
    return allPeriods.get(productName) || null;
  }, [getProductPeriods]);

  // 🔴 추가: 특정 생산품명의 생산수량 조회 (마지막 행 기준)
  const getProductQuantity = useCallback(async (productName: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // 전체 더미 데이터 조회
      const response = await axiosClient.get('/api/v1/cbam/dummy/');
      const dummyData = response.data.data || [];
      
      // 해당 생산품명의 데이터만 필터링
      const productData = dummyData.filter((item: DummyData) => 
        item.생산품명 === productName
      );
      
      if (productData.length === 0) {
        return 0;
      }
      
      // 마지막 행의 생산수량 반환 (id 기준으로 정렬)
      const sortedData = productData.sort((a: DummyData, b: DummyData) => b.id - a.id);
      return sortedData[0].생산수량 || 0;
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '생산수량 조회에 실패했습니다.';
      setError(errorMessage);
      console.error('❌ 생산품명별 생산수량 조회 실패:', err);
      return 0;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getProcessesByProduct,
    getProductPeriods,
    getProductPeriod,
    getProductQuantity
  };
};
