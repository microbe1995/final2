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
        <div className="flex-shrink-0 p-6">
          <h1 className="text-3xl font-bold text-white mb-2">CBAM 산정경계 설정</h1>
          <p className="text-white/60">
            CBAM 배출량 산정을 위한 경계를 설정하고 노드를 생성합니다.
          </p>
        </div>
        
        <div className="flex-1 min-h-0">
          <ProcessManager />
        </div>
      </div>
    </CommonShell>
  );
}
