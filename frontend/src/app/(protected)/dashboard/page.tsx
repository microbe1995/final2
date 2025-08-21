'use client';

import React from 'react';
import CommonShell from '@/components/CommonShell';
import GatewayStatus from '@/components/GatewayStatus';

const DashboardPage: React.FC = () => {
  return (
    <CommonShell>
      <div className='space-y-6'>
        <div className='flex flex-col gap-3'>
          <h1 className='text-3xl font-bold text-ecotrace-text'>
            GreenSteel 대시보드
          </h1>
          <p className='text-ecotrace-textSecondary'>
            ESG 관리 플랫폼에 오신 것을 환영합니다
          </p>
        </div>

        <div className='bg-ecotrace-surface border border-ecotrace-border rounded-lg p-6'>
          <h2 className='text-xl font-semibold text-ecotrace-text mb-2'>
            환영합니다!
          </h2>
          <p className='text-ecotrace-textSecondary'>
            GreenSteel은 LCA, CBAM, ESG 관리의 모든 것을 제공합니다.
          </p>
        </div>

        {/* Gateway 상태 컴포넌트 추가 */}
        <GatewayStatus />

        <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
          <div className='bg-blue-50 border border-blue-200 rounded-lg p-6'>
            <h3 className='text-lg font-semibold text-blue-800 mb-2'>LCA</h3>
            <p className='text-blue-700 text-sm'>생명주기 평가</p>
          </div>

          <div className='bg-purple-50 border border-purple-200 rounded-lg p-6'>
            <h3 className='text-lg font-semibold text-purple-800 mb-2'>CBAM</h3>
            <p className='text-purple-700 text-sm'>탄소 국경 조정</p>
          </div>

          <div className='bg-orange-50 border border-orange-200 rounded-lg p-6'>
            <h3 className='text-lg font-semibold text-orange-800 mb-2'>
              데이터
            </h3>
            <p className='text-orange-700 text-sm'>업로드 및 관리</p>
          </div>
        </div>
      </div>
    </CommonShell>
  );
};

export default DashboardPage;
