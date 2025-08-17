import React from 'react';
import Card from '@/molecules/Card';

// ============================================================================
// 🧩 FeatureCard Molecule Component
// ============================================================================

export interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  iconBgColor: string;
  iconColor: string;
  className?: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  iconBgColor,
  iconColor,
  className
}) => {
  return (
    <Card className={`group hover:shadow-2xl transition-all duration-300 ${className}`}>
      <div className="text-center">
        <div className={`w-20 h-20 ${iconBgColor} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:bg-opacity-80 transition-colors duration-200`}>
          <div className={iconColor}>
            {icon}
          </div>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-3 transition-colors duration-200">
          {title}
        </h3>
        <p className="text-gray-600 leading-relaxed transition-colors duration-200">
          {description}
        </p>
      </div>
    </Card>
  );
};

export default FeatureCard;
