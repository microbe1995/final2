'use client';

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import InstallProductsPage from '@/app/(protected)/cbam/install/[id]/products/page';
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
  goods_engname?: string;
  aggrgoods_name?: string;
  aggrgoods_engname?: string;
  product_sell: number;
  product_eusell: number;
  created_at?: string;
  updated_at?: string;
}

interface Process {
  id: number;
  process_name: string;
  install_id?: number;
  install_name?: string;
  start_period?: string;
  end_period?: string;
  created_at?: string;
  updated_at?: string;
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
  product_hscode: string;
  cncode_total: string;
  goods_name: string;
  goods_engname: string;
  aggrgoods_name: string;
  aggrgoods_engname: string;
  product_sell: number;
  product_eusell: number;
}

interface ProductManagerProps {
  installId: number;
  embedded?: boolean;
  onClose?: () => void;
}

export default function ProductManager({ installId, embedded = true }: ProductManagerProps) {
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
    product_hscode: '',
    cncode_total: '',
    goods_name: '',
    goods_engname: '',
    aggrgoods_name: '',
    aggrgoods_engname: '',
    product_sell: 0,
    product_eusell: 0,
  });

  const { lookupByHSCode, loading: mappingLoading } = useMappingAPI();
  const [cnCodeResults, setCnCodeResults] = useState<HSCNMappingResponse[]>([]);
  const [showCnCodeResults, setShowCnCodeResults] = useState(false);

  const { productNames, loading: productNamesLoading, error: productNamesError, fetchProductNamesByPeriod } = useProductNames();
  const [selectedProductNames, setSelectedProductNames] = useState<Set<string>>(new Set());

  const [showHSCodeModal, setShowHSCodeModal] = useState(false);
  const [hsCodeSearchInput, setHsCodeSearchInput] = useState('');
  const [searchResults, setSearchResults] = useState<HSCNMappingResponse[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [processForm, setProcessForm] = useState<{ process_name: string }>({
    process_name: '',
  });

  const { getProcessesByProduct, loading: dummyLoading, error: dummyError } = useDummyData();
  const [availableProcesses, setAvailableProcesses] = useState<string[]>([]);
  const [selectedProcess, setSelectedProcess] = useState<string>('');
  const [isEditingProcess, setIsEditingProcess] = useState<boolean>(false);

  const [productProcessesMap, setProductProcessesMap] = useState<Map<number, string[]>>(new Map());
  const [installProcessesMap, setInstallProcessesMap] = useState<Map<number, string[]>>(new Map());
  const [installs, setInstalls] = useState<Install[]>([]);
  const [selectedInstallForProcess, setSelectedInstallForProcess] = useState<number | ''>('');

  const fetchProducts = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      const filteredProducts = response.data.filter((product: Product) => product.install_id === installId);
      setProducts(filteredProducts);
    } catch (error: any) {
      console.error('❌ 제품 목록 조회 실패:', error);
    }
  };

  const fetchProcessesByInstall = useCallback(async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      const installProcessMap = new Map<number, string[]>();
      response.data.forEach((process: any) => {
        const iid = process.install_id;
        if (!iid) return;
        if (!installProcessMap.has(iid)) {
          installProcessMap.set(iid, []);
        }
        installProcessMap.get(iid)!.push(process.process_name);
      });
      setInstallProcessesMap(installProcessMap);
    } catch (error: any) {
      console.error('❌ 사업장별 공정 목록 조회 실패:', error);
    }
  }, []);

  const fetchInstalls = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      setInstalls(response.data);
    } catch (error: any) {
      console.error('❌ 사업장 목록 조회 실패:', error);
    }
  };

  const fetchProcesses = async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      setProcesses(response.data);
      const updatedMap = new Map<number, string[]>();
      products.forEach((product) => {
        const productProcesses = response.data.filter((proc: any) =>
          Array.isArray(proc.products) && proc.products.some((p: any) => p.id === product.id)
        );
        updatedMap.set(product.id, productProcesses.map((p: any) => p.process_name));
      });
      setProductProcessesMap(updatedMap);
    } catch (error: any) {
      console.error('❌ 프로세스 목록 조회 실패:', error);
    }
  };

  const fetchAvailableProcesses = useCallback(
    async (productName: string, productId: number) => {
      if (!productName) return;
      try {
        const allProcesses = await getProcessesByProduct(productName);
        const connectedProcesses = productProcessesMap.get(productId) || [];
        const currentSelectedProcess = processForm.process_name;
        const available = allProcesses.filter((process: string) => {
          if (currentSelectedProcess && process === currentSelectedProcess) {
            return true;
          }
          return !connectedProcesses.includes(process);
        });
        setAvailableProcesses(available);
      } catch (error) {
        console.error(`❌ 제품 '${productName}'의 공정 목록 조회 실패:`, error);
        setAvailableProcesses([]);
      }
    },
    [getProcessesByProduct, productProcessesMap]
  );

  const fetchProductProcesses = useCallback(
    async (productId: number, productName: string) => {
      try {
        const productProcesses = processes.filter((process) => {
          if (process.products && Array.isArray(process.products)) {
            return process.products.some((product) => product.id === productId);
          }
          return false;
        });
        const processNames = productProcesses.map((process) => process.process_name);
        setProductProcessesMap((prev) => new Map(prev.set(productId, processNames)));
      } catch (error) {
        console.error(`❌ 제품 ${productName} (ID: ${productId})의 공정 목록 조회 실패:`, error);
        setProductProcessesMap((prev) => new Map(prev.set(productId, [])));
      }
    },
    [processes]
  );

  const handleShowProcessForm = (product: Product) => {
    if (showProcessFormForProduct === product.id) {
      setShowProcessFormForProduct(null);
      setSelectedProcess('');
      setAvailableProcesses([]);
      setProcessForm({ process_name: '' });
      setSelectedInstallForProcess('');
      setIsEditingProcess(false);
      return;
    }
    setShowProcessFormForProduct(product.id);
    setIsEditingProcess(false);
    if (product.product_name) {
      fetchAvailableProcesses(product.product_name, product.id);
    }
  };

  const handleProcessSelectionChange = (processName: string) => {
    setSelectedProcess(processName);
    setProcessForm({ process_name: processName });
  };

  useEffect(() => {
    if (installId) {
      fetchProducts();
      fetchProcesses();
      fetchInstalls();
      setIsLoading(false);
    }
  }, [installId]);

  useEffect(() => {
    if (products.length > 0) {
      const existingProductNames = new Set(products.map((p) => p.product_name));
      setSelectedProductNames(existingProductNames);
      products.forEach(async (product) => {
        await fetchProductProcesses(product.id, product.product_name);
      });
    }
  }, [products, fetchProductProcesses]);

  useEffect(() => {
    if (showProcessFormForProduct) {
      const product = products.find((p) => p.id === showProcessFormForProduct);
      if (product) {
        fetchAvailableProcesses(product.product_name, product.id);
      }
      fetchInstalls();
      fetchProcessesByInstall();
    }
  }, [showProcessFormForProduct, products, fetchAvailableProcesses, fetchProcessesByInstall]);

  const handlePeriodChange = useCallback(
    (field: 'prostart_period' | 'proend_period', value: string) => {
      const newForm = { ...productForm, [field]: value };
      if (newForm.prostart_period && newForm.proend_period) {
        fetchProductNamesByPeriod(newForm.prostart_period, newForm.proend_period);
      }
      setProductForm(newForm);
    },
    [productForm, fetchProductNamesByPeriod]
  );

  const handleProductInputChange = (field: keyof ProductForm, value: string | number) => {
    setProductForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

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
      product_eusell: 0,
    });
    setEditingProduct(null);
    setShowProductForm(false);
  };

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setProductForm({
      product_name: product.product_name,
      product_category: product.product_category,
      prostart_period: product.prostart_period,
      proend_period: product.proend_period,
      product_amount: product.product_amount,
      product_hscode: '',
      cncode_total: product.cncode_total || '',
      goods_name: product.goods_name || '',
      goods_engname: product.goods_engname || '',
      aggrgoods_name: product.aggrgoods_name || '',
      aggrgoods_engname: product.aggrgoods_engname || '',
      product_sell: product.product_sell,
      product_eusell: product.product_eusell,
    });
    setShowProductForm(true);
  };

  const handleCancelEditProduct = () => {
    resetProductForm();
  };

  const handleHSCodeSearch = async (searchTerm: string) => {
    if (searchTerm.length < 2) {
      setSearchResults([]);
      return;
    }
    setIsSearching(true);
    try {
      const results = await lookupByHSCode(searchTerm);
      setSearchResults(results);
    } catch (error) {
      console.error('HS 코드 검색 실패:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleHSCodeSearchInputChange = (value: string) => {
    setHsCodeSearchInput(value);
    const timeoutId = setTimeout(() => {
      handleHSCodeSearch(value);
    }, 300);
    return () => clearTimeout(timeoutId);
  };

  const handleSelectCNCodeFromModal = (result: HSCNMappingResponse) => {
    setProductForm((prev) => ({
      ...prev,
      product_hscode: hsCodeSearchInput,
      cncode_total: result.cncode_total,
      goods_name: result.goods_name || '',
      goods_engname: result.goods_engname || '',
      aggrgoods_name: result.aggregoods_name || '',
      aggrgoods_engname: result.aggregoods_engname || '',
    }));
    setShowHSCodeModal(false);
    setHsCodeSearchInput('');
    setSearchResults([]);
  };

  const openHSCodeModal = () => {
    setShowHSCodeModal(true);
    setHsCodeSearchInput('');
    setSearchResults([]);
  };

  const handleProductSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productForm.product_name || !productForm.prostart_period || !productForm.proend_period) {
      setToast({ message: '필수 필드를 모두 입력해주세요.', type: 'error' });
      return;
    }
    try {
      const productData = {
        install_id: installId,
        product_name: productForm.product_name,
        product_category: productForm.product_category || '단순제품',
        prostart_period: productForm.prostart_period,
        proend_period: productForm.proend_period,
        product_amount: parseFloat(productForm.product_amount.toString()) || 0,
        cncode_total: productForm.cncode_total || null,
        goods_name: productForm.goods_name || null,
        goods_engname: productForm.goods_engname || null,
        aggrgoods_name: productForm.aggrgoods_name || null,
        aggrgoods_engname: productForm.aggrgoods_engname || null,
        product_sell: parseFloat(productForm.product_sell.toString()) || 0,
        product_eusell: parseFloat(productForm.product_eusell.toString()) || 0,
      };

      if (editingProduct) {
        await axiosClient.put(apiEndpoints.cbam.product.update(editingProduct.id), productData);
        setSelectedProductNames((prev) => {
          const newSet = new Set(prev);
          newSet.delete(editingProduct.product_name);
          newSet.add(productForm.product_name);
          return newSet;
        });
        setToast({ message: '제품이 성공적으로 수정되었습니다.', type: 'success' });
      } else {
        await axiosClient.post(apiEndpoints.cbam.product.create, productData);
        setSelectedProductNames((prev) => new Set(prev).add(productForm.product_name));
        setToast({ message: '제품이 성공적으로 생성되었습니다.', type: 'success' });
      }
      resetProductForm();
      fetchProducts();
    } catch (error: any) {
      console.error('❌ 제품 저장 실패:', error);
      setToast({ message: `제품 저장에 실패했습니다: ${error.response?.data?.detail || error.message}`, type: 'error' });
    }
  };

  const handleProcessSubmit = async (e: React.FormEvent, productId: number) => {
    e.preventDefault();
    const targetProductId = productId;
    const targetProduct = products.find((p) => p.id === targetProductId);
    if (!processForm.process_name) {
      setToast({ message: '공정명을 입력해주세요.', type: 'error' });
      return;
    }
    if (!selectedInstallForProcess) {
      setToast({ message: '사업장을 선택해주세요.', type: 'error' });
      return;
    }
    try {
      const processData = {
        process_name: processForm.process_name,
        install_id: selectedInstallForProcess,
        start_period: null,
        end_period: null,
        product_ids: [productId],
      };

      let response;
      if (isEditingProcess && selectedProcess && showProcessFormForProduct) {
        let existingProcess = processes.find((p) => {
          const nameMatch = p.process_name === selectedProcess;
          const installMatch = selectedInstallForProcess ? p.install_id === selectedInstallForProcess : true;
          const linked = Array.isArray(p.products) ? p.products.some((prod) => prod.id === targetProductId) : true;
          return nameMatch && installMatch && linked;
        });
        if (!existingProcess) {
          existingProcess = processes.find((p) => {
            const nameMatch = p.process_name === selectedProcess;
            const linked = Array.isArray(p.products) ? p.products.some((prod) => prod.id === targetProductId) : false;
            return nameMatch && linked;
          });
        }
        if (existingProcess) {
          const updatePayload: any = { process_name: processForm.process_name };
          if (selectedInstallForProcess) {
            updatePayload.install_id = selectedInstallForProcess;
          }
          response = await axiosClient.put(apiEndpoints.cbam.process.update(existingProcess.id), updatePayload);
          setToast({ message: `공정이 "${selectedProcess}"에서 "${processForm.process_name}"으로 수정되었습니다.`, type: 'success' });
        } else {
          response = await axiosClient.post(apiEndpoints.cbam.process.create, processData);
          setToast({ message: `새 공정 "${processForm.process_name}"이 성공적으로 생성되었습니다.`, type: 'success' });
        }
      } else {
        response = await axiosClient.post(apiEndpoints.cbam.process.create, processData);
        setToast({ message: '프로세스가 성공적으로 생성되었습니다.', type: 'success' });
      }

      setProcessForm({ process_name: '' });
      setSelectedProcess('');
      setAvailableProcesses([]);
      setShowProcessFormForProduct(null);
      setSelectedInstallForProcess('');
      setIsEditingProcess(false);

      await fetchProcesses();
      if (targetProduct) {
        await fetchProductProcesses(targetProduct.id, targetProduct.product_name);
      }
    } catch (error: any) {
      console.error('❌ 프로세스 처리 실패:', error);
      const status = error.response?.status;
      const backendDetail = error.response?.data?.detail;
      const friendlyMessage = status === 409 ? backendDetail || '동일 사업장에 동일한 공정명이 이미 존재합니다.' : backendDetail || error.message;
      setToast({ message: `프로세스 처리에 실패했습니다: ${friendlyMessage}`, type: 'error' });
    }
  };

  const handleDeleteProduct = async (productId: number, productName: string) => {
    if (!confirm(`"${productName}" 제품을 삭제하시겠습니까?\n\n⚠️ 주의: 이 제품과 연결된 모든 프로세스가 함께 삭제됩니다.`)) {
      return;
    }
    try {
      await axiosClient.delete(apiEndpoints.cbam.product.delete(productId));
      setSelectedProductNames((prev) => {
        const newSet = new Set(prev);
        newSet.delete(productName);
        return newSet;
      });
      setToast({ message: `"${productName}" 제품이 성공적으로 삭제되었습니다.`, type: 'success' });
      fetchProducts();
      fetchProcesses();
    } catch (error: any) {
      console.error('❌ 제품 삭제 실패:', error);
      setToast({ message: `제품 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`, type: 'error' });
    }
  };

  const handleDeleteProcessByName = async (processName: string, productId: number) => {
    if (!confirm(`"${processName}" 공정을 삭제하시겠습니까?`)) return;
    try {
      setIsLoading(true);
      const process = processes.find((p) => p.process_name === processName);
      if (process) {
        await axiosClient.delete(apiEndpoints.cbam.process.delete(process.id));
        setToast({ message: '공정이 성공적으로 삭제되었습니다!', type: 'success' });
        await fetchProcesses();
        const product = products.find((p) => p.id === productId);
        if (product) {
          await fetchProductProcesses(product.id, product.product_name);
        }
      } else {
        setToast({ message: '삭제할 공정을 찾을 수 없습니다.', type: 'error' });
      }
    } catch (error: any) {
      console.error('❌ 공정 삭제 실패:', error);
      setToast({ message: `공정 삭제에 실패했습니다: ${error.response?.data?.detail || error.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // 공정 수정 모드 시작 (제품별 공정 목록에서 진입)
  const handleEditProcess = (processName: string, productId: number) => {
    // 폼을 해당 제품에 대해 열고 수정 모드로 설정
    setShowProcessFormForProduct(productId);
    setSelectedProcess(processName);
    setProcessForm({ process_name: processName });
    setIsEditingProcess(true);

    // 현재 제품과 연결된 동일명 공정의 사업장을 기본값으로 설정
    const existingForProduct = processes.find((p) => {
      const nameMatch = p.process_name === processName;
      const linked = Array.isArray(p.products) && p.products.some((prod) => prod.id === productId);
      return nameMatch && linked;
    });
    if (existingForProduct && typeof existingForProduct.install_id === 'number') {
      setSelectedInstallForProcess(existingForProduct.install_id);
      if (installProcessesMap.has(existingForProduct.install_id)) {
        setAvailableProcesses(installProcessesMap.get(existingForProduct.install_id) || []);
      }
    }

    // 사용 가능한 공정 목록을 최신으로 로드
    const product = products.find((p) => p.id === productId);
    if (product) {
      fetchAvailableProcesses(product.product_name, productId);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-white/80 mt-2">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="text-white">
      {toast && (
        <div
          className={`mb-4 p-4 rounded-lg ${
            toast.type === 'success'
              ? 'bg-green-500/20 border border-green-500/50 text-green-300'
              : toast.type === 'error'
              ? 'bg-red-500/20 border border-red-500/50 text-red-300'
              : 'bg-blue-500/20 border border-blue-500/50 text-blue-300'
          }`}
        >
          {toast.message}
        </div>
      )}

      {showHSCodeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-2xl mx-4 shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">HS코드로 CN코드 검색</h3>
              <button onClick={() => setShowHSCodeModal(false)} className="text-gray-400 hover:text-white text-xl transition-colors">
                ×
              </button>
            </div>
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

      <div className="space-y-6">
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

              {(productForm.prostart_period || productForm.proend_period) && (
                <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-md">
                  <p className="text-sm text-blue-300">
                    📅 <strong>기간 설정 완료:</strong> {productForm.prostart_period || '시작일 미설정'} ~ {productForm.proend_period || '종료일 미설정'}
                  </p>
                  <p className="text-xs text-blue-400 mt-1">이제 아래에서 해당 기간에 생산되는 제품명을 선택할 수 있습니다.</p>
                </div>
              )}

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
                    if (productForm.prostart_period && productForm.proend_period && productNames.length === 0) {
                      fetchProductNamesByPeriod(productForm.prostart_period, productForm.proend_period);
                    }
                  }}
                  className={`w-full px-3 py-2 border rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    !productForm.prostart_period || !productForm.proend_period ? 'bg-gray-700/50 border-gray-500 cursor-not-allowed' : 'bg-gray-800/50 border-gray-600'
                  }`}
                  required
                  disabled={productNamesLoading || !productForm.prostart_period || !productForm.proend_period}
                >
                  <option value="">
                    {!productForm.prostart_period || !productForm.proend_period
                      ? '기간을 먼저 설정해주세요'
                      : productNamesLoading
                      ? '제품명 목록을 불러오는 중...'
                      : '제품명을 선택하세요'}
                  </option>
                  {productNames
                    .filter((name) => {
                      // 수정 모드에서는 현재 수정 중인 제품명은 드롭다운에 포함
                      if (editingProduct && name === editingProduct.product_name) return true;
                      return !selectedProductNames.has(name);
                    })
                    .map((name) => (
                      <option key={name} value={name}>
                        {name}
                      </option>
                    ))}
                </select>
                {(productForm.prostart_period && productForm.proend_period) && (
                  <div className="mt-2 p-2 bg-green-500/10 border border-green-500/20 rounded-md">
                    <p className="text-xs text-green-300">
                      ✅ 해당 기간에 생산된 제품명 {productNames.length}개가 표시됩니다
                      {selectedProductNames.size > 0 && <span className="block text-yellow-300 mt-1">🔒 이미 선택된 제품명 {selectedProductNames.size}개는 제외됨</span>}
                    </p>
                  </div>
                )}
                {productNamesLoading && <p className="text-xs text-gray-400 mt-1">제품명 목록을 불러오는 중...</p>}
                {productNamesError && <p className="text-xs text-red-400 mt-1">제품명 목록 로드 실패: {productNamesError}</p>}
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
                  <button type="button" onClick={openHSCodeModal} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors duration-200">
                    HS CODE 검색
                  </button>
                </div>
              </div>

              {productForm.cncode_total && (
                <div className="bg-green-500/10 border border-green-500/20 rounded-md p-3">
                  <h4 className="text-sm font-medium text-green-300 mb-2">✅ 선택된 CN 코드:</h4>
                  <div className="space-y-1">
                    <div className="text-sm text-white">
                      CN 코드: <span className="font-medium">{productForm.cncode_total}</span>
                    </div>
                    {productForm.goods_name && <div className="text-xs text-gray-300">품목명: {productForm.goods_name}</div>}
                    {productForm.goods_engname && <div className="text-xs text-gray-400">품목영문명: {productForm.goods_engname}</div>}
                    {productForm.aggrgoods_name && <div className="text-xs text-gray-300">품목군명: {productForm.aggrgoods_name}</div>}
                    {productForm.aggrgoods_engname && <div className="text-xs text-gray-400">품목군영문명: {productForm.aggrgoods_engname}</div>}
                  </div>
                </div>
              )}

              <div className="flex gap-4">
                {editingProduct && (
                  <button type="button" onClick={handleCancelEditProduct} className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors duration-200">
                    취소
                  </button>
                )}
                <button type="submit" className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200">
                  📦 {editingProduct ? '제품 수정' : '제품 생성'}
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">📋 등록된 제품 목록 ({products.length}개)</h3>
          {products.length === 0 ? (
            <p className="text-gray-300 text-center py-4">등록된 제품이 없습니다.</p>
          ) : (
            <div className="space-y-6">
              {products.map((product) => {
                const productProcesses = productProcessesMap.get(product.id) || [];
                const isShowingProcessForm = showProcessFormForProduct === product.id;
                return (
                  <div key={product.id} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="text-white font-semibold text-lg">{product.product_name}</h4>
                      <div className="flex gap-2">
                        <button onClick={() => handleShowProcessForm(product)} className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md transition-colors duration-200">
                          {showProcessFormForProduct === product.id ? '공정 취소' : '공정 추가'}
                        </button>
                        <button onClick={() => handleEditProduct(product)} className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200">
                          수정
                        </button>
                        <button onClick={() => handleDeleteProduct(product.id, product.product_name)} className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200">
                          삭제
                        </button>
                      </div>
                    </div>

                    <div className="space-y-1 mb-3">
                      <p className="text-gray-300 text-sm">기간: {product.prostart_period} ~ {product.proend_period}</p>
                      <p className="text-gray-300 text-sm">수량: {product.product_amount.toLocaleString()}</p>
                      <p className="text-gray-300 text-sm">공정 수: {productProcessesMap.get(product.id)?.length || 0}개</p>
                      {product.product_category && (
                        <p className="text-gray-300 text-sm">
                          카테고리: <span className="text-blue-300">{product.product_category}</span>
                        </p>
                      )}
                      {product.cncode_total && (
                        <div className="mt-2 p-2 bg-blue-500/10 rounded border border-blue-500/20">
                          <p className="text-blue-300 text-sm">
                            CN 코드: <span className="font-medium">{product.cncode_total}</span>
                          </p>
                          {product.goods_name && <p className="text-gray-300 text-xs">품목명: {product.goods_name}</p>}
                          {product.goods_engname && <p className="text-gray-400 text-xs">품목영문명: {product.goods_engname}</p>}
                          {product.aggrgoods_name && <p className="text-gray-300 text-xs">품목군명: {product.aggrgoods_name}</p>}
                          {product.aggrgoods_engname && <p className="text-gray-400 text-xs">품목군영문명: {product.aggrgoods_engname}</p>}
                        </div>
                      )}
                    </div>

                    {productProcessesMap.get(product.id) && productProcessesMap.get(product.id)!.length > 0 && (
                      <div className="mb-4 p-3 bg-white/5 rounded-lg">
                        <h5 className="text-sm font-medium text-white mb-2">📋 등록된 공정:</h5>
                        <div className="space-y-2">
                          {productProcessesMap.get(product.id)!.map((processName, index) => (
                            <div key={index} className="flex justify-between items-center p-2 bg-white/5 rounded">
                              <span className="text-gray-300 text-sm">{processName}</span>
                              <div className="flex gap-1">
                                <button onClick={() => handleEditProcess(processName, product.id)} className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors">
                                  🔧 수정
                                </button>
                                <button onClick={() => handleDeleteProcessByName(processName, product.id)} className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors">
                                  🗑️ 삭제
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {isShowingProcessForm && (
                      <div className="mb-4 p-4 bg-white/5 rounded-lg border border-purple-500/30">
                        <h5 className="text-sm font-medium text-white mb-3">{isEditingProcess && selectedProcess && showProcessFormForProduct === product.id ? '🔧 공정 수정' : '➕ 공정 추가'}</h5>
                        {availableProcesses.length > 0 ? (
                          <div className="mb-3 p-2 bg-blue-500/10 border border-blue-500/20 rounded-md">
                            <p className="text-xs text-blue-300">📋 <strong>사용 가능한 공정:</strong> {availableProcesses.length}개</p>
                            <p className="text-xs text-blue-400 mt-1">아래 드롭다운에서 해당 제품에 적합한 공정을 선택해주세요.</p>
                          </div>
                        ) : (
                          <div className="mb-3 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
                            <p className="text-xs text-yellow-300">⚠️ <strong>사용 가능한 공정이 없습니다.</strong></p>
                            <p className="text-xs text-yellow-400 mt-1">{productProcessesMap.get(product.id) && productProcessesMap.get(product.id)!.length > 0 ? '이미 모든 공정이 연결되어 있습니다.' : '더미 데이터에서 해당 제품의 공정 정보를 찾을 수 없습니다.'}</p>
                          </div>
                        )}
                        <form onSubmit={(e) => handleProcessSubmit(e, product.id)} className="space-y-3">
                          <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">사업장 선택 *</label>
                            <select
                              value={selectedInstallForProcess || ''}
                              onChange={(e) => {
                                const iid = parseInt(e.target.value);
                                setSelectedInstallForProcess(iid);
                                if (!isEditingProcess) {
                                  setSelectedProcess('');
                                }
                              }}
                              className="w-full px-3 py-2 border rounded-md text-white bg-gray-800/50 border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
                              required
                            >
                              <option value="">사업장을 선택하세요</option>
                              {installs.map((install) => (
                                <option key={install.id} value={install.id}>
                                  {install.install_name} ({installProcessesMap.get(install.id)?.length || 0}개 공정)
                                </option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">공정명 *</label>
                            <select
                              value={selectedProcess}
                              onChange={(e) => handleProcessSelectionChange(e.target.value)}
                              className={`w-full px-3 py-2 border rounded-md text-white focus:outline-none focus:ring-2 focus:ring-purple-500 ${
                                availableProcesses.length > 0 ? 'bg-gray-800/50 border-gray-600' : 'bg-gray-700/50 border-gray-500 cursor-not-allowed'
                              }`}
                              required
                              disabled={availableProcesses.length === 0}
                            >
                              <option value="">{isEditingProcess && selectedProcess && showProcessFormForProduct === product.id ? `현재: ${selectedProcess}` : availableProcesses.length > 0 ? '공정을 선택하세요' : '사용 가능한 공정이 없습니다'}</option>
                              {availableProcesses.map((process) => (
                                <option key={process} value={process}>
                                  {process}
                                </option>
                              ))}
                            </select>
                            {dummyLoading && <p className="text-xs text-gray-400 mt-1">공정 목록을 불러오는 중...</p>}
                            {dummyError && <p className="text-xs text-red-400 mt-1">공정 목록 로드 실패: {dummyError}</p>}
                            {!dummyLoading && !dummyError && availableProcesses.length === 0 && <p className="text-xs text-yellow-400 mt-1">해당 제품의 공정 정보가 더미 데이터에 등록되어 있지 않습니다.</p>}
                          </div>
                          <div className="flex gap-2">
                            <button
                              type="submit"
                              disabled={!selectedProcess || !selectedInstallForProcess || availableProcesses.length === 0}
                              className={`flex-1 px-4 py-2 text-white text-sm font-medium rounded-md transition-colors duration-200 ${
                                selectedProcess && selectedInstallForProcess && availableProcesses.length > 0 ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-500 cursor-not-allowed'
                              }`}
                            >
                              {isEditingProcess && selectedProcess && showProcessFormForProduct === product.id ? '🔧 공정 수정' : '➕ 공정 추가'}
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

        {/* 모달: 전체 제품관리 page.tsx 임베드 */}
        {showProductForm && (
          <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center">
            <div className="w-full mx-4 bg-gray-900 border border-gray-700 rounded-lg shadow-xl overflow-hidden max-w-4xl md:max-w-4xl lg:max-w-4xl">
              <div className="flex items-center justify-between p-4 border-b border-gray-700">
                <h4 className="text-white font-semibold">제품 관리</h4>
                <button onClick={() => setShowProductForm(false)} className="text-gray-300 hover:text-white">✕</button>
              </div>
              <div className="h-[60vh] min-h-[520px] overflow-y-auto">
                <InstallProductsPage overrideInstallId={installId} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


