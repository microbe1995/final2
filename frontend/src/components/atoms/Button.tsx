import React from 'react';


// ============================================================================
// 🧩 Button Atom Component
// ============================================================================

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'success' | 'warning' | 'info';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
  href?: string;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, children, disabled, href, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      primary: 'bg-[#2563eb] hover:bg-[#1d4ed8] text-white focus:ring-[#2563eb] shadow-[0_1px_2px_rgba(0,0,0,.06)] hover:shadow-[0_4px_12px_rgba(0,0,0,.10)]',
      secondary: 'bg-[#475569] hover:bg-[#374151] text-white focus:ring-[#475569] shadow-[0_1px_2px_rgba(0,0,0,.06)] hover:shadow-[0_4px_12px_rgba(0,0,0,.10)]',
      danger: 'bg-[#dc2626] hover:bg-[#b91c1c] text-white focus:ring-[#dc2626] shadow-[0_1px_2px_rgba(0,0,0,.06)] hover:shadow-[0_4px_12px_rgba(0,0,0,.10)]',
      ghost: 'bg-transparent hover:bg-[#334155] text-[#cbd5e1] hover:text-white border border-[#334155]',
      success: 'bg-[#16a34a] hover:bg-[#15803d] text-white focus:ring-[#16a34a] shadow-[0_1px_2px_rgba(0,0,0,.06)] hover:shadow-[0_4px_12px_rgba(0,0,0,.10)]',
      warning: 'bg-[#d97706] hover:bg-[#b45309] text-white focus:ring-[#d97706] shadow-[0_1px_2px_rgba(0,0,0,.06)] hover:shadow-[0_4px_12px_rgba(0,0,0,.10)]',
      info: 'bg-[#06b6d4] hover:bg-[#0891b2] text-white focus:ring-[#06b6d4] shadow-[0_1px_2px_rgba(0,0,0,.06)] hover:shadow-[0_4px_12px_rgba(0,0,0,.10)]'
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base'
    };
    
    const buttonContent = (
      <>
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {children}
      </>
    );

    if (href) {
      return (
        <a
          href={href}
          className={[
            baseClasses,
            variants[variant],
            sizes[size],
            className
          ].filter(Boolean).join(' ')}
        >
          {buttonContent}
        </a>
      );
    }

    return (
      <button
        className={[
          baseClasses,
          variants[variant],
          sizes[size],
          className
        ].filter(Boolean).join(' ')}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {buttonContent}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
