import React from 'react';
import { LucideIcon } from 'lucide-react';

interface InfoCardProps {
  title: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
}

const InfoCard: React.FC<InfoCardProps> = ({
  title,
  icon: Icon,
  children,
  className = '',
}) => {
  return (
    <div
      className={`bg-card border border-border/30 rounded-lg p-6 shadow-sm ${className}`}
    >
      <h2 className='text-xl font-semibold mb-4 flex items-center'>
        {Icon && <Icon className='h-5 w-5 mr-2' />}
        {title}
      </h2>
      {children}
    </div>
  );
};

export default InfoCard;
