import { useState, useCallback } from 'react';
import axiosClient from '@/lib/axiosClient';

export interface DummyData {
  id: number;
  로트번호: string;
  생산품명: string;
  생산수량: number; // 🔴 수정: 정규화 후 number 타입으로 고정
  투입일: string | null;
  종료일: string | null;
  공정: string;
  투입물명: string | null;
  수량: number; // 🔴 수정: 정규화 후 number 타입으로 고정
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

  return {
    loading,
    error,
    getProcessesByProduct
  };
};
