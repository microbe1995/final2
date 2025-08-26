import React from 'react';
import Button from '@/components/atomic/atoms/Button';
import { Download } from 'lucide-react';

interface ReportHeaderProps {
  projectId: string;
  onDownloadPDF: () => void;
  onDownloadExcel: () => void;
  className?: string;
}

const ReportHeader: React.FC<ReportHeaderProps> = ({
  projectId,
  onDownloadPDF,
  onDownloadExcel,
  className = '',
}) => {
  return (
    <div className={`mb-8 ${className}`}>
      <div className='flex items-start justify-between'>
        <div>
          <h1 className='text-3xl font-bold text-foreground'>LCA 보고서</h1>
          <p className='text-muted-foreground'>프로젝트 ID: {projectId}</p>
        </div>

        {/* Top right actions */}
        <div className='flex gap-2'>
          <Button
            onClick={onDownloadPDF}
            variant='outline'
            className='px-3 py-2 text-sm'
          >
            <Download className='h-4 w-4 mr-2' />
            PDF 다운로드
          </Button>
          <Button
            onClick={onDownloadExcel}
            variant='outline'
            className='px-3 py-2 text-sm'
          >
            <Download className='h-4 w-4 mr-2' />
            Excel 다운로드
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ReportHeader;
