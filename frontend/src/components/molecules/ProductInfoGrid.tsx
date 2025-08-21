import React from 'react';

interface ProductInfoGridProps {
  data: Record<string, string>;
  className?: string;
}

const ProductInfoGrid: React.FC<ProductInfoGridProps> = ({
  data,
  className = '',
}) => {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${className}`}>
      {Object.entries(data).map(([key, value]) => (
        <div
          key={key}
          className='flex justify-between py-2 border-b border-border/20'
        >
          <span className='text-muted-foreground capitalize'>
            {key.replace(/([A-Z])/g, ' $1').trim()}:
          </span>
          <span className='font-medium'>{value}</span>
        </div>
      ))}
    </div>
  );
};

export default ProductInfoGrid;
