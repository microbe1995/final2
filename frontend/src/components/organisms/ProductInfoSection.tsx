import React from 'react';
import InfoCard from '@/components/molecules/InfoCard';
import ProductInfoGrid from '@/components/molecules/ProductInfoGrid';
import { FileText } from 'lucide-react';

interface ProductInfoSectionProps {
  productInfo: Record<string, string>;
  className?: string;
}

const ProductInfoSection: React.FC<ProductInfoSectionProps> = ({
  productInfo,
  className = '',
}) => {
  return (
    <InfoCard title='철강 제품 정보' icon={FileText} className={className}>
      <ProductInfoGrid data={productInfo} />
    </InfoCard>
  );
};

export default ProductInfoSection;
