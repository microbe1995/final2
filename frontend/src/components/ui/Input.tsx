import React from 'react';
import clsx from 'clsx';

export function Input({
  className = '',
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={clsx('stitch-input', className)} {...props} />;
}
