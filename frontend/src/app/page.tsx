import React from 'react';
import WelcomeBanner from '@/molecules/WelcomeBanner';
import FeaturesSection from '@/molecules/FeaturesSection';

// ============================================================================
// 🏠 홈페이지 컴포넌트
// ============================================================================

export default function HomePage() {
  const features = [
    {
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      ),
      title: "간편한 회원가입",
      description: "한글 사용자명을 지원하는 간편한 회원가입으로 빠르게 시작하세요. 실시간 중복 체크로 안전하게 계정을 생성할 수 있습니다.",
      iconBgColor: "bg-blue-100",
      iconColor: "text-blue-600"
    },
    {
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      title: "안전한 인증",
      description: "SHA256 해싱을 통한 안전한 비밀번호 관리로 계정을 보호합니다. 세션 관리와 접근 제어로 보안을 강화했습니다.",
      iconBgColor: "bg-green-100",
      iconColor: "text-green-600"
    },
    {
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
      ),
      title: "데이터 저장",
      description: "PostgreSQL 기반의 안전한 데이터 저장소로 사용자 정보를 보호합니다. 백업과 복구 시스템으로 데이터 안정성을 보장합니다.",
      iconBgColor: "bg-purple-100",
      iconColor: "text-purple-600"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0b0c0f] transition-colors duration-200">
      <WelcomeBanner
        title="Welcome to CBAM Calculator"
        description="사업장의 데이터를 안전하고 편리하게 관리해 제품별 탄소배출량을 계산하세요. 회원가입 후 로그인하여 서비스를 경험해보세요."
        primaryButtonText="Signup"
        primaryButtonHref="/register"
        secondaryButtonText="Login"
        secondaryButtonHref="/login"
      />
      
      <FeaturesSection
        title="주요 기능"
        subtitle="CBAM Calculator가 제공하는 핵심 기능들을 소개합니다"
        features={features}
      />
    </div>
  );
} 