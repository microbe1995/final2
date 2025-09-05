import { useState, useCallback } from 'react';
import { useFuelMasterAPI } from '@/hooks/useFuelMasterAPI';
import { useMaterialMasterAPI } from '@/hooks/useMaterialMasterAPI';
import axiosClient from '@/lib/axiosClient';

export interface DummyData {
  id: number;
  로트번호: string;
  생산품명: string;
  생산수량: number; // 서버에서 float로 올 수 있으므로 최종적으로 number로 사용
  투입일: string | null;
  종료일: string | null;
  공정: string;
  투입물명: string | null;
  수량: number; // 서버에서 float로 올 수 있으므로 number로 사용
  단위: string;
  created_at: string;
  updated_at: string;
}

export const useDummyData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { searchFuels } = useFuelMasterAPI();
  const { lookupMaterialByName } = useMaterialMasterAPI();

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
      const response = await axiosClient.get('/api/v1/cbam/dummy');
      // 백엔드가 배열 그대로를 반환하므로, data 또는 data.data 모두 대응
      const payload = response.data;
      const dummyData = Array.isArray(payload) ? payload : (payload?.data || []);
      
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
      const response = await axiosClient.get('/api/v1/cbam/dummy');
      // 배열 또는 {data: [...]} 형태 모두 지원
      const payload = response.data;
      const dummyData = Array.isArray(payload) ? payload : (payload?.data || []);
      
      // 해당 생산품명의 데이터만 필터링
      const productData = dummyData.filter((item: DummyData) => item.생산품명 === productName);
      
      if (productData.length === 0) {
        return 0;
      }
      
      // 마지막 행의 생산수량 반환 (id 기준으로 정렬) + 안전 캐스팅
      const sortedData = productData.sort((a: DummyData, b: DummyData) => b.id - a.id);
      const qtyRaw = (sortedData[0] as any)?.생산수량;
      const qty = typeof qtyRaw === 'string' ? parseFloat(qtyRaw) : Number(qtyRaw);
      return Number.isFinite(qty) ? qty : 0;
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '생산수량 조회에 실패했습니다.';
      setError(errorMessage);
      console.error('❌ 생산품명별 생산수량 조회 실패:', err);
      return 0;
    } finally {
      setLoading(false);
    }
  }, []);

  // 🔴 추가: 기간/공정/제품명 기준으로 더미 투입물(원료 중심) 목록 조회
  const getMaterialsFor = useCallback(
    async (
      params: {
        processName?: string;
        startDate?: string | null;
        endDate?: string | null;
        productNames?: string[];
      }
    ) => {
      setLoading(true);
      setError(null);
      try {
        const response = await axiosClient.get('/api/v1/cbam/dummy');
        const payload = response.data;
        const dummyData: DummyData[] = Array.isArray(payload) ? payload : (payload?.data || []);

        const { processName, startDate, endDate, productNames } = params || {};
        const start = startDate ? new Date(startDate) : null;
        const end = endDate ? new Date(endDate) : null;

        // 필터링: 공정(유연 매칭), 기간, 제품명(옵션), 투입물명 존재
        const filtered = dummyData.filter((row) => {
          if (!row.투입물명) return false;
          if (processName) {
            const rowProc = String(row.공정 || '').trim();
            const proc = String(processName || '').trim();
            const rowNorm = rowProc.replace(/\s+/g, '');
            const procNorm = proc.replace(/\s+/g, '');
            const procMatched = rowNorm === procNorm || rowNorm.includes(procNorm) || procNorm.includes(rowNorm);
            if (!procMatched) return false;
          }
          if (start && row.투입일 && new Date(row.투입일) < start) return false;
          if (end && row.종료일 && new Date(row.종료일) > end) return false;
          if (productNames && productNames.length > 0) {
            if (!row.생산품명 || !productNames.includes(row.생산품명)) return false;
          }
          return true;
        });

        // 이름 기준 유니크 목록과 대표 수량/단위 집계
        const map = new Map<string, { name: string; amount: number; unit: string }>();
        for (const row of filtered) {
          const key = row.투입물명 as string;
          const prev = map.get(key);
          if (prev) {
            map.set(key, { name: key, amount: prev.amount + (row.수량 || 0), unit: prev.unit || row.단위 || '' });
          } else {
            map.set(key, { name: key, amount: row.수량 || 0, unit: row.단위 || '' });
          }
        }

        // Material Master 매칭 결과 우선 + 미매칭 fallback 함께 반환
        const names = Array.from(map.keys());
        const checks = await Promise.all(
          names.map(async (n) => {
            try {
              const res = await lookupMaterialByName(n);
              const ok = !!res && res.success && Array.isArray(res.data) && res.data.length > 0;
              return { name: n, isMaterial: ok };
            } catch {
              return { name: n, isMaterial: false };
            }
          })
        );

        const matchedNames = checks.filter((c) => c.isMaterial).map((c) => c.name);
        const matched = matchedNames.map((n) => map.get(n)!).filter(Boolean);
        // 원료 드롭다운에는 실제 원료로 판정된 항목만 노출
        return matched;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || '투입물 조회에 실패했습니다.';
        setError(errorMessage);
        console.error('❌ 투입물(원료) 조회 실패:', err);
        return [] as { name: string; amount: number; unit: string }[];
      } finally {
        setLoading(false);
      }
    },
    [lookupMaterialByName]
  );

  // 🔴 추가: 기간/공정/제품명 기준으로 더미 투입물 중 "연료" 후보만 추출
  const getFuelsFor = useCallback(
    async (
      params: {
        processName?: string;
        startDate?: string | null;
        endDate?: string | null;
        productNames?: string[];
      }
    ) => {
      setLoading(true);
      setError(null);
      try {
        const response = await axiosClient.get('/api/v1/cbam/dummy');
        const payload = response.data;
        const dummyData: DummyData[] = Array.isArray(payload) ? payload : (payload?.data || []);

        const { processName, startDate, endDate, productNames } = params || {};
        const start = startDate ? new Date(startDate) : null;
        const end = endDate ? new Date(endDate) : null;

        // 1) 더미 데이터 1차 필터링
        const filtered = dummyData.filter((row) => {
          if (!row.투입물명) return false;
          if (processName && row.공정 !== processName) return false;
          if (start && row.투입일 && new Date(row.투입일) < start) return false;
          if (end && row.종료일 && new Date(row.종료일) > end) return false;
          if (productNames && productNames.length > 0) {
            if (!row.생산품명 || !productNames.includes(row.생산품명)) return false;
          }
          return true;
        });

        // 2) 이름 기준 집계 (총량/단위 대표값)
        const map = new Map<string, { name: string; amount: number; unit: string }>();
        for (const row of filtered) {
          const key = row.투입물명 as string;
          const prev = map.get(key);
          if (prev) {
            map.set(key, { name: key, amount: prev.amount + (row.수량 || 0), unit: prev.unit || row.단위 || '' });
          } else {
            map.set(key, { name: key, amount: row.수량 || 0, unit: row.단위 || '' });
          }
        }

        // 3) Fuel Master 기준으로 실제 연료 우선 + 미매칭 항목은 fallback 으로 함께 노출
        const names = Array.from(map.keys());
        const checks = await Promise.all(
          names.map(async (n) => {
            try {
              const suggestions = await searchFuels(n);
              return { name: n, isFuel: Array.isArray(suggestions) && suggestions.length > 0 };
            } catch {
              return { name: n, isFuel: false };
            }
          })
        );

        const matchedNames = checks.filter((c) => c.isFuel).map((c) => c.name);
        const matched = matchedNames.map((n) => map.get(n)!).filter(Boolean);
        // 연료 드롭다운에는 실제 연료로 판정된 항목만 노출
        return matched;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || '연료 목록 조회에 실패했습니다.';
        setError(errorMessage);
        console.error('❌ 연료(더미) 조회 실패:', err);
        return [] as { name: string; amount: number; unit: string }[];
      } finally {
        setLoading(false);
      }
    },
    [searchFuels]
  );

  return {
    loading,
    error,
    getProcessesByProduct,
    getProductPeriods,
    getProductPeriod,
    getProductQuantity,
    getMaterialsFor,
    getFuelsFor
  };
};
