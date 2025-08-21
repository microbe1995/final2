'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import AddressSearchModal from '@/components/AddressSearchModal';
import CountrySearchModal from '@/components/CountrySearchModal';

interface UserRegisterData {
  username: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  email: string;
  phone: string;
  companyId: string;
  country: string;
  city: string;
  zipcode: string;
  address: string;
}

export default function UserRegisterPage() {
  const router = useRouter();
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
  const [isCountryModalOpen, setIsCountryModalOpen] = useState(false);
  const [formData, setFormData] = useState<UserRegisterData>({
    username: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    email: '',
    phone: '',
    companyId: '',
    country: '',
    city: '',
    zipcode: '',
    address: '',
  });

  const handleInputChange = (field: keyof UserRegisterData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAddressSelect = (addressData: any) => {
    setFormData(prev => ({
      ...prev,
      address: addressData.roadAddress,
      city: addressData.cityName,
      zipcode: addressData.postalCode,
    }));
  };

  const handleCountrySelect = (countryData: any) => {
    setFormData(prev => ({
      ...prev,
      country: countryData.korean_name,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // 개인 사용자 회원가입 로직 구현
    console.log('개인 사용자 회원가입 데이터:', formData);
  };

  return (
    <div className='min-h-screen bg-ecotrace-background flex items-center justify-center p-4'>
      <div className='w-full max-w-2xl'>
        {/* 헤더 */}
        <div className='text-center mb-8'>
          <h1 className='text-3xl font-bold text-white mb-2'>
            개인 사용자 회원가입
          </h1>
          <p className='text-white/60'>
            개인 정보를 입력하여 회원가입을 완료하세요.
          </p>
        </div>

        {/* 회원가입 폼 */}
        <div className='bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10'>
          <form onSubmit={handleSubmit} className='space-y-6'>
            {/* 계정 정보 */}
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  사용자명 *
                </label>
                <Input
                  type='text'
                  value={formData.username}
                  onChange={e => handleInputChange('username', e.target.value)}
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='사용자명을 입력하세요'
                  required
                />
              </div>

              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  성명 *
                </label>
                <Input
                  type='text'
                  value={formData.fullName}
                  onChange={e => handleInputChange('fullName', e.target.value)}
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='성명을 입력하세요'
                  required
                />
              </div>
            </div>

            {/* 비밀번호 */}
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  비밀번호 *
                </label>
                <Input
                  type='password'
                  value={formData.password}
                  onChange={e => handleInputChange('password', e.target.value)}
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='비밀번호를 입력하세요'
                  required
                />
              </div>

              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  비밀번호 확인 *
                </label>
                <Input
                  type='password'
                  value={formData.password}
                  onChange={e =>
                    handleInputChange('confirmPassword', e.target.value)
                  }
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='비밀번호를 다시 입력하세요'
                  required
                />
              </div>
            </div>

            {/* 연락처 정보 */}
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  이메일 *
                </label>
                <Input
                  type='email'
                  value={formData.email}
                  onChange={e => handleInputChange('email', e.target.value)}
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='이메일을 입력하세요'
                  required
                />
              </div>

              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  연락처 *
                </label>
                <Input
                  type='tel'
                  value={formData.phone}
                  onChange={e => handleInputChange('phone', e.target.value)}
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='010-1234-5678'
                  required
                />
              </div>
            </div>

            {/* 기업 정보 */}
            <div>
              <label className='block text-sm font-medium text-white mb-2'>
                소속 기업 ID *
              </label>
              <Input
                type='text'
                value={formData.companyId}
                onChange={e => handleInputChange('companyId', e.target.value)}
                className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                placeholder='소속 기업 ID를 입력하세요'
                required
              />
            </div>

            {/* 주소 정보 */}
            <div className='space-y-4'>
              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  주소 *
                </label>
                <div className='flex gap-2'>
                  <Input
                    type='text'
                    value={formData.address}
                    onChange={e => handleInputChange('address', e.target.value)}
                    className='flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    placeholder='주소를 입력하세요'
                    readOnly
                  />
                  <Button
                    type='button'
                    onClick={() => setIsAddressModalOpen(true)}
                    className='bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
                  >
                    주소 검색
                  </Button>
                </div>
              </div>

              <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                <div>
                  <label className='block text-sm font-medium text-white mb-2'>
                    도시 *
                  </label>
                  <Input
                    type='text'
                    value={formData.city}
                    onChange={e => handleInputChange('city', e.target.value)}
                    className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    placeholder='도시명'
                    required
                  />
                </div>

                <div>
                  <label className='block text-sm font-medium text-white mb-2'>
                    우편번호 *
                  </label>
                  <Input
                    type='text'
                    value={formData.zipcode}
                    onChange={e => handleInputChange('zipcode', e.target.value)}
                    className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    placeholder='우편번호'
                    required
                  />
                </div>

                <div>
                  <label className='block text-sm font-medium text-white mb-2'>
                    국가 *
                  </label>
                  <div className='flex gap-2'>
                    <Input
                      type='text'
                      value={formData.country}
                      onChange={e =>
                        handleInputChange('country', e.target.value)
                      }
                      className='flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='국가를 선택하세요'
                      readOnly
                    />
                    <Button
                      type='button'
                      onClick={() => setIsCountryModalOpen(true)}
                      className='bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
                    >
                      검색
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* 제출 버튼 */}
            <div className='flex justify-center pt-4'>
              <Button
                type='submit'
                className='w-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
              >
                개인 사용자 회원가입
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* 주소 검색 모달 */}
      <AddressSearchModal
        isOpen={isAddressModalOpen}
        onClose={() => setIsAddressModalOpen(false)}
        onSelect={handleAddressSelect}
      />

      {/* 국가 검색 모달 */}
      <CountrySearchModal
        isOpen={isCountryModalOpen}
        onClose={() => setIsCountryModalOpen(false)}
        onSelect={handleCountrySelect}
      />
    </div>
  );
}
