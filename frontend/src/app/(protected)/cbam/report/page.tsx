'use client';

import React, { useState, useEffect } from 'react';
import { Download, FileText, Globe, Languages } from 'lucide-react';

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
      downloadExcel: 'Excel 다운로드'
    },
    english: {
      title: 'CBAM Template',
      companyName: 'Issuer: Company Name',
      issueDate: 'Issue Date: Issue Date',
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
      downloadExcel: 'Download Excel'
    }
  };

  const t = texts[language];

  return (
    <div className="min-h-screen bg-white">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
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
      </div>

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow-lg rounded-lg p-8">
          
          {/* 보고서 헤더 */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{t.title}</h1>
            <div className="flex justify-end space-x-8 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <span>{t.companyName}</span>
                <input
                  type="text"
                  value={HARDCODED_DATA.installation[language]}
                  readOnly
                  className="w-32 px-2 py-1 border border-gray-300 rounded bg-gray-50 text-gray-800"
                />
              </div>
              <div className="flex items-center space-x-2">
                <span>{t.issueDate}</span>
                <input
                  type="date"
                  value="2024-01-15"
                  readOnly
                  className="w-32 px-2 py-1 border border-gray-300 rounded bg-gray-50 text-gray-800"
                />
              </div>
            </div>
          </div>

          {/* 1. 생산 기간 & 시설군 정보 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {t.productionPeriod} & {t.facilityInfo}
            </h2>
            
            {/* 생산 기간 */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-3">{t.productionPeriod}</h3>
              <div className="flex items-center space-x-4">
                <input
                  type="date"
                  value="2024-01-01"
                  readOnly
                  className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                />
                <span>~</span>
                <input
                  type="date"
                  value="2024-12-31"
                  readOnly
                  className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                />
              </div>
            </div>

            {/* 시설군 정보 */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-3">1. {t.facilityInfo}</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    {t.workplaceName}
                  </label>
                  <input
                    type="text"
                    value={HARDCODED_DATA.installation[language]}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    {t.address}
                  </label>
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={HARDCODED_DATA.contact.street[language]}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={HARDCODED_DATA.location.country[language]}
                        readOnly
                        className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                      />
                      <input
                        type="text"
                        value={HARDCODED_DATA.location.city[language]}
                        readOnly
                        className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <input
                        type="text"
                        value={HARDCODED_DATA.contact.postcode}
                        readOnly
                        className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                      />
                      <input
                        type="text"
                        value={HARDCODED_DATA.contact.number[language]}
                        readOnly
                        className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                      />
                      <input
                        type="text"
                        value={HARDCODED_DATA.location.unlocode}
                        readOnly
                        className="px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                      />
                    </div>
                    <input
                      type="text"
                      value={`${HARDCODED_DATA.location.coordinates.latitude}, ${HARDCODED_DATA.location.coordinates.longitude}`}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

    

                         
          {/* 2. 연락처 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              2. {t.contact}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  {t.email}
                </label>
                <input
                  type="email"
                  value={HARDCODED_DATA.contact.email}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  {t.representativeNumber}
                </label>
                <input
                  type="text"
                  value={HARDCODED_DATA.contact.telephone}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-800"
                />
              </div>
            </div>
          </div>

          {/* 푸터 */}
          <div className="flex justify-between items-end">
            <div className="text-xs text-gray-500 max-w-md">
              {t.disclaimer}
            </div>
            <div className="text-center">
              <div className="border border-gray-300 w-32 h-20 mb-2"></div>
              <p className="text-sm text-gray-600">{t.companySeal}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
