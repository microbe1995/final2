'use client';

import React, { useState } from 'react';
import { Product } from '@/hooks/useProcessManager';

interface ProductSelectorProps {
  products: Product[];
  onProductSelect: (product: Product) => void;
  onClose: () => void;
}

export const ProductSelector: React.FC<ProductSelectorProps> = ({
  products,
  onProductSelect,
  onClose,
}) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">제품 선택</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-200">✕</button>
        </div>
        <div className="space-y-2">
          {products.length > 0 ? (
            products.map((product) => (
              <div
                key={product.id}
                className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-blue-400 transition-colors"
                onClick={() => onProductSelect(product)}
              >
                <div className="font-medium text-white">{product.product_name}</div>
                <div className="text-sm text-gray-300">카테고리: {product.product_category}</div>
                <div className="text-sm text-gray-300">수량: {product.product_amount}</div>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-gray-400">
              선택된 사업장에 등록된 제품이 없습니다.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
