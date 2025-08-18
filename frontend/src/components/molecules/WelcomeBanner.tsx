import React from 'react';
import Button from '@/atoms/Button';

// ============================================================================
// 🧩 WelcomeBanner Molecule Component
// ============================================================================

export interface WelcomeBannerProps {
  title: string;
  description: string;
  primaryButtonText: string;
  primaryButtonHref: string;
  secondaryButtonText: string;
  secondaryButtonHref: string;
  className?: string;
}

const WelcomeBanner: React.FC<WelcomeBannerProps> = ({
  title,
  description,
  primaryButtonText,
  primaryButtonHref,
  secondaryButtonText,
  secondaryButtonHref,
  className
}) => {
  return (
    <section className={`relative overflow-hidden ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center">
          <h1 className="text-[28px] md:text-[32px] font-bold text-[#ffffff] mb-6 leading-[1.3] transition-colors duration-200">
            {title}
          </h1>
          
          <p className="text-[16px] md:text-[18px] text-[#cbd5e1] mb-12 max-w-4xl mx-auto leading-[1.5] transition-colors duration-200">
            {description}
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              href={primaryButtonHref}
              variant="primary"
              size="lg"
              className="text-lg px-15 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
            >
              {primaryButtonText}
            </Button>
            
            <Button
              href={secondaryButtonHref}
              variant="secondary"
              size="lg"
              className="text-lg px-15 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
            >
              {secondaryButtonText}
            </Button>
          </div>
        </div>
      </div>
      
      {/* 배경 장식 */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-0 right-1/4 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/3 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>
    </section>
  );
};

export default WelcomeBanner;
