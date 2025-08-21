import React from 'react';
import ReportHeader from '@/components/organisms/ReportHeader';
import ReportSidebar from '@/components/organisms/ReportSidebar';
import ProductInfoSection from '@/components/organisms/ProductInfoSection';
import LCAAnalysisSection from '@/components/organisms/LCAAnalysisSection';
import LCAResultsSection from '@/components/organisms/LCAResultsSection';

interface ReportPageTemplateProps {
  projectId: string;
  productInfo: Record<string, string>;
  methodTable: Array<{
    method: string;
    category: string;
    indicator: string;
    unit: string;
  }>;
  lcaResults: Array<{
    category: string;
    manufacturing: number;
    total: number;
    unit: string;
    manufacturingShare: number;
    totalShare: number;
  }>;
  onGenerateReport: (format: 'pdf' | 'excel' | 'word') => void;
  onDownloadPDF: () => void;
  onDownloadExcel: () => void;
}

const ReportPageTemplate: React.FC<ReportPageTemplateProps> = ({
  projectId,
  productInfo,
  methodTable,
  lcaResults,
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
            <LCAAnalysisSection methodTable={methodTable} />
            <LCAResultsSection results={lcaResults} />
          </div>

          {/* Right Sidebar */}
          <ReportSidebar onGenerateReport={onGenerateReport} />
        </div>
      </div>
    </div>
  );
};

export default ReportPageTemplate;
