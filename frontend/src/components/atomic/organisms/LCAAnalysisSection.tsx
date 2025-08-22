import React from 'react';
import InfoCard from '@/components/atomic/molecules/InfoCard';
import ProgressBar from '@/components/atomic/atoms/ProgressBar';
import DataTable from '@/components/atomic/atoms/DataTable';
import { BarChart3 } from 'lucide-react';

interface LCAAnalysisSectionProps {
  methodTable: Array<{
    method: string;
    category: string;
    indicator: string;
    unit: string;
  }>;
  className?: string;
}

const LCAAnalysisSection: React.FC<LCAAnalysisSectionProps> = ({
  methodTable,
  className = '',
}) => {
  const columns = [
    { key: 'method', label: 'LCIA Method' },
    { key: 'category', label: 'Category' },
    { key: 'indicator', label: 'Indicator' },
    { key: 'unit', label: 'Unit' },
  ];

  return (
    <InfoCard title='LCA 수행 정보' icon={BarChart3} className={className}>
      <div className='space-y-4'>
        {/* Lifecycle bar */}
        <div className='p-4 bg-muted/50 rounded-lg'>
          <ProgressBar
            progress={75}
            label='생명주기 범위'
            showPercentage={false}
          />
          <p className='text-sm text-muted-foreground mt-1'>
            Cradle-to-Gate (75% 완료)
          </p>
        </div>

        {/* Data quality */}
        <div>
          <h3 className='font-medium mb-2'>데이터 품질</h3>
          <ul className='space-y-1 text-sm text-muted-foreground'>
            <li>• 시간적 범위: 2024년 기준</li>
            <li>• 기술적 범위: 현재 기술 수준</li>
            <li>• 지리적 범위: 국내 생산 기준</li>
          </ul>
        </div>

        {/* Method table */}
        <div>
          <h3 className='font-medium mb-2'>평가 방법론</h3>
          <DataTable columns={columns} data={methodTable} />
        </div>
      </div>
    </InfoCard>
  );
};

export default LCAAnalysisSection;
