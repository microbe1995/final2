import { useCallback, useRef } from 'react';
import { Node } from '@xyflow/react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

/**
 * 중앙 집중식 배출량 관리 훅
 * 단일 책임: 모든 배출량 계산, 새로고침, 동기화를 중앙에서 관리
 * 이벤트 기반 아키텍처 지원
 */
export const useEmissionManager = () => {
  const inFlightProcess = useRef<Set<number>>(new Set());
  const inFlightProduct = useRef<Set<number>>(new Set());
  
  // 배출량 계산 결과 캐시
  const emissionCache = useRef<Map<number, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 30000; // 30초

  // 캐시에서 배출량 데이터 조회
  const getCachedEmission = useCallback((id: number) => {
    const cached = emissionCache.current.get(id);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data;
    }
    return null;
  }, []);

  // 배출량 데이터 캐시에 저장
  const setCachedEmission = useCallback((id: number, data: any) => {
    emissionCache.current.set(id, { data, timestamp: Date.now() });
  }, []);

  // 공정 배출량 새로고침 - 중앙 집중식 관리
  const refreshProcessEmission = useCallback(async (processId: number): Promise<any> => {
    if (inFlightProcess.current.has(processId)) return null;
    inFlightProcess.current.add(processId);
    
    try {
      // 1. 캐시에서 먼저 확인
      const cachedData = getCachedEmission(processId);
      if (cachedData) {
        console.log(`🔍 공정 ${processId} 캐시된 배출량 데이터 사용:`, cachedData);
        return cachedData;
      }

      // 2. EdgeService를 통한 중앙 집중 배출량 조회
      let data: any = null;
      try {
        const resp = await axiosClient.get(apiEndpoints.cbam.edgePropagation.processEmission(processId));
        data = resp?.data?.data || null;
        console.log(`🔍 공정 ${processId} 배출량 데이터 조회:`, data);
      } catch (err: any) {
        if (err?.response?.status === 404) {
          try {
            const created = await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId));
            const resp2 = await axiosClient.get(apiEndpoints.cbam.edgePropagation.processEmission(processId));
            data = resp2?.data?.data || created?.data;
            console.log(`🔍 공정 ${processId} 배출량 계산 후 데이터:`, data);
          } catch (calcErr) {
            console.warn('⚠️ 공정 배출량 계산 실패:', calcErr);
            return null;
          }
        } else {
          throw err;
        }
      }
      
      if (!data) return null;

      // 배출량 데이터 검증 및 보정
      try {
        const [matTotResp, fuelTotResp] = await Promise.all([
          axiosClient.get(apiEndpoints.cbam.matdir.totalByProcess(processId)).catch(() => null),
          axiosClient.get(apiEndpoints.cbam.fueldir.totalByProcess(processId)).catch(() => null)
        ]);
        
        const latestMatTotal = Number(matTotResp?.data?.total_matdir_emission ?? 0) || 0;
        const latestFuelTotal = Number(fuelTotResp?.data?.total_fueldir_emission ?? 0) || 0;
        const savedMatTotal = Number(data.total_matdir_emission ?? data.total_matdir ?? 0) || 0;
        const savedFuelTotal = Number(data.total_fueldir_emission ?? data.total_fueldir ?? 0) || 0;
        
        const mismatch = Math.abs(latestMatTotal - savedMatTotal) > 1e-6 || Math.abs(latestFuelTotal - savedFuelTotal) > 1e-6;
        if (mismatch) {
          try {
            await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId));
            const latest = await axiosClient.get(apiEndpoints.cbam.edgePropagation.processEmission(processId));
            data = latest?.data?.data || data;
          } catch (_) {}
        }
      } catch (_) {}

      // 배출량 데이터 정규화
      const hasMatPart = ('total_matdir_emission' in data) || ('total_matdir' in data);
      const hasFuelPart = ('total_fueldir_emission' in data) || ('total_fueldir' in data);
      const hasDirectParts = hasMatPart || hasFuelPart;

      const totalMat = Number(data.total_matdir_emission ?? data.total_matdir ?? 0) || 0;
      const totalFuel = Number(data.total_fueldir_emission ?? data.total_fueldir ?? 0) || 0;
      const sumDirect = totalMat + totalFuel;
      const directFromDb = Number(data.attrdir_em ?? data.attrdir_emission ?? 0) || 0;
      const directFixed = hasDirectParts ? sumDirect : directFromDb;

      // 백그라운드 보정
      if (hasDirectParts && Math.abs(directFromDb - sumDirect) > 1e-6) {
        axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId)).catch(() => {});
      }

      // 누적 배출량 계산 - 더 정확한 로직
      let cumulativeEmission = data.cumulative_emission;
      if (cumulativeEmission === undefined || cumulativeEmission === null || cumulativeEmission === 0) {
        cumulativeEmission = directFixed;
      }
      
      console.log(`🔍 공정 ${processId} 최종 배출량 계산:`, {
        attr_em: directFixed,
        cumulative_emission: cumulativeEmission,
        total_matdir_emission: totalMat,
        total_fueldir_emission: totalFuel
      });

      const result = {
        attr_em: directFixed,
        cumulative_emission: cumulativeEmission,
        total_matdir_emission: totalMat,
        total_fueldir_emission: totalFuel,
        calculation_date: data.calculation_date
      };

      // 3. 결과를 캐시에 저장
      setCachedEmission(processId, result);
      
      return result;
    } catch (e) {
      console.error('⚠️ 공정 배출량 새로고침 실패:', e);
      return null;
    } finally {
      inFlightProcess.current.delete(processId);
    }
  }, []);

  // 제품 배출량 새로고침
  const refreshProductEmission = useCallback(async (productId: number): Promise<any> => {
    if (inFlightProduct.current.has(productId)) return null;
    inFlightProduct.current.add(productId);
    
    try {
      // 실시간 계산된 배출량 가져오기
      let attrEm = 0;
      let hasProduceEdge = false;
      
      try {
        const previewResponse = await axiosClient.get(apiEndpoints.cbam.edgePropagation.productPreview(productId));
        attrEm = previewResponse?.data?.preview_attr_em ?? 0;
        hasProduceEdge = true;
        console.log(`🔍 제품 ${productId} 실시간 배출량 계산: ${attrEm} tCO2e`);
      } catch (previewError) {
        console.warn(`⚠️ 제품 ${productId} 실시간 계산 실패, DB 저장값 사용:`, previewError);
        try {
          const response = await axiosClient.get(apiEndpoints.cbam.product.get(productId));
          const product = response?.data;
          attrEm = product?.attr_em || 0;
          hasProduceEdge = attrEm > 0;
          console.log(`🔍 제품 ${productId} DB 저장값 사용: ${attrEm} tCO2e`);
        } catch (dbError) {
          console.error(`❌ 제품 ${productId} DB 조회도 실패:`, dbError);
          attrEm = 0;
          hasProduceEdge = false;
        }
      }

      // 제품 수량 정보 가져오기
      let productData = null;
      try {
        const productResponse = await axiosClient.get(apiEndpoints.cbam.product.get(productId));
        productData = productResponse?.data;
        console.log(`🔍 제품 ${productId} 최신 수량 정보:`, {
          product_amount: productData?.product_amount,
          product_sell: productData?.product_sell,
          product_eusell: productData?.product_eusell
        });
      } catch (productError) {
        console.warn(`⚠️ 제품 ${productId} 수량 정보 조회 실패:`, productError);
      }

      return {
        attr_em: attrEm,
        has_produce_edge: hasProduceEdge,
        product_amount: Number(productData?.product_amount || 0),
        product_sell: Number(productData?.product_sell || 0),
        product_eusell: Number(productData?.product_eusell || 0),
        productData: {
          attr_em: attrEm,
          production_qty: Number(productData?.product_amount || 0),
          product_sell: Number(productData?.product_sell || 0),
          product_eusell: Number(productData?.product_eusell || 0),
        }
      };
    } catch (e) {
      console.error('⚠️ 제품 배출량 새로고침 실패:', e);
      return null;
    } finally {
      inFlightProduct.current.delete(productId);
    }
  }, []);

  // 전체 그래프 재계산
  const recalculateEntireGraph = useCallback(async (): Promise<boolean> => {
    try {
      await axiosClient.post(apiEndpoints.cbam.calculation.graph.recalc, {
        trigger_edge_id: null,
        include_validation: false
      });
      console.log('✅ 백엔드 전체 그래프 재계산 완료');
      return true;
    } catch (error) {
      console.warn('⚠️ 백엔드 전체 그래프 재계산 실패:', error);
      return false;
    }
  }, []);

  // 공정 기준 재계산
  const recalculateFromProcess = useCallback(async (processId: number): Promise<boolean> => {
    try {
      const resp = await axiosClient.post(
        apiEndpoints.cbam.calculation.process.recalculate(processId)
      );
      
      // 전체 전파 수행
      try {
        await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {});
      } catch (e) {
        console.warn('⚠️ fullPropagate 실패(무시 가능):', e);
      }

      return true;
    } catch (e) {
      console.error('⚠️ 재계산 트리거 실패:', e);
      return false;
    }
  }, []);

  return {
    refreshProcessEmission,
    refreshProductEmission,
    recalculateEntireGraph,
    recalculateFromProcess,
  };
};
