import { useState, useCallback, useEffect } from 'react';
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
  start_period?: string;
  end_period?: string;
  products?: Product[];
}



export const useProcessManager = () => {
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
      setProducts(response.data);
      console.log(`✅ 사업장 ${installId}의 제품 ${response.data.length}개 로드됨:`, response.data);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('제품 목록 조회 실패:', error);
      }
      setProducts([]);
    }
  }, []);

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
