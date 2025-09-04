import { useState, useCallback, useEffect } from 'react';
import { useDummyData } from '@/hooks/useDummyData';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

export interface Install {
  id: number;
  install_name: string;
  reporting_year?: string;
}

export interface Product {
  id: number;
  product_name: string;
  product_category?: string;
  product_amount?: number;
  product_sell?: number;
  product_eusell?: number;
  install_id: number;
  cncode_total?: string;
  goods_name?: string;
  aggrgoods_name?: string;
}

export interface Process {
  id: number;
  process_name: string;
  // 공정 소속 사업장 ID (백엔드 응답 포함)
  install_id?: number;
  // 선택적으로 내려오는 사업장명
  install_name?: string;
  start_period?: string;
  end_period?: string;
  products?: Product[];
}



export const useProcessManager = () => {
  const { getProductQuantity } = useDummyData();
  // 사업장 관련 상태
  const [installs, setInstalls] = useState<Install[]>([]);
  const [selectedInstall, setSelectedInstall] = useState<Install | null>(null);

  // 제품 관련 상태
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // 공정 관련 상태
  const [processes, setProcesses] = useState<Process[]>([]);
  const [allProcesses, setAllProcesses] = useState<Process[]>([]);
  const [crossInstallProcesses, setCrossInstallProcesses] = useState<Process[]>([]);

  // 탐지 상태
  const [isDetectingChains, setIsDetectingChains] = useState(false);
  const [detectionStatus, setDetectionStatus] = useState<string>('');

  // 제품 수량 업데이트 상태
  const [isUpdatingProduct, setIsUpdatingProduct] = useState(false);

  // 사업장 목록 불러오기
  const fetchInstalls = useCallback(async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      setInstalls(response.data);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('사업장 목록 조회 실패:', error);
      }
      setInstalls([]);
    }
  }, []);

  // 선택된 사업장의 제품 목록 불러오기
  const fetchProductsByInstall = useCallback(async (installId: number) => {
    try {
      // install_id로 필터링하여 특정 사업장의 제품만 가져오기
      const response = await axiosClient.get(`${apiEndpoints.cbam.product.list}?install_id=${installId}`);
      const baseProducts: Product[] = response.data || [];

      // 제품 상세(DB)와 더미 생산수량을 병렬 조회하여 풍부화
      const enrichedProducts: Product[] = await Promise.all(
        baseProducts.map(async (p: Product) => {
          const [detail, dummyQty] = await Promise.all([
            (async () => {
              try {
                const detailResp = await axiosClient.get(apiEndpoints.cbam.product.get(p.id));
                return detailResp?.data || {};
              } catch {
                return {} as any;
              }
            })(),
            (async () => {
              try {
                return await getProductQuantity(p.product_name);
              } catch {
                return undefined as unknown as number;
              }
            })()
          ]);

          const amountFromDummy = Number.isFinite(dummyQty as number) ? Number(dummyQty as number) : undefined;
          const product_amount = amountFromDummy ?? Number(detail.product_amount ?? p.product_amount ?? 0);
          const product_sell = Number(detail.product_sell ?? p.product_sell ?? 0);
          const product_eusell = Number(detail.product_eusell ?? p.product_eusell ?? 0);

          return { ...p, product_amount, product_sell, product_eusell } as Product;
        })
      );

      setProducts(enrichedProducts);
      console.log(`✅ 사업장 ${installId}의 제품 ${enrichedProducts.length}개 로드됨(수량 포함)`, enrichedProducts);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('제품 목록 조회 실패:', error);
      }
      setProducts([]);
    }
  }, [getProductQuantity]);

  // 선택된 사업장의 공정 목록 불러오기
  const fetchProcessesByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      const installProducts = products.filter((product: Product) => product.install_id === installId);
      const productIds = installProducts.map((product: Product) => product.id);
      const installProcesses = response.data.filter((process: Process) => 
        process.products && process.products.some((p: Product) => productIds.includes(p.id))
      );
      setProcesses(installProcesses);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('공정 목록 조회 실패:', error);
      }
      setProcesses([]);
    }
  }, [products]);

  // 선택된 사업장의 모든 공정 목록 불러오기
  const fetchAllProcessesByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      const installProducts = products.filter((product: Product) => product.install_id === installId);
      const productIds = installProducts.map((product: Product) => product.id);
      const allProcesses = response.data.filter((process: Process) => 
        process.products && process.products.some((p: Product) => productIds.includes(p.id))
      );
      setAllProcesses(allProcesses);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('전체 공정 목록 조회 실패:', error);
      }
      setAllProcesses([]);
    }
  }, [products]);

  // 크로스 사업장 공정 목록 불러오기
  const fetchAllCrossInstallProcesses = useCallback(async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      const currentInstallProducts = products.filter((product: Product) => product.install_id === selectedInstall?.id);
      const productIds = currentInstallProducts.map((product: Product) => product.id);
      const allCrossProcesses = response.data.filter((process: Process) => 
        process.products && process.products.some((p: Product) => productIds.includes(p.id))
      );
      setCrossInstallProcesses(allCrossProcesses);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('크로스 사업장 공정 목록 조회 실패:', error);
      }
      setCrossInstallProcesses([]);
    }
  }, [products, selectedInstall]);

  // 선택된 제품의 공정 목록 불러오기
  const fetchProcessesByProduct = useCallback(async (productId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      const productProcesses = response.data.filter((process: Process) => 
        process.products && process.products.some((p: Product) => p.id === productId)
      );
      setProcesses(productProcesses);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('제품별 공정 목록 조회 실패:', error);
      }
      setProcesses([]);
    }
  }, []);



  // 제품 수량 업데이트
  const handleProductQuantityUpdate = useCallback(async (productQuantityForm: {
    product_amount: number;
    product_sell: number;
    product_eusell: number;
  }) => {
    if (!selectedProduct) return false;
    
    setIsUpdatingProduct(true);
    try {
      const response = await axiosClient.put(apiEndpoints.cbam.product.update(selectedProduct.id), productQuantityForm);
      
      // 선택된 제품 정보 업데이트
      setSelectedProduct({
        ...selectedProduct,
        ...productQuantityForm
      });

      // 제품 목록 내 해당 아이템도 동기화
      setProducts(prev => prev.map(p => p.id === selectedProduct.id ? { ...p, ...productQuantityForm } : p));
      
      return true;
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('❌ 제품 수량 업데이트 실패:', error);
      }
      return false;
    } finally {
      setIsUpdatingProduct(false);
    }
  }, [selectedProduct]);

  // 사업장 선택 시 제품과 공정 목록 업데이트
  useEffect(() => {
    if (selectedInstall) {
      console.log(`🔄 사업장 선택됨: ${selectedInstall.install_name} (ID: ${selectedInstall.id})`);
      fetchProductsByInstall(selectedInstall.id);
    }
  }, [selectedInstall, fetchProductsByInstall]);

  useEffect(() => {
    if (selectedInstall && products.length > 0) {
      console.log(`🔄 제품 ${products.length}개 로드됨, 공정 목록 로드 시작`);
      const timer = setTimeout(() => {
        fetchProcessesByInstall(selectedInstall.id);
        fetchAllProcessesByInstall(selectedInstall.id);
        fetchAllCrossInstallProcesses();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [selectedInstall, products, fetchProcessesByInstall, fetchAllProcessesByInstall, fetchAllCrossInstallProcesses]);

  // 컴포넌트 마운트 시 사업장 목록 불러오기
  useEffect(() => {
    fetchInstalls();
  }, [fetchInstalls]);

  return {
    // 상태
    installs,
    selectedInstall,
    products,
    selectedProduct,
    processes,
    allProcesses,
    crossInstallProcesses,
    isDetectingChains,
    detectionStatus,
    isUpdatingProduct,

    // 액션
    setSelectedInstall,
    setSelectedProduct,
    fetchProcessesByProduct,
    handleProductQuantityUpdate,
  };
};
