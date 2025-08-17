import React from 'react';
import Input from '@/atoms/Input';


// ============================================================================
// 🧩 FormField Molecule Component
// ============================================================================

export interface FormFieldProps {
  label: string;
  children?: React.ReactNode;
  className?: string;
  error?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  children,
  className,
  error
}) => {
  return (
    <div className={['w-full', className].filter(Boolean).join(' ')}>
      <label className="block text-[14px] font-medium text-[#ffffff] mb-2 leading-[1.5]">
        {label}
      </label>
      {children}
      {error && (
        <div className="mt-1 text-sm text-red-500">
          {error}
        </div>
      )}
    </div>
  );
};

export default FormField;
