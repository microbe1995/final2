'use client';

import React from 'react';
import CbamLayout from '@/components/templates/CbamLayout';
import ProcessManager from '@/components/templates/ProcessManager';

// ============================================================================
// 🎯 CBAM 산정경계 설정 페이지
// ============================================================================

export default function ProcessManagerPage() {
  return (
    <CbamLayout>
      <div className="w-full h-[80vh] min-h-[560px] flex flex-col">
        {/* 헤더 문구 제거 (중복 방지) */}
        
        <div className="flex-1 min-h-0">
          <ProcessManager />
        </div>
      </div>
    </CbamLayout>
  );
}
