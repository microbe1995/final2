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

  // 선택된 사업장의 모든 공정 목록 불러오기 (제품 연결 여부와 무관하게 install_id 기준)
  const fetchAllProcessesByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      const all = (response.data || []).filter((process: Process) => (process as any)?.install_id === installId);
      setAllProcesses(all);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('전체 공정 목록 조회 실패:', error);
      }
      setAllProcesses([]);
    }
  }, []);

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
    
    // 🔧 추가: 프론트엔드 검증 로직
    const totalSales = productQuantityForm.product_sell + productQuantityForm.product_eusell;
    const nextProcessAmount = productQuantityForm.product_amount - totalSales;
    
    if (totalSales > productQuantityForm.product_amount) {
      console.error('❌ 검증 실패: 판매량 합계가 생산량을 초과합니다');
      return false;
    }
    
    console.log('✅ 제품 수량 검증 통과:');
    console.log(`  생산량: ${productQuantityForm.product_amount} ton`);
    console.log(`  판매량: ${productQuantityForm.product_sell} ton`);
    console.log(`  EU판매량: ${productQuantityForm.product_eusell} ton`);
    console.log(`  다음공정전달량: ${nextProcessAmount} ton`);
    
    setIsUpdatingProduct(true);
    try {
      console.log('🔄 제품 수량 업데이트 시작:', productQuantityForm);
      
      const response = await axiosClient.put(apiEndpoints.cbam.product.update(selectedProduct.id), productQuantityForm);
      
      if (response.status === 200) {
        console.log('✅ 제품 수량 업데이트 성공');
        
        // 서버에서 최신 제품 데이터를 다시 불러와서 상태 동기화
        try {
          const updatedProductResponse = await axiosClient.get(apiEndpoints.cbam.product.get(selectedProduct.id));
          const updatedProduct = updatedProductResponse.data;
          
          // 선택된 제품 정보를 서버 데이터로 업데이트
          setSelectedProduct(updatedProduct);
          console.log('✅ 선택된 제품 정보 동기화 완료:', updatedProduct);

          // 제품 목록 내 해당 아이템도 서버 데이터로 동기화
          setProducts(prev => prev.map(p => p.id === selectedProduct.id ? updatedProduct : p));
          console.log('✅ 제품 목록 동기화 완료');
          
        } catch (syncError) {
          console.warn('⚠️ 제품 데이터 동기화 실패, 로컬 상태로 폴백:', syncError);
          // 동기화 실패 시 로컬 상태로 폴백
          setSelectedProduct({
            ...selectedProduct,
            ...productQuantityForm
          });
          setProducts(prev => prev.map(p => p.id === selectedProduct.id ? { ...p, ...productQuantityForm } : p));
        }
        
        // 🔄 제품 수량 저장 시 백엔드에서 자동으로 배출량 계산 및 저장됨
        // 프론트엔드에서는 캔버스 노드들만 새로고침
        try {
          console.log('🔄 제품 수량 변경으로 인한 캔버스 노드 새로고침 시작');
          
          // 🔧 백엔드 DB 업데이트 완료 대기 후 이벤트 발생
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // 캔버스 노드들 새로고침을 위한 이벤트 발생
          // (useProcessCanvas에서 fullPropagate 실행)
          window.dispatchEvent(new CustomEvent('cbam:refreshAllNodesAfterProductUpdate', {
            detail: { productId: selectedProduct.id }
          }));
          console.log('✅ 캔버스 노드 새로고침 이벤트 발생');
        } catch (refreshError) {
          console.error('❌ 캔버스 노드 새로고침 실패:', refreshError);
          // 새로고침 실패는 제품 수량 업데이트를 실패시키지 않음
        }
        
        return true;
      } else {
        console.error('❌ 제품 수량 업데이트 실패: 응답 상태 코드', response.status);
        return false;
      }
    } catch (error: any) {
      console.error('❌ 제품 수량 업데이트 실패:', error);
      if (error.response) {
        console.error('응답 데이터:', error.response.data);
        console.error('응답 상태:', error.response.status);
      }
      return false;
    } finally {
      setIsUpdatingProduct(false);
    }
  }, [selectedProduct, processes]);

  // 사업장 선택 시 제품과 공정 목록 업데이트
  useEffect(() => {
    if (selectedInstall) {
      console.log(`🔄 사업장 선택됨: ${selectedInstall.install_name} (ID: ${selectedInstall.id})`);
      // 제품은 별도로 불러오고
      fetchProductsByInstall(selectedInstall.id);
    }
  }, [selectedInstall, fetchProductsByInstall]);

  // 선택된 사업장이 바뀌면, 제품 연결 여부와 관계없이 해당 사업장의 전체 공정을 먼저 로드
  useEffect(() => {
    if (selectedInstall) {
      fetchAllProcessesByInstall(selectedInstall.id);
    }
  }, [selectedInstall, fetchAllProcessesByInstall]);

  // 제품이 로드되면 제품-연결 공정 및 크로스 공정도 갱신
  useEffect(() => {
    if (selectedInstall) {
      if (products.length > 0) {
        console.log(`🔄 제품 ${products.length}개 로드됨, 공정 목록 로드 시작`);
        fetchProcessesByInstall(selectedInstall.id);
        fetchAllCrossInstallProcesses();
      } else {
        // 제품이 없으면 제품-연결 공정 목록은 비워두되, install 전체 공정은 이미 위에서 로드됨
        setProcesses([]);
      }
    }
  }, [selectedInstall, products, fetchProcessesByInstall, fetchAllCrossInstallProcesses]);

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
