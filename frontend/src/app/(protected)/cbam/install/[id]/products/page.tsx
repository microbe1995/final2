'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axiosClient from '@/lib/axiosClient';
import { apiEndpoints } from '@/lib/axiosClient';
import { useMappingAPI, HSCNMappingResponse } from '@/hooks/useMappingAPI';
import { useProductNames } from '@/hooks/useProductNames';
import { useDummyData } from '@/hooks/useDummyData';

interface Install {
  id: number;
  install_name: string;
}

interface Product {
  id: number;
  install_id: number;
  product_name: string;
  product_category: string;
  prostart_period: string;
  proend_period: string;
  product_amount: number;
  cncode_total?: string;
  goods_name?: string;
  goods_engname?: string; // 품목영문명 추가
  aggrgoods_name?: string;
  aggrgoods_engname?: string; // 품목군영문명 추가
  product_sell: number;
  product_eusell: number;
  created_at?: string;
  updated_at?: string;
}

interface Process {
  id: number;
  process_name: string;
  start_period?: string;
  end_period?: string;
  created_at?: string;
  updated_at?: string;
  // 🔴 추가: 백엔드에서 반환하는 실제 데이터 구조
  products?: Array<{
    id: number;
    install_id: number;
    product_name: string;
    product_category: string;
    prostart_period: string;
    proend_period: string;
    product_amount: number;
    cncode_total?: string;
    goods_name?: string;
    goods_engname?: string;
    aggrgoods_name?: string;
    aggrgoods_engname?: string;
    product_sell: number;
    product_eusell: number;
    created_at?: string;
    updated_at?: string;
  }>;
}

interface ProductForm {
  product_name: string;
  product_category: string;
  prostart_period: string;
  proend_period: string;
  product_amount: number;
  product_hscode: string; // HS 코드 추가
  cncode_total: string;
  goods_name: string;
  goods_engname: string; // 품목영문명 추가
  aggrgoods_name: string;
  aggrgoods_engname: string; // 품목군영문명 추가
  product_sell: number;
  product_eusell: number;
}

export default function InstallProductsPage() {
  const router = useRouter();
  const params = useParams();
  const installId = parseInt(params.id as string);

  const [products, setProducts] = useState<Product[]>([]);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [showProductForm, setShowProductForm] = useState(false);
  const [showProcessFormForProduct, setShowProcessFormForProduct] = useState<number | null>(null);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  const [productForm, setProductForm] = useState<ProductForm>({
    product_name: '',
    product_category: '',
    prostart_period: '',
    proend_period: '',
    product_amount: 0,
    product_hscode: '', // HS 코드 초기값 추가
    cncode_total: '',
    goods_name: '',
    goods_engname: '', // 품목영문명 초기값 추가
    aggrgoods_name: '',
    aggrgoods_engname: '', // 품목군영문명 초기값 추가
    product_sell: 0,
    product_eusell: 0
  });

  // HS-CN 매핑 API 훅 사용
  const { lookupByHSCode, loading: mappingLoading } = useMappingAPI();
  const [cnCodeResults, setCnCodeResults] = useState<HSCNMappingResponse[]>([]);
  const [showCnCodeResults, setShowCnCodeResults] = useState(false);

  // 제품명 목록 훅 사용 (Railway DB의 dummy 테이블에서 가져옴)
  const { productNames, loading: productNamesLoading, error: productNamesError, fetchProductNamesByPeriod } = useProductNames();
  
  // 🔴 추가: 이미 선택된 제품명들을 추적하는 상태
  const [selectedProductNames, setSelectedProductNames] = useState<Set<string>>(new Set());

  // 모달 상태 관리
  const [showHSCodeModal, setShowHSCodeModal] = useState(false);
  const [hsCodeSearchInput, setHsCodeSearchInput] = useState('');
  const [searchResults, setSearchResults] = useState<HSCNMappingResponse[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [processForm, setProcessForm] = useState<{ process_name: string }>({
    process_name: ''
  });

  // 더미 데이터 훅 사용
  const { getProcessesByProduct, loading: dummyLoading, error: dummyError } = useDummyData();
  const [availableProcesses, setAvailableProcesses] = useState<string[]>([]);
  const [selectedProcess, setSelectedProcess] = useState<string>('');
  
  // 🔴 추가: 제품별 공정 목록 상태 관리
  const [productProcessesMap, setProductProcessesMap] = useState<Map<number, string[]>>(new Map());

  // 사업장별 제품 목록 조회
  const fetchProducts = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      // 현재 사업장의 제품들만 필터링
      const filteredProducts = response.data.filter((product: Product) => product.install_id === installId);
      setProducts(filteredProducts);
    } catch (error: any) {
      console.error('❌ 제품 목록 조회 실패:', error);
    }
  };

  // 제품별 프로세스 목록 조회
  const fetchProcesses = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      console.log('🔍 전체 공정 목록 조회 결과:', response.data);
      setProcesses(response.data);
    } catch (error: any) {
      console.error('❌ 프로세스 목록 조회 실패:', error);
    }
  };

  // 제품별 공정 목록 조회
  const fetchAvailableProcesses = useCallback(async (productName: string, productId: number) => {
    if (!productName) return;
    
    try {
      // 제품명으로만 공정 목록 조회 (기간 필터링 제거)
      const allProcesses = await getProcessesByProduct(productName);
      
      // 이미 제품에 연결된 공정들은 제외 (단, 수정 모드일 때는 현재 선택된 공정은 포함)
      const connectedProcesses = productProcessesMap.get(productId) || [];
      const currentSelectedProcess = processForm.process_name;
      
      const availableProcesses = allProcesses.filter((process: string) => {
        // 수정 모드이고 현재 선택된 공정이면 포함
        if (currentSelectedProcess && process === currentSelectedProcess) {
          return true;
        }
        // 이미 연결된 공정은 제외
        return !connectedProcesses.includes(process);
      });
      
      setAvailableProcesses(availableProcesses);
      console.log(`✅ 제품 '${productName}'의 사용 가능한 공정 목록:`, availableProcesses);
      console.log(`🔍 이미 연결된 공정들:`, connectedProcesses);
      console.log(`🔍 전체 공정 목록:`, allProcesses);
    } catch (error) {
      console.error(`❌ 제품 '${productName}'의 공정 목록 조회 실패:`, error);
      setAvailableProcesses([]);
    }
  }, [getProcessesByProduct, productProcessesMap]);

  // 🔴 수정: 특정 제품의 공정 목록 조회 및 상태 업데이트 (실제 생성된 공정)
  const fetchProductProcesses = useCallback(async (productId: number, productName: string) => {
    try {
      // 실제 생성된 공정 목록에서 해당 제품과 연결된 공정들 찾기
      const productProcesses = processes.filter(process => {
        // process.products 배열에서 해당 제품이 있는지 확인
        if (process.products && Array.isArray(process.products)) {
          return process.products.some(product => product.id === productId);
        }
        return false;
      });
      
      // 공정명만 추출
      const processNames = productProcesses.map(process => process.process_name);
      
      setProductProcessesMap(prev => new Map(prev.set(productId, processNames)));
      console.log(`✅ 제품 ${productName} (ID: ${productId})의 공정 목록 업데이트:`, processNames);
      console.log(`🔍 연결된 공정 상세:`, productProcesses);
    } catch (error) {
      console.error(`❌ 제품 ${productName} (ID: ${productId})의 공정 목록 조회 실패:`, error);
      setProductProcessesMap(prev => new Map(prev.set(productId, [])));
    }
  }, [processes]);

  // 공정 추가 폼 표시 시 해당 제품의 공정 목록 조회
  const handleShowProcessForm = (product: Product) => {
    // 이미 폼이 열려있으면 닫기
    if (showProcessFormForProduct === product.id) {
      setShowProcessFormForProduct(null);
      setSelectedProcess('');
      setAvailableProcesses([]);
      setProcessForm({ process_name: '' });
      return;
    }
    
    // 새로 폼 열기
    setShowProcessFormForProduct(product.id);
    
    // 해당 제품의 공정 목록 조회 (기간 정보 제거)
    if (product.product_name) {
      fetchAvailableProcesses(product.product_name, product.id);
    }
  };

  // 공정 선택 변경 시
  const handleProcessSelectionChange = (processName: string) => {
    setSelectedProcess(processName);
    setProcessForm({ process_name: processName });
  };

  useEffect(() => {
    if (installId) {
      fetchProducts();
      fetchProcesses();
      setIsLoading(false);
    }
  }, [installId]);

  // 🔴 추가: 제품 목록이 로드될 때마다 각 제품의 공정 목록 초기화
  useEffect(() => {
    if (products.length > 0) {
      // 🔴 추가: 기존 제품명들을 선택된 제품명 추적 상태에 추가
      const existingProductNames = new Set(products.map(p => p.product_name));
      setSelectedProductNames(existingProductNames);
      
      products.forEach(async (product) => {
        await fetchProductProcesses(product.id, product.product_name);
      });
    }
  }, [products, fetchProductProcesses]);

  // 🔴 추가: 공정 추가 폼이 열릴 때마다 사용 가능한 공정 목록 새로고침
  useEffect(() => {
    if (showProcessFormForProduct) {
      const product = products.find(p => p.id === showProcessFormForProduct);
      if (product) {
        fetchAvailableProcesses(product.product_name, product.id);
      }
    }
  }, [showProcessFormForProduct, products, fetchAvailableProcesses]);

  // 기간 변경 시 제품명 목록 업데이트 (useEffect 제거, 수동 호출로 변경)
  // useEffect(() => {
  //   if (productForm.prostart_period && productForm.proend_period) {
  //     console.log('🔄 기간 설정 완료, 제품명 목록 업데이트 시작');
  //     fetchProductNamesByPeriod(productForm.prostart_period, productForm.proend_period);
  //   }
  // }, [productForm.prostart_period, productForm.proend_period, fetchProductNamesByPeriod]);

  // 기간 설정 완료 시 수동으로 제품명 목록 업데이트
  const handlePeriodChange = useCallback((field: 'prostart_period' | 'proend_period', value: string) => {
    console.log(`🔄 기간 변경: ${field} = ${value}`);
    
    const newForm = { ...productForm, [field]: value };
    console.log('📅 새로운 폼 상태:', newForm);
    
    // 두 기간이 모두 설정된 경우에만 제품명 조회
    if (newForm.prostart_period && newForm.proend_period) {
      console.log('🔄 기간 설정 완료, 제품명 목록 업데이트 시작');
      console.log('📅 조회할 기간:', newForm.prostart_period, '~', newForm.proend_period);
      
      // API 호출 전 상태 확인
      console.log('🔍 API 호출 전 productNames 상태:', productNames);
      console.log('🔍 API 호출 전 loading 상태:', productNamesLoading);
      
      fetchProductNamesByPeriod(newForm.prostart_period, newForm.proend_period);
    } else {
      console.log('⚠️ 기간이 아직 완전히 설정되지 않음:', {
        start: newForm.prostart_period,
        end: newForm.proend_period
      });
    }
    
    setProductForm(newForm);
  }, [productForm, fetchProductNamesByPeriod, productNames, productNamesLoading]);

  const handleProductInputChange = (field: keyof ProductForm, value: string | number) => {
    setProductForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 제품 폼 초기화
  const resetProductForm = () => {
    setProductForm({
      product_name: '',
      product_category: '',
      prostart_period: '',
      proend_period: '',
      product_amount: 0,
      product_hscode: '',
      cncode_total: '',
      goods_name: '',
      goods_engname: '',
      aggrgoods_name: '',
      aggrgoods_engname: '',
      product_sell: 0,
      product_eusell: 0
    });
    setEditingProduct(null);
    setShowProductForm(false);
  };

  // 제품 수정 모드 시작
  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setProductForm({
      product_name: product.product_name,
      product_category: product.product_category,
      prostart_period: product.prostart_period,
      proend_period: product.proend_period,
      product_amount: product.product_amount,
      product_hscode: '', // HS 코드는 내부적으로만 사용
      cncode_total: product.cncode_total || '',
      goods_name: product.goods_name || '',
      goods_engname: product.goods_engname || '',
      aggrgoods_name: product.aggrgoods_name || '',
      aggrgoods_engname: product.aggrgoods_engname || '',
      product_sell: product.product_sell,
      product_eusell: product.product_eusell
    });
    setShowProductForm(true);
  };

  // 제품 수정 취소
  const handleCancelEditProduct = () => {
    resetProductForm();
  };

  // HS 코드 실시간 검색 함수
  const handleHSCodeSearch = async (searchTerm: string) => {
    if (searchTerm.length < 2) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      // 입력된 HS 코드를 그대로 사용 (패딩하지 않음)
      const results = await lookupByHSCode(searchTerm);
      setSearchResults(results);
    } catch (error) {
      console.error('HS 코드 검색 실패:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // HS 코드 검색 입력 변경 핸들러
  const handleHSCodeSearchInputChange = (value: string) => {
    setHsCodeSearchInput(value);
    // 실시간 검색 (디바운싱 적용)
    const timeoutId = setTimeout(() => {
      handleHSCodeSearch(value);
    }, 300);
    return () => clearTimeout(timeoutId);
  };

  // CN 코드 선택 함수 (모달에서)
  const handleSelectCNCodeFromModal = (result: HSCNMappingResponse) => {
    setProductForm(prev => ({
      ...prev,
      product_hscode: hsCodeSearchInput, // HS 코드는 내부적으로 저장
      cncode_total: result.cncode_total, // CN 코드가 입력 필드에 표시됨
      goods_name: result.goods_name || '',
      goods_engname: result.goods_engname || '', // 품목영문명 저장
      aggrgoods_name: result.aggregoods_name || '',
      aggrgoods_engname: result.aggregoods_engname || '' // 품목군영문명 저장
    }));
    setShowHSCodeModal(false);
    setHsCodeSearchInput('');
    setSearchResults([]);
  };

  // 모달 열기 함수
  const openHSCodeModal = () => {
    setShowHSCodeModal(true);
    setHsCodeSearchInput('');
    setSearchResults([]);
  };

  const handleProductSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!productForm.product_name || !productForm.prostart_period || !productForm.proend_period) {
      setToast({
        message: '필수 필드를 모두 입력해주세요.',
        type: 'error'
      });
      return;
    }

    try {
      // 백엔드 스키마에 맞게 데이터 변환
      const productData = {
        install_id: installId,
        product_name: productForm.product_name,
        product_category: productForm.product_category || '단순제품', // 기본값 설정
        prostart_period: productForm.prostart_period, // date 형식으로 전송
        proend_period: productForm.proend_period, // date 형식으로 전송
        product_amount: parseFloat(productForm.product_amount.toString()) || 0, // float로 변환
        cncode_total: productForm.cncode_total || null,
        goods_name: productForm.goods_name || null,
        goods_engname: productForm.goods_engname || null,
        aggrgoods_name: productForm.aggrgoods_name || null,
        aggrgoods_engname: productForm.aggrgoods_engname || null,
        product_sell: parseFloat(productForm.product_sell.toString()) || 0, // float로 변환
        product_eusell: parseFloat(productForm.product_eusell.toString()) || 0 // float로 변환
      };

      if (editingProduct) {
        // 수정
        const response = await axiosClient.put(apiEndpoints.cbam.product.update(editingProduct.id), productData);
        console.log('✅ 제품 수정 성공:', response.data);
        
        // 🔴 추가: 기존 제품명 제거하고 새 제품명 추가
        setSelectedProductNames(prev => {
          const newSet = new Set(prev);
          newSet.delete(editingProduct.product_name);
          newSet.add(productForm.product_name);
          return newSet;
        });
        
        setToast({
          message: '제품이 성공적으로 수정되었습니다.',
          type: 'success'
        });
      } else {
        // 생성
        const response = await axiosClient.post(apiEndpoints.cbam.product.create, productData);
        console.log('✅ 제품 생성 성공:', response.data);
        
        // 🔴 추가: 선택된 제품명을 추적 상태에 추가
        setSelectedProductNames(prev => new Set(prev).add(productForm.product_name));
        
        setToast({
          message: '제품이 성공적으로 생성되었습니다.',
          type: 'success'
        });
      }

      // 폼 초기화 및 숨기기
      resetProductForm();

      // 목록 새로고침
      fetchProducts();
    } catch (error: any) {
      console.error('❌ 제품 저장 실패:', error);
      setToast({
        message: `제품 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleProcessSubmit = async (e: React.FormEvent, productId: number) => {
    e.preventDefault();
    
    if (!processForm.process_name) {
      setToast({
        message: '공정명을 입력해주세요.',
        type: 'error'
      });
      return;
    }

    try {
      // 백엔드 스키마에 맞게 데이터 변환
      const processData = {
        process_name: processForm.process_name,
        start_period: null, // 선택적 필드
        end_period: null,   // 선택적 필드
        product_ids: [productId]  // 다대다 관계를 위해 배열로 전송
      };

      console.log('🔍 전송할 공정 데이터:', processData);

      let response;
      
      // 🔴 수정: 수정 모드인지 추가 모드인지 구분하여 처리
      if (selectedProcess && showProcessFormForProduct) {
        // 수정 모드: 기존 공정 업데이트
        console.log('🔧 공정 수정 모드:', selectedProcess, '→', processForm.process_name);
        
        // 기존 공정 ID 찾기
        const existingProcess = processes.find(p => p.process_name === selectedProcess);
        if (existingProcess) {
          // 공정명만 업데이트
          response = await axiosClient.put(apiEndpoints.cbam.process.update(existingProcess.id), {
            process_name: processForm.process_name
          });
          console.log('✅ 공정 수정 성공:', response.data);
          setToast({
            message: `공정이 "${selectedProcess}"에서 "${processForm.process_name}"으로 수정되었습니다.`,
            type: 'success'
          });
        } else {
          throw new Error('수정할 공정을 찾을 수 없습니다.');
        }
      } else {
        // 추가 모드: 새 공정 생성
        console.log('➕ 공정 추가 모드');
        console.log('🔍 API 엔드포인트:', apiEndpoints.cbam.process.create);
        
        response = await axiosClient.post(apiEndpoints.cbam.process.create, processData);
        console.log('✅ 프로세스 생성 성공:', response.data);
        
        setToast({
          message: '프로세스가 성공적으로 생성되었습니다.',
          type: 'success'
        });
      }

      // 폼 초기화 및 숨기기
      setProcessForm({
        process_name: ''
      });
      setSelectedProcess('');
      setAvailableProcesses([]);
      setShowProcessFormForProduct(null);

      // 목록 새로고침
      await fetchProcesses();
      
      // 🔴 수정: 해당 제품의 공정 목록 새로고침
      if (showProcessFormForProduct) {
        const product = products.find(p => p.id === showProcessFormForProduct);
        if (product) {
          // 제품별 공정 목록 업데이트
          await fetchProductProcesses(product.id, product.product_name);
        }
      }
      
      console.log('🔄 공정 목록 새로고침 완료');
    } catch (error: any) {
      console.error('❌ 프로세스 처리 실패:', error);
      console.error('❌ 에러 응답 데이터:', error.response?.data);
      console.error('❌ 에러 상태 코드:', error.response?.status);
      setToast({
        message: `프로세스 처리에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleDeleteProduct = async (productId: number, productName: string) => {
    if (!confirm(`"${productName}" 제품을 삭제하시겠습니까?\n\n⚠️ 주의: 이 제품과 연결된 모든 프로세스가 함께 삭제됩니다.`)) {
      return;
    }

    try {
      await axiosClient.delete(apiEndpoints.cbam.product.delete(productId));
      console.log('✅ 제품 삭제 성공');
      
      // 🔴 추가: 선택된 제품명에서 제거
      setSelectedProductNames(prev => {
        const newSet = new Set(prev);
        newSet.delete(productName);
        return newSet;
      });
      
      setToast({
        message: `"${productName}" 제품이 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchProducts();
      fetchProcesses();
    } catch (error: any) {
      console.error('❌ 제품 삭제 실패:', error);
      setToast({
        message: `제품 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  const handleDeleteProcess = async (processId: number, processName: string) => {
    if (!confirm(`"${processName}" 프로세스를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await axiosClient.delete(apiEndpoints.cbam.process.delete(processId));
      console.log('✅ 프로세스 삭제 성공');
      
      setToast({
        message: `"${processName}" 프로세스가 성공적으로 삭제되었습니다.`,
        type: 'success'
      });

      fetchProcesses();
    } catch (error: any) {
      console.error('❌ 프로세스 삭제 실패:', error);
      setToast({
        message: `프로세스 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    }
  };

  // 🔴 추가: 공정 수정 모드 시작
  const handleEditProcess = (processName: string, productId: number) => {
    console.log('🔧 공정 수정 모드 시작:', processName, '제품 ID:', productId);
    
    // 공정 수정 폼을 표시하고 해당 공정 정보를 설정
    setShowProcessFormForProduct(productId);
    setSelectedProcess(processName);
    setProcessForm({ process_name: processName });
    
    // 해당 제품의 사용 가능한 공정 목록 새로고침 (수정 모드)
    const product = products.find(p => p.id === productId);
    if (product) {
      fetchAvailableProcesses(product.product_name, productId);
    }
  };

  // 🔴 추가: 공정명으로 공정 삭제 (제품별 공정 목록에서)
  const handleDeleteProcessByName = async (processName: string, productId: number) => {
    if (!confirm(`"${processName}" 공정을 삭제하시겠습니까?`)) return;

    try {
      setIsLoading(true);
      
      // 공정명으로 공정 ID 찾기
      const process = processes.find(p => p.process_name === processName);
      if (process) {
        await axiosClient.delete(apiEndpoints.cbam.process.delete(process.id));
        console.log('✅ 공정 삭제 성공');
        setToast({
          message: '공정이 성공적으로 삭제되었습니다!',
          type: 'success'
        });
        
                 // 공정 목록 새로고침
         await fetchProcesses();
         
         // 해당 제품의 공정 목록 새로고침
         const product = products.find(p => p.id === productId);
         if (product) {
           await fetchProductProcesses(product.id, product.product_name);
         }
      } else {
        setToast({
          message: '삭제할 공정을 찾을 수 없습니다.',
          type: 'error'
        });
      }
    } catch (error: any) {
      console.error('❌ 공정 삭제 실패:', error);
      setToast({
        message: `공정 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-300 mt-4">데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* 토스트 메시지 */}
        {toast && (
          <div className={`mb-4 p-4 rounded-lg ${
            toast.type === 'success' ? 'bg-green-600' : 
            toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
          }`}>
            {toast.message}
          </div>
        )}

        {/* HS 코드 검색 모달 */}
        {showHSCodeModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-2xl mx-4 shadow-2xl">
              {/* 모달 헤더 */}
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white">HS코드로 CN코드 검색</h3>
                <button
                  onClick={() => setShowHSCodeModal(false)}
                  className="text-gray-400 hover:text-white text-xl transition-colors"
                >
                  ×
                </button>
              </div>

              {/* 검색 입력 필드 */}
              <div className="mb-4">
                <input
                  type="text"
                  value={hsCodeSearchInput}
                  onChange={(e) => handleHSCodeSearchInputChange(e.target.value)}
                  placeholder="HS 코드를 입력하세요"
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  autoFocus
                />
              </div>

              {/* 검색 결과 */}
              <div className="max-h-96 overflow-y-auto">
                {isSearching && (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="text-gray-300 mt-2">검색 중...</p>
                  </div>
                )}

                {!isSearching && searchResults.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">검색 결과 ({searchResults.length}개)</h4>
                    {searchResults.map((result, index) => (
                      <div
                        key={index}
                        onClick={() => handleSelectCNCodeFromModal(result)}
                        className="p-3 border border-gray-600 rounded-md cursor-pointer hover:bg-gray-700 transition-colors"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="text-sm font-medium text-blue-400">{result.cncode_total}</div>
                            <div className="text-xs text-gray-300 mt-1">{result.goods_name}</div>
                            <div className="text-xs text-gray-400">{result.aggregoods_name}</div>
                          </div>
                          <div className="text-xs text-gray-500 ml-2">선택</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {!isSearching && hsCodeSearchInput.length >= 2 && searchResults.length === 0 && (
                  <div className="text-center py-4">
                    <p className="text-gray-400">검색 결과가 없습니다.</p>
                  </div>
                )}

                {hsCodeSearchInput.length < 2 && (
                  <div className="text-center py-4">
                    <p className="text-gray-400">HS 코드를 2자리 이상 입력해주세요.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 제품 관리 섹션 */}
        <div className="space-y-6">
          {/* 제품 생성/수정 폼 */}
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">📦 제품 관리</h2>
              <button
                onClick={() => {
                  if (showProductForm) {
                    resetProductForm();
                  } else {
                    setShowProductForm(true);
                  }
                }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors duration-200"
              >
                {showProductForm ? '취소' : '제품 추가'}
              </button>
            </div>

            {showProductForm && (
              <form onSubmit={handleProductSubmit} className="space-y-4">
                {/* 기간 설정을 먼저 배치 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">기간 시작일 *</label>
                    <input
                      type="date"
                      value={productForm.prostart_period}
                      onChange={(e) => handlePeriodChange('prostart_period', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">기간 종료일 *</label>
                    <input
                      type="date"
                      value={productForm.proend_period}
                      onChange={(e) => handlePeriodChange('proend_period', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>

                {/* 기간별 제품명 안내 메시지 */}
                {(productForm.prostart_period || productForm.proend_period) && (
                  <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-md">
                    <p className="text-sm text-blue-300">
                      📅 <strong>기간 설정 완료:</strong> {productForm.prostart_period || '시작일 미설정'} ~ {productForm.proend_period || '종료일 미설정'}
                    </p>
                    <p className="text-xs text-blue-400 mt-1">
                      이제 아래에서 해당 기간에 생산되는 제품명을 선택할 수 있습니다.
                    </p>
                  </div>
                )}

                {/* 제품명 선택 (기간 설정 후 활성화) */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    제품명 * 
                    {(!productForm.prostart_period || !productForm.proend_period) && (
                      <span className="text-yellow-400 text-xs ml-2">(기간을 먼저 설정해주세요)</span>
                    )}
                  </label>
                  <select
                    value={productForm.product_name}
                    onChange={(e) => handleProductInputChange('product_name', e.target.value)}
                    onFocus={() => {
                      // 드롭다운 클릭 시에만 데이터 로드
                      if (productForm.prostart_period && productForm.proend_period && productNames.length === 0) {
                        console.log('🔄 드롭다운 클릭, 제품명 목록 로드 시작');
                        fetchProductNamesByPeriod(productForm.prostart_period, productForm.proend_period);
                      }
                    }}
                    className={`w-full px-3 py-2 border rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      (!productForm.prostart_period || !productForm.proend_period) 
                        ? 'bg-gray-700/50 border-gray-500 cursor-not-allowed' 
                        : 'bg-gray-800/50 border-gray-600'
                    }`}
                    required
                    disabled={productNamesLoading || !productForm.prostart_period || !productForm.proend_period}
                  >
                    <option value="">
                      {(!productForm.prostart_period || !productForm.proend_period) 
                        ? '기간을 먼저 설정해주세요' 
                        : productNamesLoading 
                          ? '제품명 목록을 불러오는 중...'
                          : '제품명을 선택하세요'
                      }
                    </option>
                    {productNames
                      .filter(name => !selectedProductNames.has(name)) // 🔴 추가: 이미 선택된 제품명 제외
                      .map((name) => (
                        <option key={name} value={name}>{name}</option>
                      ))}
                  </select>
                  
                  {/* 기간별 필터링 정보 표시 */}
                  {(productForm.prostart_period && productForm.proend_period) && (
                    <div className="mt-2 p-2 bg-green-500/10 border border-green-500/20 rounded-md">
                      <p className="text-xs text-green-300">
                        ✅ 해당 기간에 생산된 제품명 {productNames.length}개가 표시됩니다
                        {selectedProductNames.size > 0 && (
                          <span className="block text-yellow-300 mt-1">
                            🔒 이미 선택된 제품명 {selectedProductNames.size}개는 제외됨
                          </span>
                        )}
                      </p>
                    </div>
                  )}
                  
                  {productNamesLoading && (
                    <p className="text-xs text-gray-400 mt-1">제품명 목록을 불러오는 중...</p>
                  )}
                  {productNamesError && (
                    <p className="text-xs text-red-400 mt-1">제품명 목록 로드 실패: {productNamesError}</p>
                  )}
                  {productNames.length === 0 && !productNamesLoading && !productNamesError && productForm.prostart_period && productForm.proend_period && (
                    <p className="text-xs text-yellow-400 mt-1">해당 기간에 생산된 제품명이 없습니다.</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">제품 카테고리</label>
                  <select
                    value={productForm.product_category}
                    onChange={(e) => handleProductInputChange('product_category', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">카테고리를 선택하세요</option>
                    <option value="단순제품">단순제품</option>
                    <option value="복합제품">복합제품</option>
                  </select>
                </div>

                {/* CN 코드 입력 필드 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">CN 코드</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={productForm.cncode_total}
                        onChange={(e) => handleProductInputChange('cncode_total', e.target.value)}
                        className="flex-1 px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="HS CODE 검색 후 자동 입력"
                        readOnly
                      />
                      <button
                        type="button"
                        onClick={openHSCodeModal}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors duration-200"
                      >
                        HS CODE 검색
                      </button>
                    </div>
                  </div>

                  {/* CN 코드 및 품목 정보 표시 */}
                  {productForm.cncode_total && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-md p-3">
                      <h4 className="text-sm font-medium text-green-300 mb-2">✅ 선택된 CN 코드:</h4>
                      <div className="space-y-1">
                        <div className="text-sm text-white">CN 코드: <span className="font-medium">{productForm.cncode_total}</span></div>
                        {productForm.goods_name && (
                          <div className="text-xs text-gray-300">품목명: {productForm.goods_name}</div>
                        )}
                        {productForm.goods_engname && (
                          <div className="text-xs text-gray-400">품목영문명: {productForm.goods_engname}</div>
                        )}
                        {productForm.aggrgoods_name && (
                          <div className="text-xs text-gray-300">품목군명: {productForm.aggrgoods_name}</div>
                        )}
                        {productForm.aggrgoods_engname && (
                          <div className="text-xs text-gray-400">품목군영문명: {productForm.aggrgoods_engname}</div>
                        )}
                      </div>
                    </div>
                  )}

                <div className="flex gap-4">
                  {editingProduct && (
                    <button
                      type="button"
                      onClick={handleCancelEditProduct}
                      className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors duration-200"
                    >
                      취소
                    </button>
                  )}
                  <button
                    type="submit"
                    className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
                  >
                    📦 {editingProduct ? '제품 수정' : '제품 생성'}
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* 제품 목록 */}
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">📋 등록된 제품 목록 ({products.length}개)</h3>
            
            {products.length === 0 ? (
              <p className="text-gray-300 text-center py-4">등록된 제품이 없습니다.</p>
            ) : (
              <div className="space-y-6">
                {products.map((product) => {
                  // 🔴 수정: 제품별 공정 목록을 productProcessesMap에서 가져오기
                  const productProcesses = productProcessesMap.get(product.id) || [];
                  const isShowingProcessForm = showProcessFormForProduct === product.id;
                  
                  return (
                    <div key={product.id} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                       <div className="flex justify-between items-start mb-2">
                         <h4 className="text-white font-semibold text-lg">{product.product_name}</h4>
                         
                         {/* 🔴 추가: 오른쪽 상단에 공정 관련 버튼들 배치 */}
                         <div className="flex gap-2">
                           {/* 공정 추가/취소 버튼 */}
                           <button
                             onClick={() => handleShowProcessForm(product)}
                             className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                           >
                             {showProcessFormForProduct === product.id ? '공정 취소' : '공정 추가'}
                           </button>
                           
                           {/* 제품 수정 버튼 */}
                           <button
                             onClick={() => handleEditProduct(product)}
                             className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                           >
                             수정
                           </button>
                           
                           {/* 제품 삭제 버튼 */}
                           <button
                             onClick={() => handleDeleteProduct(product.id, product.product_name)}
                             className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                           >
                             삭제
                           </button>
                         </div>
                       </div>
                      
                      <div className="space-y-1 mb-3">
                        <p className="text-gray-300 text-sm">기간: {product.prostart_period} ~ {product.proend_period}</p>
                        <p className="text-gray-300 text-sm">수량: {product.product_amount.toLocaleString()}</p>
                        <p className="text-gray-300 text-sm">공정 수: {productProcessesMap.get(product.id)?.length || 0}개</p>
                        {product.product_category && (
                          <p className="text-gray-300 text-sm">카테고리: <span className="text-blue-300">{product.product_category}</span></p>
                        )}
                                                 {product.cncode_total && (
                           <div className="mt-2 p-2 bg-blue-500/10 rounded border border-blue-500/20">
                             <p className="text-blue-300 text-sm">CN 코드: <span className="font-medium">{product.cncode_total}</span></p>
                             {product.goods_name && (
                               <p className="text-gray-300 text-xs">품목명: {product.goods_name}</p>
                             )}
                             {product.goods_engname && (
                               <p className="text-gray-400 text-xs">품목영문명: {product.goods_engname}</p>
                             )}
                             {product.aggrgoods_name && (
                               <p className="text-gray-300 text-xs">품목군명: {product.aggrgoods_name}</p>
                             )}
                             {product.aggrgoods_engname && (
                               <p className="text-gray-400 text-xs">품목군영문명: {product.aggrgoods_engname}</p>
                             )}
                           </div>
                         )}
                      </div>

                      {/* 공정 목록 */}
                      {productProcessesMap.get(product.id) && productProcessesMap.get(product.id)!.length > 0 && (
                        <div className="mb-4 p-3 bg-white/5 rounded-lg">
                          <h5 className="text-sm font-medium text-white mb-2">📋 등록된 공정:</h5>
                          <div className="space-y-2">
                             {productProcessesMap.get(product.id)!.map((processName, index) => (
                               <div key={index} className="flex justify-between items-center p-2 bg-white/5 rounded">
                                 <span className="text-gray-300 text-sm">{processName}</span>
                                 <div className="flex gap-1">
                                   <button
                                     onClick={() => handleEditProcess(processName, product.id)}
                                     className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                                   >
                                     🔧 수정
                                   </button>
                                   <button
                                     onClick={() => handleDeleteProcessByName(processName, product.id)}
                                     className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                                   >
                                     🗑️ 삭제
                                   </button>
                                 </div>
                               </div>
                             ))}
                          </div>
                        </div>
                      )}

                                             {/* 공정 추가/수정 폼 */}
                       {isShowingProcessForm && (
                         <div className="mb-4 p-4 bg-white/5 rounded-lg border border-purple-500/30">
                           <h5 className="text-sm font-medium text-white mb-3">
                             {selectedProcess && showProcessFormForProduct === product.id 
                               ? '🔧 공정 수정' 
                               : '➕ 공정 추가'
                             }
                           </h5>
                          
                                                     {/* 더미 데이터에서 가져온 공정 목록 안내 */}
                           {availableProcesses.length > 0 ? (
                             <div className="mb-3 p-2 bg-blue-500/10 border border-blue-500/20 rounded-md">
                               <p className="text-xs text-blue-300">
                                 📋 <strong>사용 가능한 공정:</strong> {availableProcesses.length}개
                               </p>
                               <p className="text-xs text-blue-400 mt-1">
                                 아래 드롭다운에서 해당 제품에 적합한 공정을 선택해주세요.
                               </p>
                             </div>
                           ) : (
                             <div className="mb-3 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
                               <p className="text-xs text-yellow-300">
                                 ⚠️ <strong>사용 가능한 공정이 없습니다.</strong>
                               </p>
                               <p className="text-xs text-yellow-400 mt-1">
                                 {productProcessesMap.get(product.id) && productProcessesMap.get(product.id)!.length > 0 
                                   ? '이미 모든 공정이 연결되어 있습니다.' 
                                   : '더미 데이터에서 해당 제품의 공정 정보를 찾을 수 없습니다.'
                                 }
                               </p>
                             </div>
                           )}
                          
                          <form onSubmit={(e) => handleProcessSubmit(e, product.id)} className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-300 mb-1">공정명 *</label>
                              
                              {/* 더미 데이터 공정 드롭다운 (필수) */}
                              <select
                                value={selectedProcess}
                                onChange={(e) => handleProcessSelectionChange(e.target.value)}
                                className={`w-full px-3 py-2 border rounded-md text-white focus:outline-none focus:ring-2 focus:ring-purple-500 ${
                                  availableProcesses.length > 0 
                                    ? 'bg-gray-800/50 border-gray-600' 
                                    : 'bg-gray-700/50 border-gray-500 cursor-not-allowed'
                                }`}
                                required
                                disabled={availableProcesses.length === 0}
                              >
                                <option value="">
                                  {selectedProcess && showProcessFormForProduct === product.id
                                    ? `현재: ${selectedProcess}`
                                    : availableProcesses.length > 0 
                                      ? '공정을 선택하세요' 
                                      : '사용 가능한 공정이 없습니다'
                                  }
                                </option>
                                {availableProcesses.map((process) => (
                                  <option key={process} value={process}>{process}</option>
                                ))}
                              </select>
                              
                              {/* 로딩 및 에러 상태 표시 */}
                              {dummyLoading && (
                                <p className="text-xs text-gray-400 mt-1">공정 목록을 불러오는 중...</p>
                              )}
                              {dummyError && (
                                <p className="text-xs text-red-400 mt-1">공정 목록 로드 실패: {dummyError}</p>
                              )}
                              
                              {/* 공정이 없을 때 안내 메시지 */}
                              {!dummyLoading && !dummyError && availableProcesses.length === 0 && (
                                <p className="text-xs text-yellow-400 mt-1">
                                  해당 제품의 공정 정보가 더미 데이터에 등록되어 있지 않습니다.
                                </p>
                              )}
                            </div>
                            
                            <div className="flex gap-2">
                                                             <button
                                 type="submit"
                                 disabled={!selectedProcess || availableProcesses.length === 0}
                                 className={`flex-1 px-4 py-2 text-white text-sm font-medium rounded-md transition-colors duration-200 ${
                                   selectedProcess && availableProcesses.length > 0
                                     ? 'bg-purple-600 hover:bg-purple-700'
                                     : 'bg-gray-500 cursor-not-allowed'
                                 }`}
                               >
                                 ➕ 공정 추가
                               </button>
                             </div>
                          </form>
                        </div>
                      )}

                      
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
