'use client';

import { ReactNode } from 'react';
import CbamSidebar from './CbamSidebar';

interface Props { children: ReactNode }

export default function CbamLayout({ children }: Props) {
  return (
    <main className="px-4 sm:px-6 lg:px-8 py-6">
      {children}
    </main>
  );
}


