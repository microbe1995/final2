'use client';

import { useState, useCallback, ChangeEvent } from 'react';

export interface FormOptions<T> {
  initialValues: T;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
  onSubmit?: (values: T) => void | Promise<void>;
}

export function useForm<T extends Record<string, any>>(options: FormOptions<T>) {
  const [values, setValues] = useState<T>(options.initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setValues(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 에러가 있었다면 실시간으로 제거
    if (errors[name as keyof T]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  }, [errors]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (options.validate) {
      const validationErrors = options.validate(values);
      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        return;
      }
    }

    setIsSubmitting(true);
    try {
      await options.onSubmit?.(values);
    } finally {
      setIsSubmitting(false);
    }
  }, [values, options]);

  const reset = useCallback(() => {
    setValues(options.initialValues);
    setErrors({});
  }, [options.initialValues]);

  const setFieldValue = useCallback((
    field: keyof T,
    value: any
  ) => {
    setValues(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  const setFieldError = useCallback((
    field: keyof T,
    error: string
  ) => {
    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  }, []);

  return {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    reset,
    setFieldValue,
    setFieldError,
  };
}
