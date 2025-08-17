import React from 'react';
import FeatureCard from '@/molecules/FeatureCard';

// ============================================================================
// 🧩 FeaturesSection Molecule Component
// ============================================================================

export interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  iconBgColor: string;
  iconColor: string;
}

export interface FeaturesSectionProps {
  title: string;
  subtitle: string;
  features: Feature[];
  className?: string;
}

const FeaturesSection: React.FC<FeaturesSectionProps> = ({
  title,
  subtitle,
  features,
  className
}) => {
  return (
    <section className={`py-24 bg-[#0b0c0f] transition-colors duration-200 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-[22px] font-bold text-[#ffffff] mb-4 transition-colors duration-200 leading-[1.3]">
            {title}
          </h2>
          <p className="text-[16px] text-[#cbd5e1] transition-colors duration-200 leading-[1.5]">
            {subtitle}
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              iconBgColor={feature.iconBgColor}
              iconColor={feature.iconColor}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
