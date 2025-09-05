'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { Download, FileText, Globe, Languages } from 'lucide-react';
import CbamLayout from '@/components/cbam/CbamLayout';

// ============================================================================
// 🎯 Gas Emission Report 페이지 - 독립적인 완전한 구현
// ============================================================================

// 하드코딩된 데이터 (이미지에서 확인된 데이터)
const HARDCODED_DATA = {
  // 설치 정보
  installation: {
    korean: "삼정",
    english: "Samjong"
  },
  economicActivity: {
    korean: "철강",
    english: "steel industry"
  },
  representative: {
    korean: "김중동",
    english: "kimjongdong"
  },
  
  // 연락처 정보
  contact: {
    email: "KPMG@adf.com",
    telephone: "010-1234-1234",
    street: {
      korean: "테헤란로",
      english: "Teheran-ro"
    },
    number: {
      korean: "152",
      english: "152"
    },
    postcode: "06236",
    city: "서울 강남구"
  },
  
  // 위치 정보
  location: {
    city: {
      korean: "서울",
      english: "Seoul"
    },
    country: {
      korean: "대한민국",
      english: "Korea"
    },
    unlocode: "KR",
    coordinates: {
      latitude: 37.50002424,
      longitude: 127.03650862
    }
  }
};

// 제품 정보 타입 정의 (DB에서 가져올 데이터)
interface Product {
  id: string;
  cnCode: string;
  productName: string;
  routes: Route[];
}

interface Route {
  id: string;
  name: string;
  ingredients: Ingredient[];
  fuels: Fuel[];
}

interface Ingredient {
  id: string;
  name: string;
  emission: number;
  isAggregatedGoods: boolean;
}

interface Fuel {
  id: string;
  name: string;
  emission: number;
}

// Gas Emission Report 페이지 컴포넌트
export default function GasEmissionReportPage() {
  const [language, setLanguage] = useState<'korean' | 'english'>('korean');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingProductData, setLoadingProductData] = useState(false);
  const todayStr = new Date().toISOString().split('T')[0];
  
  // 실데이터: 제품 테이블/설치 테이블에서 가져올 항목 정의
  type ProductRecord = {
    id: number;
    install_id: number;
    product_name: string;
    cncode_total?: string | null;
    goods_name?: string | null;
    goods_engname?: string | null;
    aggrgoods_name?: string | null;
    aggrgoods_engname?: string | null;
    product_eusell: number;
    attr_em?: number | null;
  };
  type InstallRecord = { id: number; install_name: string };
  const [productOptions, setProductOptions] = useState<ProductRecord[]>([]);
  const [installMap, setInstallMap] = useState<Record<number, string>>({});
  const [selectedProductId, setSelectedProductId] = useState<number | ''>('');
  
  // 폼 데이터 상태
  const [formData, setFormData] = useState({
    // 헤더 정보
    companyName: '',
    issueDate: '',
    
    // 생산 기간
    startPeriod: '',
    endPeriod: '',
    
    // 시설 정보
    installationName: '',
    address: {
      workplaceName: '',
      country: '',
      city: '',
      postcode: '',
      workplace: '',
      currencyCode: '',
      coordinates: ''
    },
    
    // 제품 정보
    productGroup: '',
    
    // 배출계수
    emissionFactor: '',
    
    // 연락처
    email: '',
    contact: ''
  });

  // 제품 데이터 로딩 (실제로는 API에서 가져올 데이터)
  useEffect(() => {
    // 시뮬레이션된 API 호출
    const loadProducts = async () => {
      setLoading(true);
      
      // 실제 환경에서는 API에서 데이터를 가져옴
      // const response = await fetch('/api/products');
      // const data = await response.json();
      
      // 임시 하드코딩된 제품 데이터 (DB에서 가져올 구조)
      const mockProducts: Product[] = [
        {
          id: '1',
          cnCode: '7208',
          productName: '고강도 강판',
          routes: [
            {
              id: 'route1',
              name: 'Route 1',
              ingredients: [
                { id: 'ing1', name: '원료1', emission: 0, isAggregatedGoods: false },
                { id: 'ing2', name: '원료2', emission: 0, isAggregatedGoods: false }
              ],
              fuels: [
                { id: 'fuel1', name: '연료1', emission: 0 },
                { id: 'fuel2', name: '연료2', emission: 0 }
              ]
            },
            {
              id: 'route2',
              name: 'Route 2',
              ingredients: [
                { id: 'ing1', name: '원료1', emission: 0, isAggregatedGoods: false },
                { id: 'ing2', name: '원료2', emission: 0, isAggregatedGoods: false }
              ],
              fuels: [
                { id: 'fuel1', name: '연료1', emission: 0 },
                { id: 'fuel2', name: '연료2', emission: 0 }
              ]
            }
          ]
        }
      ];
      
      setTimeout(() => {
        setProducts(mockProducts);
        setLoading(false);
      }, 1000);
    };

    loadProducts();
  }, []);

  // 언어 전환 핸들러
  const toggleLanguage = () => {
    setLanguage(prev => prev === 'korean' ? 'english' : 'korean');
  };

  // 제품/설치 실데이터 로드
  const handleLoadProductData = async () => {
    try {
      setLoadingProductData(true);
      const [prodRes, instRes] = await Promise.all([
        axiosClient.get(apiEndpoints.cbam.product.list),
        axiosClient.get(apiEndpoints.cbam.install.list)
      ]);
      const prods: ProductRecord[] = Array.isArray(prodRes.data) ? prodRes.data : [];
      const installs: InstallRecord[] = Array.isArray(instRes.data) ? instRes.data : [];
      const map: Record<number, string> = installs.reduce((acc, i) => { acc[i.id] = i.install_name; return acc; }, {} as Record<number, string>);
      setProductOptions(prods);
      setInstallMap(map);
      if (prods.length > 0) {
        setSelectedProductId(prods[0].id);
      }
    } catch (e) {
      alert('제품/설치 데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoadingProductData(false);
    }
  };

  // 보고서 다운로드 함수
  const handleDownloadReport = (type: 'pdf' | 'excel') => {
    console.log(`${type} 보고서 다운로드 시작`);
    // 실제 구현에서는 서버에서 보고서를 생성하고 다운로드
    alert(`${type.toUpperCase()} 보고서 다운로드가 시작됩니다.`);
  };

  // 폼 데이터 변경 핸들러
  const handleFormChange = (field: string, value: string) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...(prev[parent as keyof typeof prev] as any),
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  // 다국어 텍스트
  const texts = {
    korean: {
      title: 'CBAM 템플릿',
      companyName: '발행처: 회사명',
      issueDate: '발행일자: 발행 일자',
      
      productionPeriod: '생산 기간',
      startPeriod: '시작 기간',
      endPeriod: '종료 기간',
      facilityInfo: '시설군 정보',
      workplaceName: '사업장 명',
      address: '주소',
      country: '국가/코드',
      city: '도시',
      postcode: '우편번호',
      workplace: '사업장',
      currencyCode: 'UN 통화 코드',
      coordinates: '좌표(위 경도)',
      productInfo: '제품 생산 info',
      productGroup: '품목군',
      cnCode: 'CN코드/제품명',
      productionProcess: '생산 공정',
      process: '공정',
      productionVolume: '생산량',
      ingredient: '원료',
      fuel: '연료',
      emission: '배출량',
      precursorMaterial: '전구 물질 여부',
      precursorInfo: '전구체 info',
      precursorMaterialName: '전구물질 명',
      movementRoute: '이동 루트 (국가 or 생산 공정)',
      consumptionProcess: '소모 공정',
      emissionFactor: '배출계수',
      cbamDefaultValue: 'CBAM 기본값*',
      contact: 'Contact',
      email: 'Email',
      representativeNumber: '대표 번호',
      disclaimer: '* 기업 자세 계산값이 존재할 경우 에너지, 원료별 계수값을 사랑하고 해당 증빙자료 산출',
      companySeal: '회사 직인 (인)',
      downloadPdf: 'PDF 다운로드',
      downloadExcel: 'Excel 다운로드',
      productSectionTitle: '제품 정보',
      loadProductInfo: '제품 정보 불러오기',
      selectProduct: '제품 선택',
      installName: '사업장 명',
      productName: '제품명',
      goodsName: '품목명',
      goodsEngName: '품목영문명',
      aggrGoodsName: '품목군명',
      aggrGoodsEngName: '품목군영문명',
      euSell: 'EU 수출량',
      productAttrEm: '제품 배출량'
    },
    english: {
      title: 'CBAM Template',
      companyName: 'Issuer: Company Name',
      issueDate: 'Issue Date',
      productionPeriod: 'Reporting period',
      startPeriod: 'start',
      endPeriod: 'End',
      facilityInfo: 'About the installation',
      workplaceName: 'Name of the installation',
      address: 'Address',
      country: 'Country',
      city: 'City',
      postcode: 'Post code',
      workplace: 'Workplace',
      currencyCode: 'UNLOCODE:',
      coordinates: 'Coordinates of the main emssion source (latitude, longitude)',
      productInfo: 'Product information',
      productGroup: 'Product',
      cnCode: 'CN Code/ Product name',
      productionProcess: 'Production Process',
      process: 'Route',
      productionVolume: 'Production Volume',
      ingredient: 'ingredient',
      fuel: 'fuel',
      emission: 'Emission',
      precursorMaterial: 'Aggregated goods?',
      precursorInfo: 'Precursor Info',
      precursorMaterialName: 'Precursor Material Name',
      movementRoute: 'Movement Route (Country or Production Process)',
      consumptionProcess: 'Consumption Process',
      emissionFactor: 'Emission Factor',
      cbamDefaultValue: 'CBAM Default Value*',
      contact: 'Contact',
      email: 'EMAIL',
      representativeNumber: 'CONTACT',
      disclaimer: '* If detailed calculation values exist for the company, use energy and raw material coefficients and calculate the corresponding supporting data',
      companySeal: 'Official Company Stamp',
      downloadPdf: 'Download PDF',
      downloadExcel: 'Download Excel',
      productSectionTitle: 'Product information',
      loadProductInfo: 'Load product info',
      selectProduct: 'Select product',
      installName: 'Installation name',
      productName: 'Product name',
      goodsName: 'Goods name (KR)',
      goodsEngName: 'Goods name (EN)',
      aggrGoodsName: 'Aggregated goods (KR)',
      aggrGoodsEngName: 'Aggregated goods (EN)',
      euSell: 'EU sell quantity',
      productAttrEm: 'Product attr emissions'
    }
  };

  const t = texts[language];

  const inputSm = 'w-32 px-2 py-1 bg-white/10 border border-white/20 rounded text-white';
  const input = 'w-full px-3 py-2 bg-white/10 border border-white/20 rounded text-white';
  const inputInline = 'px-3 py-2 bg-white/10 border border-white/20 rounded text-white';

  return (
    <CbamLayout>
      <div className='space-y-6'>
        {/* 헤더 카드 */}
        <div className='stitch-card p-6'>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-white mr-3" />
              <h1 className="text-2xl font-bold text-white">{t.title}</h1>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={toggleLanguage}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <Languages className="h-4 w-4" />
                <span>{language === 'korean' ? 'English' : '한국어'}</span>
              </button>
              <button
                onClick={() => handleDownloadReport('pdf')}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>{t.downloadPdf}</span>
              </button>
              <button
                onClick={() => handleDownloadReport('excel')}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>{t.downloadExcel}</span>
              </button>
            </div>
          </div>
        </div>

        {/* 메인 카드 */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-8">
          
          {/* 보고서 헤더 */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-4">{t.title}</h1>
            <div className="flex justify-end space-x-8 text-sm text-white/70">
              <div className="flex items-center space-x-2">
                <span>{t.companyName}</span>
                <input
                  type="text"
                  value={HARDCODED_DATA.installation[language]}
                  readOnly
                  className={inputSm}
                />
              </div>
              <div className="flex items-center space-x-2">
                <span>{t.issueDate}</span>
                <input
                  type="date"
                  value={todayStr}
                  readOnly
                  className={inputSm}
                />
              </div>
            </div>
          </div>

          {/* 1. 생산 기간 & 시설군 정보 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">
              {t.productionPeriod} & {t.facilityInfo}
            </h2>
            
            {/* 생산 기간 */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-white mb-3">{t.productionPeriod}</h3>
              <div className="flex items-center space-x-4">
                <input
                  type="date"
                  value="2025-01-01"
                  readOnly
                  className={inputInline}
                />
                <span>~</span>
                <input
                  type="date"
                  value="2025-12-31"
                  readOnly
                  className={inputInline}
                />
              </div>
            </div>

            {/* 시설군 정보 */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-white mb-3">1. {t.facilityInfo}</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">
                    {t.workplaceName}
                  </label>
                  <input
                    type="text"
                    value={HARDCODED_DATA.installation[language]}
                    readOnly
                    className={input}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">
                    {t.address}
                  </label>
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={HARDCODED_DATA.contact.street[language]}
                      readOnly
                      className={input}
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={HARDCODED_DATA.location.country[language]}
                        readOnly
                        className={inputInline}
                      />
                      <input
                        type="text"
                        value={HARDCODED_DATA.location.city[language]}
                        readOnly
                        className={inputInline}
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <input
                        type="text"
                        value={HARDCODED_DATA.contact.postcode}
                        readOnly
                        className={inputInline}
                      />
                      <input
                        type="text"
                        value={HARDCODED_DATA.contact.number[language]}
                        readOnly
                        className={inputInline}
                      />
                      <input
                        type="text"
                        value={HARDCODED_DATA.location.unlocode}
                        readOnly
                        className={inputInline}
                      />
                    </div>
                    <input
                      type="text"
                      value={`${HARDCODED_DATA.location.coordinates.latitude}, ${HARDCODED_DATA.location.coordinates.longitude}`}
                      readOnly
                      className={input}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 2. 제품 정보 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">2. {t.productSectionTitle}</h2>
            <div className="flex items-center gap-2 mb-4">
              <button
                onClick={handleLoadProductData}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                disabled={loadingProductData}
              >
                {loadingProductData ? '불러오는 중...' : t.loadProductInfo}
              </button>
              {productOptions.length > 0 && (
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value ? parseInt(e.target.value) : '')}
                  className="select-dark"
                >
                  <option value="">{t.selectProduct}</option>
                  {productOptions.map((p) => (
                    <option key={p.id} value={p.id}>
                      {installMap[p.install_id] ? `${installMap[p.install_id]} · ` : ''}{p.product_name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {selectedProductId !== '' && productOptions.length > 0 && (
              (() => {
                const p = productOptions.find(pp => pp.id === selectedProductId);
                if (!p) return null;
                const installName = installMap[p.install_id] || '';
                return (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* 공통 */}
                    <div>
                      <label className="block text-sm font-medium text-white/70 mb-2">{t.installName}</label>
                      <input type="text" readOnly value={installName} className={input} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-white/70 mb-2">{t.productName}</label>
                      <input type="text" readOnly value={p.product_name} className={input} />
                    </div>
                    {language === 'korean' ? (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-white/70 mb-2">{t.goodsName}</label>
                          <input type="text" readOnly value={p.goods_name || ''} className={input} />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-white/70 mb-2">{t.aggrGoodsName}</label>
                          <input type="text" readOnly value={p.aggrgoods_name || ''} className={input} />
                        </div>
                      </>
                    ) : (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-white/70 mb-2">{t.goodsEngName}</label>
                          <input type="text" readOnly value={p.goods_engname || ''} className={input} />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-white/70 mb-2">{t.aggrGoodsEngName}</label>
                          <input type="text" readOnly value={p.aggrgoods_engname || ''} className={input} />
                        </div>
                      </>
                    )}
                    {/* CN 코드 표시 */}
                    <div>
                      <label className="block text-sm font-medium text-white/70 mb-2">CN Code</label>
                      <input type="text" readOnly value={p.cncode_total || ''} className={input} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-white/70 mb-2">{t.euSell}</label>
                      <input type="text" readOnly value={String(p.product_eusell ?? '')} className={input} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-white/70 mb-2">{t.productAttrEm}</label>
                      <input type="text" readOnly value={typeof p.attr_em === 'number' ? `${p.attr_em.toFixed(2)} tCO2e` : ''} className={input} />
                    </div>
                  </div>
                );
              })()
            )}
          </div>

          {/* 3. 연락처 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">
              3. {t.contact}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  {t.email}
                </label>
                <input
                  type="email"
                  value={HARDCODED_DATA.contact.email}
                  readOnly
                  className={input}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  {t.representativeNumber}
                </label>
                <input
                  type="text"
                  value={HARDCODED_DATA.contact.telephone}
                  readOnly
                  className={input}
                />
              </div>
            </div>
          </div>

          {/* 푸터 */}
          <div className="flex justify-between items-end">
            <div className="text-xs text-white/60 max-w-md">
              {t.disclaimer}
            </div>
            <div className="text-center">
              <div className="border border-white/30 w-32 h-20 mb-2"></div>
              <p className="text-sm text-white/70">{t.companySeal}</p>
            </div>
          </div>
        </div>
      </div>
    </CbamLayout>
  );
}
