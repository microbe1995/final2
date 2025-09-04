'use client';

import React from 'react';
import CommonShell from '@/components/common/CommonShell';
import ProcessManager from '@/components/cbam/ProcessManager';

// ============================================================================
// 🎯 CBAM 산정경계 설정 페이지
// ============================================================================

export default function ProcessManagerPage() {
  return (
    <CommonShell>
      <div className="w-full h-screen flex flex-col">
        {/* 헤더 문구 제거 (중복 방지) */}
        
        <div className="flex-1 min-h-0">
          <ProcessManager />
        </div>
      </div>
    </CommonShell>
  );
}
