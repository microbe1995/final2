import React from 'react';


// ============================================================================
// 🧩 Input Atom Component
// ============================================================================

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-[14px] font-medium text-white mb-2 leading-[1.5]">
            {label}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="h-5 w-5 text-[#94a3b8]">
                {leftIcon}
              </div>
            </div>
          )}
          
          <input
            id={inputId}
            className={[
              'block w-full rounded-[12px] border border-[#334155] px-3 py-2 text-white placeholder-[#94a3b8]',
              'bg-[#1e293b] focus:bg-[#1e293b]',
              'focus:border-[#60a5fa] focus:outline-none focus:ring-2 focus:ring-[#60a5fa]/20',
              'disabled:bg-[#1e293b] disabled:cursor-not-allowed',
              'transition-colors duration-[160ms]',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-[#f87171] focus:border-[#f87171] focus:ring-[#f87171]/20',
              className
            ].filter(Boolean).join(' ')}
            ref={ref}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <div className="h-5 w-5 text-[#94a3b8]">
                {rightIcon}
              </div>
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1 text-[14px] text-[#f87171] leading-[1.5]">
            {error}
          </p>
        )}
        
        {helperText && !error && (
          <p className="mt-1 text-[14px] text-[#94a3b8] leading-[1.5]">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
