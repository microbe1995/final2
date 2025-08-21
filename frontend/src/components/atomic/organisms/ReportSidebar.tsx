import React from 'react';
import ReportGenerationForm from '@/components/atomic/molecules/ReportGenerationForm';
import ReportStatusList from '@/components/atomic/molecules/ReportStatusList';

interface ReportSidebarProps {
  onGenerateReport: (format: 'pdf' | 'excel' | 'word') => void;
  className?: string;
}

const ReportSidebar: React.FC<ReportSidebarProps> = ({
  onGenerateReport,
  className = '',
}) => {
  const statusItems = [
    { label: '프로젝트 개요', status: 'completed' as const },
    { label: '분석 범위', status: 'completed' as const },
    { label: 'LCI 데이터', status: 'completed' as const },
    { label: '영향평가 결과', status: 'completed' as const },
    { label: '해석 및 결론', status: 'completed' as const },
  ];

  return (
    <div
      className={`w-full lg:w-80 sticky top-8 max-h-[calc(100vh-8rem)] overflow-y-auto space-y-6 ${className}`}
    >
      {/* Report Generation */}
      <div className='bg-card border border-border/30 rounded-lg p-6 shadow-sm'>
        <h3 className='text-lg font-medium mb-4'>보고서 생성</h3>
        <ReportGenerationForm onGenerate={onGenerateReport} />
      </div>

      {/* Report Status */}
      <div className='bg-card border border-border/30 rounded-lg p-6 shadow-sm'>
        <h3 className='text-lg font-medium mb-4'>보고서 상태</h3>
        <ReportStatusList items={statusItems} />
      </div>
    </div>
  );
};

export default ReportSidebar;
