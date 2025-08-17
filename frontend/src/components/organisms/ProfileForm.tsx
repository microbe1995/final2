import React, { useState, useEffect } from 'react';
import FormField from '@/molecules/FormField';
import Button from '@/atoms/Button';
import Card from '@/molecules/Card';
import Input from '@/atoms/Input';

// ============================================================================
// 🧩 ProfileForm Organism Component
// ============================================================================

export interface ProfileFormProps {
  user: {
    full_name: string;
    email: string;
  };
  onUpdateProfile: (data: { full_name: string; email: string }) => void;
  onUpdatePassword: (data: { current_password: string; new_password: string; confirm_password: string }) => void;
  isLoading?: boolean;
  error?: string;
  success?: string;
  className?: string;
}

const ProfileForm: React.FC<ProfileFormProps> = ({
  user,
  onUpdateProfile,
  onUpdatePassword,
  isLoading = false,
  error,
  success,
  className
}) => {
  const [profileData, setProfileData] = useState({
    full_name: user.full_name,
    email: user.email
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setProfileData({
      full_name: user.full_name,
      email: user.email
    });
  }, [user]);

  const handleProfileChange = (field: string, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handlePasswordChange = (field: string, value: string) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

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
    }

    if (!passwordData.confirm_password) {
      errors.confirm_password = '새 비밀번호 확인을 입력해주세요';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      errors.confirm_password = '새 비밀번호가 일치하지 않습니다';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateProfile()) {
      onUpdateProfile(profileData);
    }
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validatePassword()) {
      onUpdatePassword(passwordData);
      // Reset password form after successful submission
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    }
  };

  return (
    <div className={`space-y-8 ${className}`}>
      {/* 프로필 정보 수정 */}
      <Card>
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">프로필 정보</h2>
          
          <form onSubmit={handleProfileSubmit} className="space-y-6">
            <FormField label="이름 *">
              <Input
                name="full_name"
                type="text"
                placeholder="이름을 입력하세요"
                value={profileData.full_name}
                onChange={(e) => handleProfileChange('full_name', e.target.value)}
                error={validationErrors.full_name}
                required
              />
            </FormField>

            <FormField label="이메일 *">
              <Input
                name="email"
                type="email"
                placeholder="이메일을 입력하세요"
                value={profileData.email}
                onChange={(e) => handleProfileChange('email', e.target.value)}
                error={validationErrors.email}
                required
              />
            </FormField>

            <Button
              type="submit"
              variant="primary"
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? '업데이트 중...' : '프로필 업데이트'}
            </Button>
          </form>
        </div>
      </Card>

      {/* 비밀번호 변경 */}
      <Card>
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">비밀번호 변경</h2>
          
          <form onSubmit={handlePasswordSubmit} className="space-y-6">
            <FormField label="현재 비밀번호 *">
              <Input
                name="current_password"
                type="password"
                placeholder="현재 비밀번호를 입력하세요"
                value={passwordData.current_password}
                onChange={(e) => handlePasswordChange('current_password', e.target.value)}
                error={validationErrors.current_password}
                required
              />
            </FormField>

            <FormField label="새 비밀번호 *">
              <Input
                name="new_password"
                type="password"
                placeholder="새 비밀번호를 입력하세요 (6자 이상)"
                value={passwordData.new_password}
                onChange={(e) => handlePasswordChange('new_password', e.target.value)}
                error={validationErrors.new_password}
                required
              />
            </FormField>

            <FormField label="새 비밀번호 확인 *">
              <Input
                name="confirm_password"
                type="password"
                placeholder="새 비밀번호를 다시 입력하세요"
                value={passwordData.confirm_password}
                onChange={(e) => handlePasswordChange('confirm_password', e.target.value)}
                error={validationErrors.confirm_password}
                required
              />
            </FormField>

            <Button
              type="submit"
              variant="secondary"
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? '변경 중...' : '비밀번호 변경'}
            </Button>
          </form>
        </div>
      </Card>

      {/* 상태 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-600">{success}</p>
        </div>
      )}
    </div>
  );
};

export default ProfileForm;
