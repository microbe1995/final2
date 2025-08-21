'use client';

import { useRouter } from 'next/navigation';
import LcaLayout from '@/components/lca/LcaLayout';

export default function InterpretationPage() {
  const router = useRouter();

  const handleNext = () => {
    router.push('/lca/report');
  };

  const contributionData = [
    { name: '고로 제철', share: 52.3 },
    { name: '전로 제강', share: 28.7 },
    { name: '압연 공정', share: 12.4 },
    { name: '원료 운송', share: 6.6 },
  ];

  const sensitivityData = [
    { parameter: '코크스 사용량', delta: 10, impactDelta: 15.2 },
    { parameter: '전력 사용량', delta: 15, impactDelta: 8.7 },
    { parameter: '철광석 품질', delta: 20, impactDelta: 12.1 },
  ];

  return (
    <LcaLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-ecotrace-text mb-2">해석 (Interpretation)</h1>
          <p className="text-ecotrace-textSecondary">LCIA 결과를 분석하고 철강 제품의 환경영향을 해석합니다</p>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* 메인 콘텐츠 */}
          <div className="flex-1 space-y-8">
            {/* 기여도 분석 */}
            <div className="bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-ecotrace-text mb-4 flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                기여도 분석
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-ecotrace-border">
                          <th className="text-left p-2 text-ecotrace-text font-medium">공정</th>
                          <th className="text-left p-2 text-ecotrace-text font-medium">기여율 (%)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {contributionData.map((item, index) => (
                          <tr key={index} className="border-b border-ecotrace-border/30">
                            <td className="p-2 text-ecotrace-text">{item.name}</td>
                            <td className="p-2 text-ecotrace-text">{item.share}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                <div className="bg-ecotrace-secondary/20 border border-ecotrace-border rounded-lg p-4 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-ecotrace-textSecondary text-sm mb-2">기여도 차트</div>
                    <div className="text-ecotrace-textSecondary text-xs">차트 컴포넌트</div>
                  </div>
                </div>
              </div>
            </div>

            {/* 민감도 분석 */}
            <div className="bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-ecotrace-text mb-4 flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                민감도 분석
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-ecotrace-border">
                          <th className="text-left p-2 text-ecotrace-text font-medium">매개변수</th>
                          <th className="text-left p-2 text-ecotrace-text font-medium">변화율 (%)</th>
                          <th className="text-left p-2 text-ecotrace-text font-medium">영향 변화 (%)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sensitivityData.map((item, index) => (
                          <tr key={index} className="border-b border-ecotrace-border/30">
                            <td className="p-2 text-ecotrace-text">{item.parameter}</td>
                            <td className="p-2 text-ecotrace-text">±{item.delta}%</td>
                            <td className="p-2 text-ecotrace-text">±{item.impactDelta}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                <div className="bg-ecotrace-secondary/20 border border-ecotrace-border rounded-lg p-4 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-ecotrace-textSecondary text-sm mb-2">민감도 차트</div>
                    <div className="text-ecotrace-textSecondary text-xs">차트 컴포넌트</div>
                  </div>
                </div>
              </div>
            </div>

            {/* 액션 버튼 */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleNext}
                className="bg-ecotrace-accent text-white px-4 py-2 rounded-lg hover:bg-ecotrace-accent/90 transition-colors text-sm font-medium"
              >
                보고서로 이동
              </button>
            </div>
          </div>

          {/* 사이드바 */}
          <aside className="w-full lg:w-80">
            <div className="sticky top-8 bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6 shadow-sm max-h-[calc(100vh-8rem)] overflow-y-auto">
              <h3 className="text-lg font-semibold text-ecotrace-text mb-4 flex items-center">
                <span className="w-2 h-2 bg-orange-500 rounded-full mr-3"></span>
                해석 요약
              </h3>
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-ecotrace-secondary/30">
                  <div className="font-medium text-ecotrace-text mb-1">주요 기여 공정</div>
                  <div className="text-ecotrace-textSecondary text-sm">고로 제철 (52.3%)</div>
                </div>
                <div className="p-3 rounded-lg bg-ecotrace-secondary/30">
                  <div className="font-medium text-ecotrace-text mb-1">민감도 분석</div>
                  <div className="text-ecotrace-textSecondary text-sm">코크스 사용량이 가장 민감</div>
                </div>
                <div className="p-3 rounded-lg bg-ecotrace-secondary/30">
                  <div className="font-medium text-ecotrace-text mb-1">개선 권고</div>
                  <div className="text-ecotrace-textSecondary text-sm">수소 환원 기술 검토</div>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </LcaLayout>
  );
}
