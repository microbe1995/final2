import React from 'react';
import Input from '@/atoms/Input';
import { cn } from '@/lib/utils';

// ============================================================================
// 🧩 FormField Molecule Component
// ============================================================================

export interface FormFieldProps {
  label: string;
  name: string;
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  className?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  placeholder,
  value,
  onChange,
  onBlur,
  error,
  helperText,
  required = false,
  disabled = false,
  leftIcon,
  rightIcon,
  className
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleBlur = () => {
    onBlur?.();
  };

  return (
    <div className={cn('w-full', className)}>
      <Input
        label={label}
        name={name}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
        error={error}
        helperText={helperText}
        required={required}
        disabled={disabled}
        leftIcon={leftIcon}
        rightIcon={rightIcon}
      />
    </div>
  );
};

export default FormField;
