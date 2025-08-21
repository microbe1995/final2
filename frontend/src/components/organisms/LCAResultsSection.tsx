import React from 'react';
import InfoCard from '@/components/molecules/InfoCard';
import DataTable from '@/components/atoms/DataTable';
import { TrendingUp } from 'lucide-react';

interface LCAResult {
  category: string;
  manufacturing: number;
  total: number;
  unit: string;
  manufacturingShare: number;
  totalShare: number;
}

interface LCAResultsSectionProps {
  results: LCAResult[];
  className?: string;
}

const LCAResultsSection: React.FC<LCAResultsSectionProps> = ({
  results,
  className = '',
}) => {
  const columns = [
    { key: 'category', label: '영향범주' },
    { key: 'preManufacturing', label: '제조전', align: 'right' as const },
    { key: 'manufacturing', label: '제조', align: 'right' as const },
    { key: 'total', label: '전과정', align: 'right' as const },
    { key: 'unit', label: '단위' },
    {
      key: 'manufacturingShare',
      label: '제조 기여율 (%)',
      align: 'right' as const,
    },
    { key: 'totalShare', label: '전체 기여율 (%)', align: 'right' as const },
  ];

  const tableData = results.map(result => ({
    ...result,
    preManufacturing: '-',
    manufacturing: result.manufacturing.toFixed(1),
    total: result.total.toFixed(1),
    manufacturingShare: `${result.manufacturingShare}%`,
    totalShare: `${result.totalShare}%`,
  }));

  return (
    <InfoCard title='철강 LCA 결과' icon={TrendingUp} className={className}>
      <DataTable columns={columns} data={tableData} />
    </InfoCard>
  );
};

export default LCAResultsSection;
