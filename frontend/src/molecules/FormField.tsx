import React from 'react';
import Input from '@/atoms/Input';


// ============================================================================
// 🧩 FormField Molecule Component
// ============================================================================

export interface FormFieldProps {
  label: string;
  children?: React.ReactNode;
  className?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  children,
  className
}) => {
  return (
    <div className={['w-full', className].filter(Boolean).join(' ')}>
      <label className="block text-[14px] font-medium text-[#ffffff] mb-2 leading-[1.5]">
        {label}
      </label>
      {children}
    </div>
  );
};

export default FormField;
