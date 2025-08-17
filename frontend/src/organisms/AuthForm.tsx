import React, { useState } from 'react';
import FormField from '@/molecules/FormField';
import Button from '@/atoms/Button';
import Card from '@/molecules/Card';
import Input from '@/atoms/Input';

// ============================================================================
// 🧩 AuthForm Organism Component
// ============================================================================

export interface AuthFormProps {
  type: 'login' | 'register';
  onSubmit: (data: AuthFormData) => void;
  isLoading?: boolean;
  error?: string;
  className?: string;
}

export interface AuthFormData {
  email: string;
  password: string;
  fullName?: string;
  confirmPassword?: string;
}

const AuthForm: React.FC<AuthFormProps> = ({
  type,
  onSubmit,
  isLoading = false,
  error,
  className
}) => {
  const [formData, setFormData] = useState<AuthFormData>({
    email: '',
    password: '',
    fullName: '',
    confirmPassword: ''
  });

  const [validationErrors, setValidationErrors] = useState<Partial<AuthFormData>>({});

  const handleInputChange = (field: keyof AuthFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Partial<AuthFormData> = {};

    if (!formData.email) {
      errors.email = '이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = '올바른 이메일 형식을 입력해주세요';
    }

    if (!formData.password) {
      errors.password = '비밀번호를 입력해주세요';
    } else if (formData.password.length < 6) {
      errors.password = '비밀번호는 최소 6자 이상이어야 합니다';
    }

    if (type === 'register') {
      if (!formData.fullName) {
        errors.fullName = '이름을 입력해주세요';
      } else if (formData.fullName.length < 2) {
        errors.fullName = '이름은 최소 2자 이상이어야 합니다';
      }

      if (!formData.confirmPassword) {
        errors.confirmPassword = '비밀번호 확인을 입력해주세요';
      } else if (formData.confirmPassword !== formData.password) {
        errors.confirmPassword = '비밀번호가 일치하지 않습니다';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      const submitData: AuthFormData = {
        email: formData.email,
        password: formData.password,
        ...(type === 'register' && {
          fullName: formData.fullName,
          confirmPassword: formData.confirmPassword
        })
      };
      
      onSubmit(submitData);
    }
  };

  return (
    <Card className={className}>
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {type === 'login' ? '로그인' : '회원가입'}
        </h2>
        <p className="text-gray-600 mt-2">
          {type === 'login' 
            ? 'CBAM Calculator 계정으로 로그인하세요'
            : '새로운 계정을 만들어보세요'
          }
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {type === 'register' && (
          <FormField label="이름 *">
            <Input
              name="fullName"
              type="text"
              placeholder="실명을 입력하세요"
              value={formData.fullName || ''}
              onChange={(e) => handleInputChange('fullName', e.target.value)}
              error={validationErrors.fullName}
              required
            />
          </FormField>
        )}

        <FormField label="이메일 *">
          <Input
            name="email"
            type="email"
            placeholder="이메일을 입력하세요"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            error={validationErrors.email}
            required
          />
        </FormField>

        <FormField label="비밀번호 *">
          <Input
            name="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            value={formData.password}
            onChange={(e) => handleInputChange('password', e.target.value)}
            error={validationErrors.password}
            required
          />
        </FormField>

        {type === 'register' && (
          <FormField label="비밀번호 확인 *">
            <Input
              name="confirmPassword"
              type="password"
              placeholder="비밀번호를 다시 입력하세요"
              value={formData.confirmPassword || ''}
              onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
              error={validationErrors.confirmPassword}
              required
            />
          </FormField>
        )}

        {error && (
          <div className="text-red-600 text-sm text-center p-3 bg-red-50 rounded-lg">
            {error}
          </div>
        )}

        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isLoading}
          className="w-full"
        >
          {isLoading 
            ? (type === 'login' ? '로그인 중...' : '회원가입 중...')
            : (type === 'login' ? '로그인' : '회원가입')
          }
        </Button>
      </form>

      <div className="text-center mt-6">
        <p className="text-gray-600">
          {type === 'login' ? '계정이 없으신가요?' : '이미 계정이 있으신가요?'}
          <a
            href={type === 'login' ? '/register' : '/login'}
            className="text-blue-600 hover:text-blue-700 font-medium ml-1"
          >
            {type === 'login' ? 'SignUp' : 'SignIn'}
          </a>
        </p>
      </div>
    </Card>
  );
};

export default AuthForm;
