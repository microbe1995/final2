'use client';

import { FC } from 'react';
import {
  ClipboardList,
  Factory,
  Workflow,
  FileText,
  Settings,
} from 'lucide-react';

type TabKey = 'overview' | 'install' | 'boundary' | 'reports' | 'settings';

interface CbamSidebarProps {
  activeTab: TabKey;
  onSelect: (tab: TabKey) => void;
}

const items: Array<{ key: TabKey; name: string; description: string; icon: any }> = [
  { key: 'overview', name: '투입물', description: '투입 데이터 관리', icon: ClipboardList },
  { key: 'install', name: '사업장관리', description: '시설군 생성 및 관리', icon: Factory },
  { key: 'boundary', name: '산정경계설정', description: '경계 설정 및 노드', icon: Workflow },
  { key: 'reports', name: '보고서', description: 'CBAM 보고서', icon: FileText },
  { key: 'settings', name: '설정', description: '환경설정', icon: Settings },
];

const CbamSidebar: FC<CbamSidebarProps> = ({ activeTab, onSelect }) => {
  return (
    <div className="w-64 bg-ecotrace-secondary border-r border-ecotrace-border h-[calc(100vh-0px)] flex-shrink-0">
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between p-4 border-b border-ecotrace-border">
          <h2 className="text-lg font-semibold text-white">CBAM 모듈</h2>
          <span className="text-xs text-ecotrace-textSecondary">프로세스/계산</span>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {items.map(({ key, name, description, icon: Icon }) => {
            const isActive = activeTab === key;
            return (
              <button
                key={key}
                onClick={() => onSelect(key)}
                className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3 group ${
                  isActive
                    ? 'bg-ecotrace-accent text-white'
                    : 'text-ecotrace-textSecondary hover:text-white hover:bg-ecotrace-secondary/50'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-ecotrace-textSecondary group-hover:text-white'}`} />
                <div className="flex-1">
                  <div className="font-medium">{name}</div>
                  <div className="text-xs opacity-75">{description}</div>
                </div>
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-ecotrace-border">
          <div className="text-xs text-ecotrace-textSecondary text-center">
            GreenSteel CBAM v1.0.0
          </div>
        </div>
      </div>
    </div>
  );
};

export default CbamSidebar;


