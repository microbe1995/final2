import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { label, error, helperText, leftIcon, rightIcon, className, id, ...props },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className='w-full'>
        {label && (
          <label
            htmlFor={inputId}
            className='block text-sm font-medium text-ecotrace-text mb-2'
          >
            {label}
          </label>
        )}

        <div className='relative'>
          {leftIcon && (
            <div className='absolute left-3 top-1/2 transform -translate-y-1/2 text-ecotrace-textSecondary'>
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={cn(
              'w-full px-4 py-3 bg-ecotrace-surface border border-ecotrace-border rounded-lg text-ecotrace-text placeholder-ecotrace-textSecondary transition-colors duration-200',
              'focus:outline-none focus:ring-2 focus:ring-ecotrace-primary focus:border-ecotrace-primary',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              className
            )}
            {...props}
          />

          {rightIcon && (
            <div className='absolute right-3 top-1/2 transform -translate-y-1/2 text-ecotrace-textSecondary'>
              {rightIcon}
            </div>
          )}
        </div>

        {error && <p className='mt-1 text-sm text-red-500'>{error}</p>}

        {helperText && !error && (
          <p className='mt-1 text-sm text-ecotrace-textSecondary'>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
