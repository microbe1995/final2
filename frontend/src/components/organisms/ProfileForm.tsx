import React, { useState, useEffect } from 'react';
import FormField from '@/molecules/FormField';
import Button from '@/atoms/Button';
import Card from '@/molecules/Card';
import Input from '@/atoms/Input';

// ============================================================================
// 🧩 ProfileForm Organism Component
// ============================================================================

export interface ProfileFormProps {
  // 기본 정보 업데이트용
  user?: {
    full_name: string;
    email: string;
  };
  onUpdateProfile?: (data: { full_name: string; email: string }) => void;
  
  // 비밀번호 변경용
  onUpdatePassword?: (data: { current_password: string; new_password: string; confirm_password: string }) => void;
  
  // 공통 props
  isLoading?: boolean;
  error?: string;
  success?: string;
  className?: string;
  
  // 폼 타입 구분
  isPasswordChange?: boolean;
  
  // 새로운 인터페이스 (Profile 페이지용)
  onSubmit?: (data: any) => void;
}

const ProfileForm: React.FC<ProfileFormProps> = ({
  user,
  onUpdateProfile,
  onUpdatePassword,
  isLoading = false,
  error,
  success,
  className,
  isPasswordChange = false,
  onSubmit
}) => {
  // ============================================================================
  // 🎯 상태 관리 - 단일 책임
  // ============================================================================
  
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || ''
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // ============================================================================
  // 🔄 부수 효과 - 사용자 정보 동기화
  // ============================================================================
  
  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name,
        email: user.email
      });
    }
  }, [user]);

  // ============================================================================
  // 🎯 이벤트 핸들러 - 단일 책임
  // ============================================================================
  
  const handleProfileChange = (field: string, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
    
    // 유효성 검사 에러 클리어
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handlePasswordChange = (field: string, value: string) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
    
    // 유효성 검사 에러 클리어
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // ============================================================================
  // ✅ 유효성 검사 - 단일 책임
  // ============================================================================
  
  const validateProfile = (): boolean => {
    const errors: Record<string, string> = {};

    if (!profileData.full_name) {
      errors.full_name = '이름을 입력해주세요';
    } else if (profileData.full_name.length < 2) {
      errors.full_name = '이름은 최소 2자 이상이어야 합니다';
    }

    if (!profileData.email) {
      errors.email = '이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileData.email)) {
      errors.email = '올바른 이메일 형식을 입력해주세요';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validatePassword = (): boolean => {
    const errors: Record<string, string> = {};

    if (!passwordData.current_password) {
      errors.current_password = '현재 비밀번호를 입력해주세요';
    }

    if (!passwordData.new_password) {
      errors.new_password = '새 비밀번호를 입력해주세요';
    } else if (passwordData.new_password.length < 6) {
      errors.new_password = '새 비밀번호는 최소 6자 이상이어야 합니다';
    } else if (passwordData.new_password === passwordData.current_password) {
      errors.new_password = '새 비밀번호는 현재 비밀번호와 달라야 합니다';
    }

    if (!passwordData.confirm_password) {
      errors.confirm_password = '비밀번호 확인을 입력해주세요';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      errors.confirm_password = '비밀번호가 일치하지 않습니다';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // ============================================================================
  // 🚀 제출 핸들러 - 단일 책임
  // ============================================================================
  
  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateProfile()) return;
    
    if (onSubmit) {
      onSubmit(profileData);
    } else if (onUpdateProfile) {
      onUpdateProfile(profileData);
    }
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePassword()) return;
    
    if (onSubmit) {
      onSubmit(passwordData);
    } else if (onUpdatePassword) {
      onUpdatePassword(passwordData);
    }
  };

  // ============================================================================
  // 🎨 렌더링 - 조건부 렌더링
  // ============================================================================
  
  if (isPasswordChange) {
    return (
      <Card className={className}>
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          <FormField
            label="현재 비밀번호"
            error={validationErrors.current_password}
          >
            <Input
              type="password"
              value={passwordData.current_password}
              onChange={(e) => handlePasswordChange('current_password', e.target.value)}
              placeholder="현재 비밀번호를 입력하세요"
              disabled={isLoading}
            />
          </FormField>

          <FormField
            label="새 비밀번호"
            error={validationErrors.new_password}
          >
            <Input
              type="password"
              value={passwordData.new_password}
              onChange={(e) => handlePasswordChange('new_password', e.target.value)}
              placeholder="새 비밀번호를 입력하세요"
              disabled={isLoading}
            />
          </FormField>

          <FormField
            label="비밀번호 확인"
            error={validationErrors.confirm_password}
          >
            <Input
              type="password"
              value={passwordData.confirm_password}
              onChange={(e) => handlePasswordChange('confirm_password', e.target.value)}
              placeholder="새 비밀번호를 다시 입력하세요"
              disabled={isLoading}
            />
          </FormField>

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? '변경 중...' : '비밀번호 변경'}
          </Button>
        </form>
      </Card>
    );
  }

  // 기본 프로필 폼
  return (
    <Card className={className}>
      <form onSubmit={handleProfileSubmit} className="space-y-4">
        <FormField
          label="이름"
          error={validationErrors.full_name}
        >
          <Input
            type="text"
            value={profileData.full_name}
            onChange={(e) => handleProfileChange('full_name', e.target.value)}
            placeholder="이름을 입력하세요"
            disabled={isLoading}
          />
        </FormField>

        <FormField
          label="이메일"
          error={validationErrors.email}
        >
          <Input
            type="email"
            value={profileData.email}
            onChange={(e) => handleProfileChange('email', e.target.value)}
            placeholder="이메일을 입력하세요"
            disabled={isLoading}
          />
        </FormField>

        <Button
          type="submit"
          variant="primary"
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? '업데이트 중...' : '프로필 업데이트'}
        </Button>
      </form>
    </Card>
  );
};

export default ProfileForm;
