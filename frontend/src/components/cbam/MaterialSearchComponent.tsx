import React, { useState, useEffect } from 'react';
import { useMaterialMasterAPI, MaterialMapping } from '@/hooks/useMaterialMasterAPI';

// ============================================================================
// 🔍 원료 검색 및 배출계수 자동 매핑 컴포넌트
// ============================================================================

interface MaterialSearchComponentProps {
  onMaterialSelect?: (material: MaterialMapping) => void;
  onFactorChange?: (factor: number) => void;
  initialMaterialName?: string;
  showSuggestions?: boolean;
}

export const MaterialSearchComponent: React.FC<MaterialSearchComponentProps> = ({
  onMaterialSelect,
  onFactorChange,
  initialMaterialName = '',
  showSuggestions = true,
}) => {
  const [materialName, setMaterialName] = useState(initialMaterialName);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState<MaterialMapping | null>(null);
  const [factor, setFactor] = useState<number>(0);

  const {
    loading,
    error,
    searchMaterialByName,
    getMaterialFactor,
    getMaterialNameSuggestions,
    autoMapMaterialFactor,
  } = useMaterialMasterAPI();

  // 원료명 입력 시 자동완성 제안
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (materialName.trim().length >= 2) {
        const suggestions = await getMaterialNameSuggestions(materialName);
        setSuggestions(suggestions);
        setShowSuggestionsList(true);
      } else {
        setSuggestions([]);
        setShowSuggestionsList(false);
      }
    };

    const debounceTimer = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounceTimer);
  }, [materialName, getMaterialNameSuggestions]);

  // 원료명 선택 시 배출계수 자동 매핑
  const handleMaterialSelect = async (selectedName: string) => {
    setMaterialName(selectedName);
    setShowSuggestionsList(false);
    
    try {
      // 배출계수 자동 매핑
      const autoFactor = await autoMapMaterialFactor(selectedName);
      if (autoFactor !== null) {
        setFactor(autoFactor);
        onFactorChange?.(autoFactor);
        
        // 선택된 원료 정보 설정
        const searchResult = await searchMaterialByName(selectedName);
        if (searchResult.success && searchResult.data.length > 0) {
          const material = searchResult.data[0];
          setSelectedMaterial(material);
          onMaterialSelect?.(material);
        }
      }
    } catch (err) {
      console.error('배출계수 자동 매핑 실패:', err);
    }
  };

  // 수동으로 배출계수 입력
  const handleFactorChange = (newFactor: number) => {
    setFactor(newFactor);
    onFactorChange?.(newFactor);
  };

  // 원료 검색 실행
  const handleSearch = async () => {
    if (!materialName.trim()) return;
    
    try {
      const result = await searchMaterialByName(materialName);
      if (result.success && result.data.length > 0) {
        const material = result.data[0];
        setSelectedMaterial(material);
        setFactor(material.mat_factor);
        onMaterialSelect?.(material);
        onFactorChange?.(material.mat_factor);
      }
    } catch (err) {
      console.error('원료 검색 실패:', err);
    }
  };

  return (
    <div className="space-y-4">
      {/* 원료명 입력 및 검색 */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          투입된 원료명
        </label>
        <div className="flex space-x-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={materialName}
              onChange={(e) => setMaterialName(e.target.value)}
              onFocus={() => setShowSuggestionsList(true)}
              placeholder="원료명을 입력하세요 (예: 철광석, 석회석)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            
            {/* 자동완성 제안 목록 */}
            {showSuggestions && showSuggestionsList && suggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleMaterialSelect(suggestion)}
                    className="w-full px-3 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <button
            type="button"
            onClick={handleSearch}
            disabled={loading || !materialName.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '검색중...' : '검색'}
          </button>
        </div>
      </div>

      {/* 배출계수 표시 및 수정 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          배출계수
        </label>
        <input
          type="number"
          value={factor}
          onChange={(e) => handleFactorChange(parseFloat(e.target.value) || 0)}
          step="0.0001"
          min="0"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {selectedMaterial && (
          <p className="mt-1 text-sm text-green-600">
            ✅ 자동 매핑됨: {selectedMaterial.mat_name} (탄소함량: {selectedMaterial.carbon_content || 'N/A'})
          </p>
        )}
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {/* 선택된 원료 정보 */}
      {selectedMaterial && (
        <div className="p-4 bg-gray-50 rounded-md">
          <h4 className="font-medium text-gray-900 mb-2">선택된 원료 정보</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="font-medium">원료명:</span> {selectedMaterial.mat_name}
            </div>
            <div>
              <span className="font-medium">배출계수:</span> {selectedMaterial.mat_factor}
            </div>
            {selectedMaterial.carbon_content && (
              <div>
                <span className="font-medium">탄소함량:</span> {selectedMaterial.carbon_content}
              </div>
            )}
            {selectedMaterial.mat_engname && (
              <div>
                <span className="font-medium">영문명:</span> {selectedMaterial.mat_engname}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
