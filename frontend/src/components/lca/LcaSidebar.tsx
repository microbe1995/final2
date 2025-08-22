'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  HomeIcon, 
  ClipboardDocumentListIcon, 
  ChartBarIcon, 
  CalculatorIcon, 
  DocumentTextIcon
} from '@heroicons/react/24/outline';

const menuItems = [
  {
    name: '대시보드',
    href: '/lca',
    icon: HomeIcon,
    description: 'LCA 프로젝트 개요',
  },
  {
    name: '목적 및 범위',
    href: '/lca/scope',
    icon: ClipboardDocumentListIcon,
    description: '프로젝트 스코프 정의',
  },
  {
    name: '생명주기 인벤토리',
    href: '/lca/lci',
    icon: ChartBarIcon,
    description: 'LCI 데이터 입력 및 관리',
  },
  {
    name: '생명주기 영향평가',
    href: '/lca/lcia',
    icon: CalculatorIcon,
    description: 'LCIA 계산 및 결과',
  },
  {
    name: '해석',
    href: '/lca/interpretation',
    icon: DocumentTextIcon,
    description: '결과 해석 및 분석',
  },
  {
    name: '보고서',
    href: '/lca/report',
    icon: DocumentTextIcon,
    description: 'LCA 보고서 생성',
  },
];

export default function LcaSidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-ecotrace-secondary border-r border-ecotrace-border h-screen flex-shrink-0">
      <div className="flex flex-col h-full">
        {/* 사이드바 헤더 */}
        <div className="flex items-center justify-between p-4 border-b border-ecotrace-border">
          <h2 className="text-lg font-semibold text-white">LCA 모듈</h2>
          <span className="text-xs text-ecotrace-textSecondary">생명주기 평가</span>
        </div>
        
        {/* 사이드바 네비게이션 */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3 group ${
                  isActive
                    ? 'bg-ecotrace-accent text-white'
                    : 'text-ecotrace-textSecondary hover:text-white hover:bg-ecotrace-secondary/50'
                }`}
              >
                <Icon className={`w-5 h-5 ${
                  isActive
                    ? 'text-white'
                    : 'text-ecotrace-textSecondary group-hover:text-white'
                }`} />
                <div className="flex-1">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs opacity-75">{item.description}</div>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* 사이드바 푸터 */}
        <div className="p-4 border-t border-ecotrace-border">
          <div className="text-xs text-ecotrace-textSecondary text-center">
            GreenSteel LCA v1.0.0
          </div>
        </div>
      </div>
    </div>
  );
}
