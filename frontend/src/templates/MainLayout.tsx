import React from 'react';
import Navigation from '@/organisms/Navigation';

// ============================================================================
// 🧩 MainLayout Template Component
// ============================================================================

export interface MainLayoutProps {
  children: React.ReactNode;
  showNavigation?: boolean;
  className?: string;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  showNavigation = true,
  className
}) => {
  return (
    <div className="min-h-screen bg-[#0b0c0f] transition-colors duration-200">
      {showNavigation && <Navigation />}
      
      <main className={className}>
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
