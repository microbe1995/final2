import React from 'react';

interface SectionTitleProps {
  children: React.ReactNode;
}

const SectionTitle: React.FC<SectionTitleProps> = ({ children }) => {
  return (
    <div className='flex items-center gap-3 mt-6 mb-3'>
      <h3 className='text-[var(--text-1)] font-medium'>{children}</h3>
      <div className='flex-1 h-px bg-[rgba(255,255,255,.08)]' />
    </div>
  );
};

export default SectionTitle;
