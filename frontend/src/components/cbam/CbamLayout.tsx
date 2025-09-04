'use client';

import { ReactNode } from 'react';
import CbamSidebar from './CbamSidebar';

interface Props { children: ReactNode }

export default function CbamLayout({ children }: Props) {
  return (
    <div className="flex">
      <div className="hidden lg:block w-64">
        <CbamSidebar embedded />
      </div>
      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}


