'use client';

import React, { useState } from 'react';
import CommonShell from '@/components/CommonShell';
import { useDataSearchAPI } from '@/hooks/useDataSearchAPI';
import type {
  HSCodeSearchResponse,
  CountrySearchResponse,
  FuelSearchResponse,
  MaterialSearchResponse,
  PrecursorSearchResponse,
} from '@/hooks/useDataSearchAPI';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Search, Database, Globe, Fuel, Package, Link } from 'lucide-react';

// ============================================================================
// 🔍 CBAM 데이터 검색 페이지
// ============================================================================

export default function CBAMSearchPage() {
  const [activeTab, setActiveTab] = useState<
    'hscode' | 'country' | 'fuel' | 'material' | 'precursor'
  >('hscode');

  // 데이터 검색 API 훅
  const {
    searchHSCode,
    searchCountry,
    searchFuels,
    searchMaterials,
    searchPrecursors,
  } = useDataSearchAPI();
fr
  // 검색 상태
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<{
    hscode?: HSCodeSearchResponse;
    country?: CountrySearchResponse;
    fuel?: FuelSearchResponse;
    material?: MaterialSearchResponse;
    precursor?: PrecursorSearchResponse;
  }>({});

  // 검색 폼 상태
  const [hsCodeQuery, setHsCodeQuery] = useState('');
  const [countryQuery, setCountryQuery] = useState('');
  const [fuelQuery, setFuelQuery] = useState('');
  const [fuelType, setFuelType] = useState('');
  const [materialQuery, setMaterialQuery] = useState('');
  const [materialCategory, setMaterialCategory] = useState('');
  const [precursorQuery, setPrecursorQuery] = useState('');
  const [precursorCategory, setPrecursorCategory] = useState('');

  // ============================================================================
  // 🔍 검색 핸들러 함수들
  // ============================================================================

  const handleHSCodeSearch = async () => {
    if (!hsCodeQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const result = await searchHSCode(hsCodeQuery);
      if (result) {
        setSearchResults(prev => ({ ...prev, hscode: result }));
      }
    } catch (error) {
      console.error('HS코드 검색 실패:', error);
    }
    setIsSearching(false);
  };

  const handleCountrySearch = async () => {
    if (!countryQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const result = await searchCountry({
        query: countryQuery,
        search_type: 'all',
      });
      if (result) {
        setSearchResults(prev => ({ ...prev, country: result }));
      }
    } catch (error) {
      console.error('국가 검색 실패:', error);
    }
    setIsSearching(false);
  };

  const handleFuelSearch = async () => {
    setIsSearching(true);
    try {
      const result = await searchFuels(fuelQuery || undefined, fuelType || undefined);
      if (result) {
        setSearchResults(prev => ({ ...prev, fuel: result }));
      }
    } catch (error) {
      console.error('연료 검색 실패:', error);
    }
    setIsSearching(false);
  };

  const handleMaterialSearch = async () => {
    setIsSearching(true);
    try {
      const result = await searchMaterials(materialQuery || undefined, materialCategory || undefined);
      if (result) {
        setSearchResults(prev => ({ ...prev, material: result }));
      }
    } catch (error) {
      console.error('원료 검색 실패:', error);
    }
    setIsSearching(false);
  };

  const handlePrecursorSearch = async () => {
    setIsSearching(true);
    try {
      const result = await searchPrecursors(precursorQuery || undefined, precursorCategory || undefined);
      if (result) {
        setSearchResults(prev => ({ ...prev, precursor: result }));
      }
    } catch (error) {
      console.error('전구물질 검색 실패:', error);
    }
    setIsSearching(false);
  };

  // ============================================================================
  // 🎨 렌더링 함수들
  // ============================================================================

  const renderHSCodeSearch = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4 flex items-center'>
          <Database className='w-5 h-5 mr-2' />
          HS코드 검색
        </h3>
        <p className='stitch-caption text-white/60 mb-4'>
          HS코드를 입력하여 해당하는 품목 정보를 검색합니다.
        </p>
        
        <div className='flex gap-4 mb-4'>
          <Input
            type='text'
            value={hsCodeQuery}
            onChange={(e) => setHsCodeQuery(e.target.value)}
            placeholder='HS코드를 입력하세요 (예: 7201, 2501)'
            className='flex-1 bg-white/10 border-white/20 text-white'
            onKeyPress={(e) => e.key === 'Enter' && handleHSCodeSearch()}
          />
          <Button
            onClick={handleHSCodeSearch}
            disabled={isSearching || !hsCodeQuery.trim()}
            className='bg-primary hover:bg-primary/90'
          >
            <Search className='w-4 h-4 mr-2' />
            {isSearching ? '검색 중...' : '검색'}
          </Button>
        </div>

        {searchResults.hscode && (
          <div className='bg-white/5 rounded-lg p-4'>
            <h4 className='font-semibold text-white mb-3'>
              검색 결과 ({searchResults.hscode.total_count}개)
            </h4>
            <div className='space-y-2'>
              {searchResults.hscode.hscodes.map((item, index) => (
                <div key={index} className='p-3 bg-white/5 rounded border border-white/10'>
                  <div className='flex justify-between items-start'>
                    <div>
                      <p className='font-medium text-white'>{item.hs_code}</p>
                      <p className='text-white/80 text-sm'>{item.hs_name_ko}</p>
                      <p className='text-white/60 text-xs'>{item.hs_name_en}</p>
                    </div>
                    <span className='text-xs bg-primary/20 text-primary-foreground px-2 py-1 rounded'>
                      {item.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderCountrySearch = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4 flex items-center'>
          <Globe className='w-5 h-5 mr-2' />
          국가 검색
        </h3>
        <p className='stitch-caption text-white/60 mb-4'>
          국가명이나 국가코드로 국가 정보를 검색합니다.
        </p>
        
        <div className='flex gap-4 mb-4'>
          <Input
            type='text'
            value={countryQuery}
            onChange={(e) => setCountryQuery(e.target.value)}
            placeholder='국가명 또는 국가코드를 입력하세요 (예: 한국, KR)'
            className='flex-1 bg-white/10 border-white/20 text-white'
            onKeyPress={(e) => e.key === 'Enter' && handleCountrySearch()}
          />
          <Button
            onClick={handleCountrySearch}
            disabled={isSearching || !countryQuery.trim()}
            className='bg-primary hover:bg-primary/90'
          >
            <Search className='w-4 h-4 mr-2' />
            {isSearching ? '검색 중...' : '검색'}
          </Button>
        </div>

        {searchResults.country && (
          <div className='bg-white/5 rounded-lg p-4'>
            <h4 className='font-semibold text-white mb-3'>
              검색 결과 ({searchResults.country.total_count}개)
            </h4>
            <div className='space-y-2'>
              {searchResults.country.countries.map((item, index) => (
                <div key={index} className='p-3 bg-white/5 rounded border border-white/10'>
                  <div className='flex justify-between items-start'>
                    <div>
                      <p className='font-medium text-white'>{item.korean_name}</p>
                      <p className='text-white/80 text-sm'>{item.country_name}</p>
                      {item.unlocode && (
                        <p className='text-white/60 text-xs'>UNLOCODE: {item.unlocode}</p>
                      )}
                    </div>
                    <span className='text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded'>
                      {item.code}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderFuelSearch = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4 flex items-center'>
          <Fuel className='w-5 h-5 mr-2' />
          연료 검색
        </h3>
        <p className='stitch-caption text-white/60 mb-4'>
          연료명이나 연료 타입으로 연료 정보와 배출계수를 검색합니다.
        </p>
        
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'>
          <Input
            type='text'
            value={fuelQuery}
            onChange={(e) => setFuelQuery(e.target.value)}
            placeholder='연료명 (예: 천연가스, 석탄)'
            className='bg-white/10 border-white/20 text-white'
          />
          <select
            value={fuelType}
            onChange={(e) => setFuelType(e.target.value)}
            className='p-2 bg-white/10 border border-white/20 text-white rounded-md'
          >
            <option value=''>모든 연료 타입</option>
            <option value='gas'>가스</option>
            <option value='liquid'>액체</option>
            <option value='solid'>고체</option>
          </select>
          <Button
            onClick={handleFuelSearch}
            disabled={isSearching}
            className='bg-primary hover:bg-primary/90'
          >
            <Search className='w-4 h-4 mr-2' />
            {isSearching ? '검색 중...' : '검색'}
          </Button>
        </div>

        {searchResults.fuel && (
          <div className='bg-white/5 rounded-lg p-4'>
            <h4 className='font-semibold text-white mb-3'>
              검색 결과 ({searchResults.fuel.total_count}개)
            </h4>
            <div className='space-y-2'>
              {searchResults.fuel.fuels.map((item, index) => (
                <div key={index} className='p-3 bg-white/5 rounded border border-white/10'>
                  <div className='flex justify-between items-start'>
                    <div>
                      <p className='font-medium text-white'>{item.fuel_name}</p>
                      <p className='text-white/60 text-sm'>배출계수: {item.emission_factor} kg CO₂eq/{item.unit}</p>
                      <p className='text-white/60 text-xs'>발열량: {item.calorific_value} MJ/{item.unit}</p>
                    </div>
                    <span className='text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded'>
                      {item.fuel_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderMaterialSearch = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4 flex items-center'>
          <Package className='w-5 h-5 mr-2' />
          원료 검색
        </h3>
        <p className='stitch-caption text-white/60 mb-4'>
          원료명이나 카테고리로 원료 정보와 배출계수를 검색합니다.
        </p>
        
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'>
          <Input
            type='text'
            value={materialQuery}
            onChange={(e) => setMaterialQuery(e.target.value)}
            placeholder='원료명 (예: 철강, 시멘트)'
            className='bg-white/10 border-white/20 text-white'
          />
          <select
            value={materialCategory}
            onChange={(e) => setMaterialCategory(e.target.value)}
            className='p-2 bg-white/10 border border-white/20 text-white rounded-md'
          >
            <option value=''>모든 카테고리</option>
            <option value='metal'>금속</option>
            <option value='cement'>시멘트</option>
            <option value='chemical'>화학</option>
            <option value='fertilizer'>비료</option>
          </select>
          <Button
            onClick={handleMaterialSearch}
            disabled={isSearching}
            className='bg-primary hover:bg-primary/90'
          >
            <Search className='w-4 h-4 mr-2' />
            {isSearching ? '검색 중...' : '검색'}
          </Button>
        </div>

        {searchResults.material && (
          <div className='bg-white/5 rounded-lg p-4'>
            <h4 className='font-semibold text-white mb-3'>
              검색 결과 ({searchResults.material.total_count}개)
            </h4>
            <div className='space-y-2'>
              {searchResults.material.materials.map((item, index) => (
                <div key={index} className='p-3 bg-white/5 rounded border border-white/10'>
                  <div className='flex justify-between items-start'>
                    <div>
                      <p className='font-medium text-white'>{item.material_name}</p>
                      <p className='text-white/60 text-sm'>배출계수: {item.emission_factor} kg CO₂eq/{item.unit}</p>
                    </div>
                    <span className='text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded'>
                      {item.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderPrecursorSearch = () => (
    <div className='space-y-6'>
      <div className='stitch-card p-6'>
        <h3 className='stitch-h1 text-lg font-semibold mb-4 flex items-center'>
          <Link className='w-5 h-5 mr-2' />
          전구물질 검색
        </h3>
        <p className='stitch-caption text-white/60 mb-4'>
          전구물질명이나 카테고리로 전구물질 정보와 배출계수를 검색합니다.
        </p>
        
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'>
          <Input
            type='text'
            value={precursorQuery}
            onChange={(e) => setPrecursorQuery(e.target.value)}
            placeholder='전구물질명'
            className='bg-white/10 border-white/20 text-white'
          />
          <select
            value={precursorCategory}
            onChange={(e) => setPrecursorCategory(e.target.value)}
            className='p-2 bg-white/10 border border-white/20 text-white rounded-md'
          >
            <option value=''>모든 카테고리</option>
            <option value='intermediate'>중간재</option>
            <option value='input'>투입재</option>
            <option value='byproduct'>부산물</option>
          </select>
          <Button
            onClick={handlePrecursorSearch}
            disabled={isSearching}
            className='bg-primary hover:bg-primary/90'
          >
            <Search className='w-4 h-4 mr-2' />
            {isSearching ? '검색 중...' : '검색'}
          </Button>
        </div>

        {searchResults.precursor && (
          <div className='bg-white/5 rounded-lg p-4'>
            <h4 className='font-semibold text-white mb-3'>
              검색 결과 ({searchResults.precursor.total_count}개)
            </h4>
            <div className='space-y-2'>
              {searchResults.precursor.precursors.map((item, index) => (
                <div key={index} className='p-3 bg-white/5 rounded border border-white/10'>
                  <div className='flex justify-between items-start'>
                    <div>
                      <p className='font-medium text-white'>{item.precursor_name}</p>
                      <p className='text-white/60 text-sm'>배출계수: {item.emission_factor} kg CO₂eq/{item.unit}</p>
                      {item.carbon_content && (
                        <p className='text-white/60 text-xs'>탄소 함량: {item.carbon_content}%</p>
                      )}
                    </div>
                    <span className='text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded'>
                      {item.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <CommonShell>
      <div className='space-y-6'>
        {/* 페이지 헤더 */}
        <div className='flex flex-col gap-3'>
          <h1 className='stitch-h1 text-3xl font-bold'>CBAM 데이터 검색</h1>
          <p className='stitch-caption'>
            CBAM 계산에 필요한 HS코드, 국가, 연료, 원료, 전구물질 정보를 검색합니다
          </p>
        </div>

        {/* 탭 네비게이션 */}
        <div className='flex space-x-1 p-1 bg-white/5 rounded-lg overflow-x-auto'>
          <button
            onClick={() => setActiveTab('hscode')}
            className={`flex-shrink-0 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'hscode'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            📊 HS코드
          </button>
          <button
            onClick={() => setActiveTab('country')}
            className={`flex-shrink-0 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'country'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            🌍 국가
          </button>
          <button
            onClick={() => setActiveTab('fuel')}
            className={`flex-shrink-0 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'fuel'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            🔥 연료
          </button>
          <button
            onClick={() => setActiveTab('material')}
            className={`flex-shrink-0 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'material'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            🏭 원료
          </button>
          <button
            onClick={() => setActiveTab('precursor')}
            className={`flex-shrink-0 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'precursor'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            🔗 전구물질
          </button>
        </div>

        {/* 탭 콘텐츠 */}
        {activeTab === 'hscode' && renderHSCodeSearch()}
        {activeTab === 'country' && renderCountrySearch()}
        {activeTab === 'fuel' && renderFuelSearch()}
        {activeTab === 'material' && renderMaterialSearch()}
        {activeTab === 'precursor' && renderPrecursorSearch()}
      </div>
    </CommonShell>
  );
}
