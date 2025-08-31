'use client';

import React, { useState } from 'react';
import { Process, Product, Install } from '@/hooks/useProcessManager';

interface ProcessSelectorProps {
  processes: Process[];
  allProcesses: Process[];
  products: Product[];
  installs: Install[];
  selectedProduct: Product | null;
  selectedInstall: Install | null;
  onProcessSelect: (process: Process) => void;
  onClose: () => void;
}

export const ProcessSelector: React.FC<ProcessSelectorProps> = ({
  processes,
  allProcesses,
  products,
  installs,
  selectedProduct,
  selectedInstall,
  onProcessSelect,
  onClose,
}) => {
  const [processFilterMode, setProcessFilterMode] = useState<'all' | 'product'>('all');

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">
            공정 선택 - {selectedProduct?.product_name}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-200">✕</button>
        </div>
        <div className="space-y-2">
          {processes.length > 0 ? (
            processes.map((process) => (
              <div
                key={process.id}
                className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-purple-400 transition-colors"
                onClick={() => onProcessSelect(process)}
              >
                <div className="font-medium text-white">{process.process_name}</div>
                <div className="text-sm text-gray-300">시작일: {process.start_period || 'N/A'}</div>
                <div className="text-sm text-gray-300">종료일: {process.end_period || 'N/A'}</div>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-gray-400">
              {selectedProduct?.product_name}에 등록된 공정이 없습니다.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// 제품별 공정 선택 모달 (탭 포함)
export const ProductProcessModal: React.FC<{
  selectedProduct: Product | null;
  allProcesses: Process[];
  products: Product[];
  installs: Install[];
  selectedInstall: Install | null;
  onProcessSelect: (process: Process) => void;
  onClose: () => void;
}> = ({
  selectedProduct,
  allProcesses,
  products,
  installs,
  selectedInstall,
  onProcessSelect,
  onClose,
}) => {
  const [productModalTab, setProductModalTab] = useState<'process' | 'quantity'>('process');
  const [processFilterMode, setProcessFilterMode] = useState<'all' | 'product'>('all');
  const [productQuantityForm, setProductQuantityForm] = useState({
    product_amount: selectedProduct?.product_amount || 0,
    product_sell: selectedProduct?.product_sell || 0,
    product_eusell: selectedProduct?.product_eusell || 0
  });

  // useEffect로 selectedProduct 변경 시 폼 값 업데이트
  React.useEffect(() => {
    if (selectedProduct) {
      setProductQuantityForm({
        product_amount: selectedProduct.product_amount || 0,
        product_sell: selectedProduct.product_sell || 0,
        product_eusell: selectedProduct.product_eusell || 0
      });
    }
  }, [selectedProduct]);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-4xl w-full mx-4 border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">
            {selectedProduct?.product_name} 관리
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-200">✕</button>
        </div>
        
        {/* 탭 네비게이션 */}
        <div className="mb-6 flex gap-2 border-b border-gray-700">
          <button
            onClick={() => setProductModalTab('process')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              productModalTab === 'process'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            🔄 공정 선택
          </button>
          <button
            onClick={() => setProductModalTab('quantity')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              productModalTab === 'quantity'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            📊 수량/판매량
          </button>
        </div>
        
        {/* 탭 컨텐츠 */}
        {productModalTab === 'process' && (
          <div>
            {/* 필터링 옵션 */}
            <div className="mb-4 flex gap-2">
              <button
                onClick={() => setProcessFilterMode('all')}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  processFilterMode === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                전체 공정
              </button>
              {selectedProduct && (
                <button
                  onClick={() => setProcessFilterMode('product')}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    processFilterMode === 'product'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {selectedProduct.product_name} 공정만
                </button>
              )}
            </div>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {(() => {
                const displayProcesses = processFilterMode === 'product' 
                  ? allProcesses.filter((process: Process) => 
                      process.products && process.products.some((p: Product) => p.id === selectedProduct?.id)
                    )
                  : allProcesses;
                
                return displayProcesses.length > 0 ? (
                  displayProcesses.map((process: Process) => {
                    const relatedProducts = products.filter((product: Product) => 
                      process.products && process.products.some((p: Product) => p.id === product.id)
                    );
                    const productNames = relatedProducts.map((product: Product) => product.product_name).join(', ');
                    
                    const isExternalProcess = process.products && 
                      process.products.some((p: Product) => p.install_id !== selectedInstall?.id);
                    const processInstall = installs.find((install: Install) => 
                      process.products && process.products.some((p: Product) => p.install_id === install.id)
                    );
                    
                    return (
                      <div
                        key={process.id}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          isExternalProcess 
                            ? 'border-gray-500 bg-gray-700 hover:bg-gray-600' 
                            : 'border-gray-600 hover:bg-gray-700 hover:border-purple-400'
                        }`}
                        onClick={() => onProcessSelect(process)}
                      >
                        <div className="font-medium text-white">{process.process_name}</div>
                        <div className="text-sm text-gray-300">사용 제품: {productNames || 'N/A'}</div>
                        {isExternalProcess && (
                          <div className="text-sm text-gray-400">
                            외부 사업장: {processInstall?.install_name || '알 수 없음'} (읽기 전용)
                          </div>
                        )}
                        <div className="text-sm text-gray-300">시작일: {process.start_period || 'N/A'}</div>
                        <div className="text-sm text-gray-300">종료일: {process.end_period || 'N/A'}</div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-4 text-gray-400">
                    {processFilterMode === 'product' 
                      ? `${selectedProduct?.product_name}에 등록된 공정이 없습니다.`
                      : '등록된 공정이 없습니다.'
                    }
                  </div>
                );
              })()}
            </div>
          </div>
        )}
        
        {productModalTab === 'quantity' && (
          <div>
            {/* 제품 정보 표시 */}
            <div className="mb-6 p-4 bg-gray-700 rounded-lg">
              <h4 className="text-white font-medium mb-2">제품 정보</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-300">제품명:</span>
                  <span className="text-white ml-2">{selectedProduct?.product_name}</span>
                </div>
                {selectedProduct?.cncode_total && (
                  <div>
                    <span className="text-gray-300">CN 코드:</span>
                    <span className="text-blue-300 ml-2">{selectedProduct.cncode_total}</span>
                  </div>
                )}
                {selectedProduct?.goods_name && (
                  <div>
                    <span className="text-gray-300">품목명:</span>
                    <span className="text-white ml-2">{selectedProduct.goods_name}</span>
                  </div>
                )}
                {selectedProduct?.aggrgoods_name && (
                  <div>
                    <span className="text-gray-300">품목군명:</span>
                    <span className="text-white ml-2">{selectedProduct.aggrgoods_name}</span>
                  </div>
                )}
              </div>
            </div>
            
            {/* 수량/판매량 입력 폼 */}
            <div className="space-y-4">
              <h4 className="text-white font-medium">수량 및 판매량 입력</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    제품 수량 (ton) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={productQuantityForm.product_amount}
                    onChange={(e) => setProductQuantityForm(prev => ({
                      ...prev,
                      product_amount: parseFloat(e.target.value) || 0
                    }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    제품 판매량 (ton) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={productQuantityForm.product_sell}
                    onChange={(e) => setProductQuantityForm(prev => ({
                      ...prev,
                      product_sell: parseFloat(e.target.value) || 0
                    }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    제품 EU 판매량 (ton) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={productQuantityForm.product_eusell}
                    onChange={(e) => setProductQuantityForm(prev => ({
                      ...prev,
                      product_eusell: parseFloat(e.target.value) || 0
                    }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>
              
              {/* 현재 입력된 값 표시 */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="text-sm text-blue-300 mb-1">제품 수량</div>
                  <div className="text-2xl font-bold text-white">{productQuantityForm.product_amount.toLocaleString()} ton</div>
                </div>
                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                  <div className="text-sm text-green-300 mb-1">제품 판매량</div>
                  <div className="text-2xl font-bold text-white">{productQuantityForm.product_sell.toLocaleString()} ton</div>
                </div>
                <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                  <div className="text-sm text-purple-300 mb-1">EU 판매량</div>
                  <div className="text-2xl font-bold text-white">{productQuantityForm.product_eusell.toLocaleString()} ton</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
