'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface Tab {
  id: string;
  label: string;
  content?: React.ReactNode;
}

interface TabGroupProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  variant?: 'default' | 'underline';
  className?: string;
}

const TabGroup: React.FC<TabGroupProps> = ({
  tabs,
  activeTab,
  onTabChange,
  variant = 'default',
  className,
}) => {
  const tabVariants = {
    default: 'px-4 py-2 rounded-lg transition-colors duration-200',
    underline: 'px-4 py-4 border-b-2 transition-colors duration-200',
  };

  const activeVariants = {
    default: 'bg-ecotrace-primary text-white',
    underline: 'border-ecotrace-accent text-ecotrace-text',
  };

  const inactiveVariants = {
    default:
      'text-ecotrace-textSecondary hover:text-ecotrace-text hover:bg-ecotrace-surface',
    underline:
      'border-transparent text-ecotrace-textSecondary hover:text-ecotrace-text',
  };

  return (
    <div className={cn('w-full', className)}>
      {/* 탭 헤더 */}
      <div className='flex border-b border-ecotrace-border'>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              tabVariants[variant],
              activeTab === tab.id
                ? activeVariants[variant]
                : inactiveVariants[variant],
              'focus:outline-none focus:ring-2 focus:ring-ecotrace-primary focus:ring-offset-2 focus:ring-offset-ecotrace-background'
            )}
            role='tab'
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 탭 패널 */}
      {tabs.map(tab => (
        <div
          key={tab.id}
          id={`panel-${tab.id}`}
          role='tabpanel'
          aria-labelledby={`tab-${tab.id}`}
          className={cn('mt-4', activeTab === tab.id ? 'block' : 'hidden')}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
};

export default TabGroup;
