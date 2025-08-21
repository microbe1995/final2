'use client';

import { useState } from 'react';
import LcaLayout from '@/components/lca/LcaLayout';

export default function ReportPage() {
  const [loading, setLoading] = useState(false);

  const handleDownload = (type: 'pdf' | 'excel') => {
    setLoading(true);
    // TODO: 백엔드 연결 시 실제 다운로드 호출
    setTimeout(() => {
      alert(`${type.toUpperCase()} 다운로드는 추후 제공 예정입니다.`);
      setLoading(false);
    }, 1000);
  };

  // 샘플 데이터
  const reportData = {
    productInfo: {
      productName: '고강도 철강 제품',
      owner: '김철강',
      period: '2024년 1월 ~ 12월',
      productClass: '철강 제품',
      majorFunction: '구조용 재료',
      secondaryFunction: '내식성',
      unit: '1톤',
      packaging: { min: '최소', out: '출하용' },
      productFeatures: '고강도, 내식성',
    },
    scope: {
      lifecycle: '원료채취 ~ 제조',
      dataQuality: {
        temporal: '2024년 기준',
        technical: '현재 기술 수준',
        geographic: '국내',
        source: '공장 데이터',
      },
    },
    methodTable: [
      { category: '기후변화', indicator: 'GWP', unit: 'kg CO2-eq' },
      { category: '산성화', indicator: 'AP', unit: 'kg SO2-eq' },
      { category: '부영양화', indicator: 'EP', unit: 'kg PO4-eq' },
    ],
    resultsTable: [
      {
        category: '기후변화',
        preManufacture: 150,
        manufacturing: 850,
        total: 1000,
        unit: 'kg CO2-eq',
        manufacturingContribution: 85.0,
        totalContribution: 100.0,
      },
      {
        category: '산성화',
        preManufacture: 2.5,
        manufacturing: 7.5,
        total: 10.0,
        unit: 'kg SO2-eq',
        manufacturingContribution: 75.0,
        totalContribution: 100.0,
      },
      {
        category: '부영양화',
        preManufacture: 0.8,
        manufacturing: 1.2,
        total: 2.0,
        unit: 'kg PO4-eq',
        manufacturingContribution: 60.0,
        totalContribution: 100.0,
      },
    ],
  };

  return (
    <LcaLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-ecotrace-text mb-2">{reportData.productInfo.productName}</h1>
          <p className="text-ecotrace-textSecondary">담당자: {reportData.productInfo.owner} | 기간: {reportData.productInfo.period}</p>
        </div>

        <div className="space-y-8">
          {/* 헤더 액션 */}
          <div className="flex flex-wrap gap-2 justify-end">
            <button
              onClick={() => handleDownload('pdf')}
              disabled={loading}
              className="px-3 py-1 text-sm rounded border border-ecotrace-border hover:bg-ecotrace-secondary/10 transition-colors text-ecotrace-text disabled:opacity-50"
            >
              {loading ? '처리 중...' : 'PDF 다운로드'}
            </button>
            <button
              onClick={() => handleDownload('excel')}
              disabled={loading}
              className="px-3 py-1 text-sm rounded border border-ecotrace-border hover:bg-ecotrace-secondary/10 transition-colors text-ecotrace-text disabled:opacity-50"
            >
              {loading ? '처리 중...' : 'Excel 다운로드'}
            </button>
          </div>

          {/* 1. 제품 정보 */}
          <section className="bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-ecotrace-text mb-4 flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              1. 철강 제품 정보
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-ecotrace-background border border-ecotrace-border rounded-lg p-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">제품명</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.productName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">제품 분류</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.productClass}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">주요 기능</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.majorFunction}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">보조 기능</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.secondaryFunction}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">기준 단위</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.unit}</span>
                  </div>
                </div>
              </div>
              <div className="bg-ecotrace-background border border-ecotrace-border rounded-lg p-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">최소 포장재</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.packaging.min}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">출하 포장재</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.packaging.out}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ecotrace-textSecondary">제품 특성</span>
                    <span className="text-ecotrace-text font-medium">{reportData.productInfo.productFeatures}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* 2. LCA 수행 정보 */}
          <section className="bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-ecotrace-text mb-4 flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
              2. LCA 수행 정보
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-ecotrace-accent mb-3">생애주기 범위</h3>
                <div className="flex items-center gap-4 p-4 bg-ecotrace-accent/10 border border-ecotrace-accent/20 rounded-lg">
                  <div className="flex-1 h-2 bg-ecotrace-secondary relative rounded">
                    <div className="absolute left-0 top-0 h-full w-1/3 bg-ecotrace-accent rounded-l"></div>
                    <div className="absolute left-1/3 top-0 h-full w-1/3 bg-ecotrace-accent/70"></div>
                  </div>
                  <div className="text-sm text-ecotrace-accent">{reportData.scope.lifecycle}</div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-ecotrace-accent mb-3">데이터 품질</h3>
                <div className="bg-ecotrace-background border border-ecotrace-border rounded-lg p-4">
                  <ul className="space-y-2 text-sm">
                    <li className="text-ecotrace-text">• <strong>시간적 범위:</strong> {reportData.scope.dataQuality.temporal}</li>
                    <li className="text-ecotrace-text">• <strong>기술적 범위:</strong> {reportData.scope.dataQuality.technical}</li>
                    <li className="text-ecotrace-text">• <strong>지리적 범위:</strong> {reportData.scope.dataQuality.geographic}</li>
                    <li className="text-ecotrace-text">• <strong>데이터 출처:</strong> {reportData.scope.dataQuality.source}</li>
                  </ul>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-ecotrace-accent mb-3">영향평가 방법론</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-ecotrace-border">
                        <th className="text-left p-2 text-ecotrace-text font-medium">LCIA Method</th>
                        <th className="text-left p-2 text-ecotrace-text font-medium">영향범주</th>
                        <th className="text-left p-2 text-ecotrace-text font-medium">범주지표</th>
                        <th className="text-left p-2 text-ecotrace-text font-medium">단위</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reportData.methodTable.map((method, index) => (
                        <tr key={index} className="border-b border-ecotrace-border/30">
                          <td className="p-2 text-ecotrace-text">IPCC 2021 GWP</td>
                          <td className="p-2 text-ecotrace-text">{method.category}</td>
                          <td className="p-2 text-ecotrace-text">{method.indicator}</td>
                          <td className="p-2 text-ecotrace-text">{method.unit}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>

          {/* 3. 결과 테이블 */}
          <section className="bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-ecotrace-text mb-4 flex items-center">
              <span className="w-2 h-2 bg-orange-500 rounded-full mr-3"></span>
              3. 철강 LCA 결과
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-ecotrace-border">
                    <th className="text-left p-2 text-ecotrace-text font-medium">영향범주</th>
                    <th className="text-left p-2 text-ecotrace-text font-medium">제조전</th>
                    <th className="text-left p-2 text-ecotrace-text font-medium">제조</th>
                    <th className="text-left p-2 text-ecotrace-text font-medium">전과정</th>
                    <th className="text-left p-2 text-ecotrace-text font-medium">단위</th>
                    <th className="text-left p-2 text-ecotrace-text font-medium">제조 기여율</th>
                    <th className="text-left p-2 text-ecotrace-text font-medium">전체 기여율</th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.resultsTable.map((result, index) => (
                    <tr key={index} className="border-b border-ecotrace-border/30">
                      <td className="p-2 text-ecotrace-text font-medium">{result.category}</td>
                      <td className="p-2 text-ecotrace-text">{result.preManufacture.toFixed(0)}</td>
                      <td className="p-2 text-ecotrace-text">{result.manufacturing.toFixed(0)}</td>
                      <td className="p-2 text-ecotrace-text font-medium">{result.total.toFixed(0)}</td>
                      <td className="p-2 text-ecotrace-text">{result.unit}</td>
                      <td className="p-2 text-ecotrace-text">{result.manufacturingContribution?.toFixed(1)}%</td>
                      <td className="p-2 text-ecotrace-text">{result.totalContribution?.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </LcaLayout>
  );
}
