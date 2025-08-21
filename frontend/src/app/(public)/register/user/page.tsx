'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface UserRegisterData {
  fullName: string;
  username: string;
  companyId: string;
  password: string;
  confirmPassword: string;
}

export default function UserRegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<UserRegisterData>({
    fullName: '',
    username: '',
    companyId: '',
    password: '',
    confirmPassword: '',
  });

  const handleInputChange = (field: keyof UserRegisterData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert('비밀번호가 일치하지 않습니다.');
      return;
    }
    
    // 개인 사용자 회원가입 로직 구현
    console.log('개인 사용자 회원가입 데이터:', formData);
    
    // 회원가입 성공 후 로그인 페이지로 이동
    router.push('/login');
  };

  return (
    <div className='min-h-screen bg-ecotrace-background flex items-center justify-center p-4'>
      <div className='w-full max-w-md'>
        {/* 헤더 */}
        <div className='text-center mb-8'>
          <h1 className='text-3xl font-bold text-white mb-2'>
            개인 사용자 회원가입
          </h1>
          <p className='text-white/60'>
            기본 정보를 입력하여 회원가입을 완료하세요.
          </p>
        </div>

        {/* 회원가입 폼 */}
        <div className='bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10'>
          <form onSubmit={handleSubmit} className='space-y-6'>
            {/* 사용자 이름 */}
            <div>
              <label className='block text-sm font-medium text-white mb-2'>
                사용자 이름 *
              </label>
              <Input
                type='text'
                value={formData.fullName}
                onChange={e => handleInputChange('fullName', e.target.value)}
                className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                placeholder='실명을 입력하세요'
                required
              />
            </div>

            {/* 아이디 */}
            <div>
              <label className='block text-sm font-medium text-white mb-2'>
                아이디 *
              </label>
              <Input
                type='text'
                value={formData.username}
                onChange={e => handleInputChange('username', e.target.value)}
                className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                placeholder='로그인에 사용할 아이디를 입력하세요'
                required
              />
            </div>

            {/* 기업 아이디 */}
            <div>
              <label className='block text-sm font-medium text-white mb-2'>
                기업 아이디 *
              </label>
              <Input
                type='text'
                value={formData.companyId}
                onChange={e => handleInputChange('companyId', e.target.value)}
                className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                placeholder='소속 기업의 아이디를 입력하세요'
                required
              />
            </div>

            {/* 비밀번호 */}
            <div>
              <label className='block text-sm font-medium text-white mb-2'>
                비밀번호 *
              </label>
              <Input
                type='password'
                value={formData.password}
                onChange={e => handleInputChange('password', e.target.value)}
                className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                placeholder='8자 이상의 비밀번호를 입력하세요'
                required
                minLength={8}
              />
            </div>

            {/* 비밀번호 확인 */}
            <div>
              <label className='block text-sm font-medium text-white mb-2'>
                비밀번호 확인 *
              </label>
              <Input
                type='password'
                value={formData.confirmPassword}
                onChange={e => handleInputChange('confirmPassword', e.target.value)}
                className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                placeholder='비밀번호를 다시 입력하세요'
                required
                minLength={8}
              />
            </div>

            {/* 제출 버튼 */}
            <Button
              type='submit'
              className='w-full bg-primary hover:bg-primary/90 text-white font-medium py-3 px-4 rounded-lg transition-colors'
            >
              회원가입 완료
            </Button>
          </form>

          {/* 로그인 링크 */}
          <div className='mt-6 text-center'>
            <p className='text-white/60'>
              이미 계정이 있으신가요?{' '}
              <button
                onClick={() => router.push('/login')}
                className='text-primary hover:text-primary/80 underline'
              >
                로그인하기
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
