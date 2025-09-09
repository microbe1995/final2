import React from 'react';

interface ProgressBarProps {
  progress: number; // 0-100
  label?: string;
  showPercentage?: boolean;
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  label,
  showPercentage = true,
  className = '',
}) => {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <div className='flex justify-between items-center'>
          <span className='text-sm font-medium'>{label}</span>
          {showPercentage && (
            <span className='text-sm text-muted-foreground'>
              {clampedProgress}%
            </span>
          )}
        </div>
      )}
      <div className='w-full bg-muted rounded-full h-2'>
        <div
          className='bg-primary h-2 rounded-full transition-all duration-300 ease-in-out'
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
