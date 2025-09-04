'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  ClipboardList,
  Factory,
  Workflow,
  FileText,
} from 'lucide-react';

const menuItems = [
  { name: '투입물', href: '/cbam', icon: ClipboardList, description: '투입 데이터 관리' },
  { name: '사업장관리', href: '/cbam/install', icon: Factory, description: '시설군 생성 및 관리' },
  { name: '산정경계설정', href: '/cbam/process-manager', icon: Workflow, description: '경계 설정 및 노드' },
  { name: '보고서', href: '/cbam/report', icon: FileText, description: 'CBAM 보고서' },
];

interface Props { embedded?: boolean }

export default function CbamSidebar({ embedded = false }: Props) {
  const pathname = usePathname();
  const Nav = (
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
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-ecotrace-textSecondary group-hover:text-white'}`} />
                <div className="flex-1">
                  <div className="font-medium">{item.name}</div>
                </div>
              </Link>
            );
          })}
    </nav>
  );

  if (embedded) {
    return Nav;
  }

  return (
    <div className="w-64 bg-ecotrace-secondary border-r border-ecotrace-border h-screen flex-shrink-0">
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between p-4 border-b border-ecotrace-border">
          <h2 className="text-lg font-semibold text-white">CBAM 모듈</h2>
          <span className="text-xs text-ecotrace-textSecondary">프로세스/계산</span>
        </div>
        {Nav}
        <div className="p-4 border-t border-ecotrace-border">
          <div className="text-xs text-ecotrace-textSecondary text-center">GreenSteel CBAM v1.0.0</div>
        </div>
      </div>
    </div>
  );
}


