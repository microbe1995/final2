import React from 'react';
import ReportHeader from '@/components/organisms/ReportHeader';
import ReportSidebar from '@/components/organisms/ReportSidebar';
import ProductInfoSection from '@/components/organisms/ProductInfoSection';
// LCA 섹션 제거됨

interface ReportPageTemplateProps {
  projectId: string;
  productInfo: Record<string, string>;
  // LCA 관련 prop 제거됨
  onGenerateReport: (format: 'pdf' | 'excel' | 'word') => void;
  onDownloadPDF: () => void;
  onDownloadExcel: () => void;
}

const ReportPageTemplate: React.FC<ReportPageTemplateProps> = ({
  projectId,
  productInfo,
  // LCA 관련 prop 제거됨
  onGenerateReport,
  onDownloadPDF,
  onDownloadExcel,
}) => {
  return (
    <div className='min-h-screen'>
      <div className='px-4 sm:px-6 lg:px-8 py-8'>
        <ReportHeader
          projectId={projectId}
          onDownloadPDF={onDownloadPDF}
          onDownloadExcel={onDownloadExcel}
        />

        <div className='flex flex-col lg:flex-row gap-6'>
          {/* Main Content */}
          <div className='flex-1 space-y-6'>
            <ProductInfoSection productInfo={productInfo} />
          </div>

          {/* Right Sidebar */}
          <ReportSidebar onGenerateReport={onGenerateReport} />
        </div>
      </div>
    </div>
  );
};

export default ReportPageTemplate;
