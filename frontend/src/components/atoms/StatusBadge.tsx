import React from 'react';

interface StatusBadgeProps {
  status: 'completed' | 'pending' | 'error';
  children: React.ReactNode;
  className?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  children,
  className = '',
}) => {
  const getStatusStyles = () => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusStyles()} ${className}`}
    >
      {status === 'completed' && <span className='mr-1'>✓</span>}
      {status === 'pending' && <span className='mr-1'>⏳</span>}
      {status === 'error' && <span className='mr-1'>✗</span>}
      {children}
    </span>
  );
};

export default StatusBadge;
