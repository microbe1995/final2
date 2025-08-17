import React from 'react';


// ============================================================================
// 🧩 Card Molecule Component
// ============================================================================

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  border?: boolean;
  hover?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  padding = 'md',
  shadow = 'md',
  border = true,
  hover = false
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8'
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg'
  };

  return (
    <div
      className={[
        'bg-[#1e293b] text-white rounded-[12px] transition-all duration-[160ms]',
        'border border-[#334155]',
        paddingClasses[padding],
        shadowClasses[shadow],
        hover && 'hover:shadow-[0_4px_12px_rgba(0,0,0,.4)] hover:-translate-y-1',
        className
      ].filter(Boolean).join(' ')}
    >
      {children}
    </div>
  );
};

export default Card;
