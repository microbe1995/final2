'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import AddressSearchModal from '@/components/common/AddressSearchModal';



interface CompanyData {
  company_id: string;
  password: string;
  confirm_password: string;
  Installation: string;
  Installation_en: string;
  economic_activity: string;
  economic_activity_en: string;
  representative: string;
  representative_en: string;
  email: string;
  telephone: string;
  street: string;
  street_en: string;
  number: string;
  number_en: string;
  postcode: string;
  city: string;
  city_en: string;
  country: string;
  country_en: string;
  country_code: string;
  unlocode: string;
  sourcelatitude: number | null;
  sourcelongitude: number | null;
}

interface UserData {
  username: string;
  password: string;
  fullName: string;
  companyId: string;
}

interface AddressData {
  roadAddress: string;
  jibunAddress: string;
  buildingNumber: string;
  postalCode: string;
  cityName: string;
}

interface Country {
  id: string;
  korean_name: string;
  country_name: string;
  code: string;
  unlocode?: string;
}



export default function RegisterPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'company' | 'user'>('company');
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
  const [checkingUsername, setCheckingUsername] = useState(false);
  const [checkingCompanyId, setCheckingCompanyId] = useState(false);
  const [checkingCompanyIdAvailability, setCheckingCompanyIdAvailability] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null);
  const [companyIdAvailable, setCompanyIdAvailable] = useState<boolean | null>(null);
  const [companyIdAvailability, setCompanyIdAvailability] = useState<boolean | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState<CompanyData>({
    company_id: '',
    password: '',
    confirm_password: '',
    Installation: '',
    Installation_en: '',
    economic_activity: '',
    economic_activity_en: '',
    representative: '',
    representative_en: '',
    email: '',
    telephone: '',
    street: '',
    street_en: '',
    number: '',
    number_en: '',
    postcode: '',
    city: '',
    city_en: '',
    country: '',
    country_en: '',
    country_code: '',
    unlocode: '',
    sourcelatitude: null,
    sourcelongitude: null,
  });

  const [userFormData, setUserFormData] = useState<UserData>({
    username: '',
    password: '',
    fullName: '',
    companyId: '',
  });

  const handleInputChange = (field: keyof CompanyData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleUserInputChange = (field: keyof UserData, value: string) => {
    setUserFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleAddressSelect = (addressData: AddressData) => {
    setFormData(prev => ({
      ...prev,
      street: addressData.roadAddress || '',
      street_en: addressData.roadAddress || '',
      number: addressData.buildingNumber || '',
      number_en: addressData.buildingNumber || '',
      postcode: addressData.postalCode || '',
      city: addressData.cityName || '',
      city_en: addressData.cityName || '',
      sourcelatitude: null,
      sourcelongitude: null,
    }));
  };

  const checkUsernameAvailability = async (username: string) => {
    if (!username) return;
    
    setCheckingUsername(true);
    try {
      const response = await fetch('/api/v1/auth/check-username', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username }),
      });
      
      const result = await response.json();
      console.log('Username check response:', result); // 디버깅용
      setUsernameAvailable(result.data?.available);
    } catch (error) {
      setUsernameAvailable(null);
    } finally {
      setCheckingUsername(false);
    }
  };

  const checkCompanyIdAvailability = async (companyId: string) => {
    if (!companyId) return;
    
    setCheckingCompanyId(true);
    try {
      const response = await fetch('/api/v1/auth/check-company-id', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: companyId }),
      });
      
      const result = await response.json();
      console.log('Company ID existence check response:', result); // 디버깅용
      setCompanyIdAvailable(result.data?.available);
    } catch (error) {
      setCompanyIdAvailable(null);
    } finally {
      setCheckingCompanyId(false);
    }
  };

  const checkCompanyIdDuplicate = async (companyId: string) => {
    if (!companyId) return;
    
    setCheckingCompanyIdAvailability(true);
    try {
      const response = await fetch('/api/v1/auth/check-company-id-availability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: companyId }),
      });
      
      const result = await response.json();
      console.log('API Response:', result); // 디버깅용
      setCompanyIdAvailability(result.data?.available);
    } catch (error) {
      setCompanyIdAvailability(null);
    } finally {
      setCheckingCompanyIdAvailability(false);
    }
  };



  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (activeTab === 'company') {
      // 기업 회원가입 로직
      setLoading(true);
      setError(null);
      setSuccess(null);

      // 비밀번호 확인
      if (formData.password !== formData.confirm_password) {
        setError('비밀번호가 일치하지 않습니다.');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('/api/v1/auth/register/company', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            company_id: formData.company_id,
            password: formData.password,
            Installation: formData.Installation,
            Installation_en: formData.Installation_en,
            economic_activity: formData.economic_activity,
            economic_activity_en: formData.economic_activity_en,
            representative: formData.representative,
            representative_en: formData.representative_en,
            email: formData.email,
            telephone: formData.telephone,
            street: formData.street,
            street_en: formData.street_en,
            number: formData.number,
            number_en: formData.number_en,
            postcode: formData.postcode,
            city: formData.city,
            city_en: formData.city_en,
            country: formData.country,
            country_en: formData.country_en,
            country_code: formData.country_code,
            unlocode: formData.unlocode,
            sourcelatitude: formData.sourcelatitude,
            sourcelongitude: formData.sourcelongitude,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '회원가입에 실패했습니다.');
        }

        setSuccess('기업 회원가입이 완료되었습니다! 3초 후 로그인 페이지로 이동합니다.');
        
        // 3초 후 로그인 페이지로 이동
        setTimeout(() => {
          router.push('/login');
        }, 3000);
        
        setFormData({
          company_id: '',
          password: '',
          confirm_password: '',
          Installation: '',
          Installation_en: '',
          economic_activity: '',
          economic_activity_en: '',
          representative: '',
          representative_en: '',
          email: '',
          telephone: '',
          street: '',
          street_en: '',
          number: '',
          number_en: '',
          postcode: '',
          city: '',
          city_en: '',
          country: '',
          country_en: '',
          country_code: '',
          unlocode: '',
          sourcelatitude: null,
          sourcelongitude: null,
        });
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        );
      } finally {
        setLoading(false);
      }
    } else {
      // 개인 사용자 회원가입 로직
      setLoading(true);
      setError(null);
      setSuccess(null);



      try {
        const response = await fetch('/api/v1/auth/register/user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: userFormData.username,
            password: userFormData.password,
            full_name: userFormData.fullName,
            company_id: userFormData.companyId,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '회원가입에 실패했습니다.');
        }

        setSuccess('개인 사용자 회원가입이 완료되었습니다! 3초 후 로그인 페이지로 이동합니다.');
        
        // 3초 후 로그인 페이지로 이동
        setTimeout(() => {
          router.push('/login');
        }, 3000);
        
        setUserFormData({
          username: '',
          password: '',
          fullName: '',
          companyId: '',
        });
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        );
      } finally {
        setLoading(false);
      }
    }
  };



  return (
    <div className='min-h-screen bg-ecotrace-background flex items-center justify-center p-4'>
      <div className='w-full max-w-4xl'>
        {/* 탭 네비게이션 */}
        <div className='flex mb-8 bg-white/5 rounded-lg p-1'>
          <button
            onClick={() => setActiveTab('company')}
            className={`flex-1 py-3 px-6 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'company'
                ? 'bg-white/10 text-white'
                : 'text-white/60 hover:text-white/80'
            }`}
          >
            기업 회원가입
          </button>
          <button
            onClick={() => setActiveTab('user')}
            className={`flex-1 py-3 px-6 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'user'
                ? 'bg-primary text-white'
                : 'text-white/60 hover:text-white/80'
            }`}
          >
            개인 사용자 회원가입
          </button>
        </div>

        {/* 회원가입 폼 */}
        <div className='bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10'>
          {activeTab === 'company' ? (
            // 기업 회원가입 폼
            <form onSubmit={handleSubmit} className='space-y-6'>
              <h2 className='text-2xl font-bold text-white text-center mb-6'>
                기업 회원가입
              </h2>
              <p className='text-white/60 text-center mb-8'>
                기업 정보를 입력하여 회원가입을 완료하세요.
              </p>

              {error && (
                <div className='p-4 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg'>
                  {error}
                </div>
              )}

              {success && (
                <div className='p-4 bg-green-500/20 border border-green-500/30 text-green-400 rounded-lg'>
                  {success}
                </div>
              )}

              {/* 계정 정보 */}
              <div className='space-y-4'>
                <h3 className='text-lg font-semibold text-white border-b border-white/20 pb-2'>
                  계정 정보
                </h3>
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      기업 ID *
                    </label>
                    <div className='flex gap-2'>
                      <Input
                        type='text'
                        value={formData.company_id}
                        onChange={e =>
                          handleInputChange('company_id', e.target.value)
                        }
                        className='flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                        placeholder='기업 ID를 입력하세요'
                        required
                      />
                      <Button
                        type='button'
                        onClick={() => checkCompanyIdDuplicate(formData.company_id)}
                        disabled={checkingCompanyIdAvailability || !formData.company_id}
                        className='px-4 py-2 bg-primary text-white rounded hover:bg-primary/80 disabled:opacity-50'
                      >
                        {checkingCompanyIdAvailability ? '확인 중...' : '중복확인'}
                      </Button>
                    </div>
                    {companyIdAvailability !== null && (
                      <div className={`mt-2 text-sm ${companyIdAvailability ? 'text-green-400' : 'text-red-400'}`}>
                        {companyIdAvailability ? '사용 가능한 기업 ID입니다.' : '이미 사용 중인 기업 ID입니다.'}
                      </div>
                    )}
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      비밀번호 *
                    </label>
                    <Input
                      type='password'
                      value={formData.password}
                      onChange={e =>
                        handleInputChange('password', e.target.value)
                      }
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
                      value={formData.confirm_password}
                      onChange={e =>
                        handleInputChange('confirm_password', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='비밀번호를 다시 입력하세요'
                      required
                    />
                  </div>
                </div>
              </div>

              {/* 기업 정보 */}
              <div className='space-y-4'>
                <h3 className='text-lg font-semibold text-white border-b border-white/20 pb-2'>
                  기업 정보
                </h3>
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      사업장명 *
                    </label>
                    <Input
                      type='text'
                      value={formData.Installation}
                      onChange={e =>
                        handleInputChange('Installation', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='사업장명을 입력하세요'
                      required
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      사업장 영문명
                    </label>
                    <Input
                      type='text'
                      value={formData.Installation_en}
                      onChange={e =>
                        handleInputChange('Installation_en', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='사업장 영문명을 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      업종명
                    </label>
                    <Input
                      type='text'
                      value={formData.economic_activity}
                      onChange={e =>
                        handleInputChange('economic_activity', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='업종명을 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      업종명 영문명
                    </label>
                    <Input
                      type='text'
                      value={formData.economic_activity_en}
                      onChange={e =>
                        handleInputChange(
                          'economic_activity_en',
                          e.target.value
                        )
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='업종명 영문명을 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      대표자명
                    </label>
                    <Input
                      type='text'
                      value={formData.representative}
                      onChange={e =>
                        handleInputChange('representative', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='대표자명을 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      영문대표자명
                    </label>
                    <Input
                      type='text'
                      value={formData.representative_en}
                      onChange={e =>
                        handleInputChange('representative_en', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='영문대표자명을 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      이메일
                    </label>
                    <Input
                      type='email'
                      value={formData.email}
                      onChange={e => handleInputChange('email', e.target.value)}
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='이메일을 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      전화번호
                    </label>
                    <Input
                      type='tel'
                      value={formData.telephone}
                      onChange={e =>
                        handleInputChange('telephone', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='전화번호를 입력하세요'
                    />
                  </div>
                </div>
              </div>

              {/* 주소 정보 */}
              <div className='space-y-4'>
                <h3 className='text-lg font-semibold text-white border-b border-white/20 pb-2'>
                  주소 정보
                </h3>

                {/* 주소 검색 버튼 */}
                <div className='mb-4'>
                  <Button
                    type='button'
                    onClick={() => setIsAddressModalOpen(true)}
                    variant='outline'
                    className='border-white/30 text-white hover:bg-white/10 transition-colors'
                  >
                    주소 검색
                  </Button>
                </div>

                <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      도로명
                    </label>
                    <Input
                      type='text'
                      value={formData.street}
                      onChange={e =>
                        handleInputChange('street', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='도로명 (자동 입력)'
                      readOnly
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      건물 번호
                    </label>
                    <Input
                      type='text'
                      value={formData.number}
                      onChange={e =>
                        handleInputChange('number', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='건물 번호를 입력하세요'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      우편번호
                    </label>
                    <Input
                      type='text'
                      value={formData.postcode}
                      onChange={e =>
                        handleInputChange('postcode', e.target.value)
                      }
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='우편번호'
                      readOnly
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      도시명
                    </label>
                    <Input
                      type='text'
                      value={formData.city}
                      onChange={e => handleInputChange('city', e.target.value)}
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='도시명'
                      readOnly
                    />
                  </div>
                </div>

                {/* 국가 정보 */}
                <div className='mt-4 space-y-4'>
                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      국가명
                    </label>
                    <Input
                      type='text'
                      value={formData.country}
                      onChange={e =>
                        handleInputChange('country', e.target.value)
                      }
                      placeholder='국가명을 입력하세요'
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      국가영문명
                    </label>
                    <Input
                      type='text'
                      value={formData.country_en}
                      onChange={e =>
                        handleInputChange('country_en', e.target.value)
                      }
                      placeholder='영문 국가명을 입력하세요'
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    />
                  </div>

                  <div>
                    <label className='block text-sm font-medium text-white mb-2'>
                      UNLOCODE
                    </label>
                    <Input
                      type='text'
                      value={formData.unlocode}
                      onChange={e =>
                        handleInputChange('unlocode', e.target.value)
                      }
                      placeholder='UNLOCODE를 입력하세요 (예: KR, US, JP)'
                      className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    />
                  </div>
                </div>
              </div>

              {/* 제출 버튼 */}
              <div className='flex justify-center pt-4'>
                <Button
                  type='submit'
                  disabled={loading}
                  className='w-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
                >
                  {loading ? '처리 중...' : '기업 회원가입'}
                </Button>
              </div>
            </form>
          ) : (
            // 개인 사용자 회원가입 폼
            <form onSubmit={handleSubmit} className='space-y-6'>
              <h2 className='text-2xl font-bold text-white text-center mb-6'>
                개인 사용자 회원가입
              </h2>
              <p className='text-white/60 text-center mb-8'>
                개인 정보를 입력하여 회원가입을 완료하세요.
              </p>

              {error && (
                <div className='p-4 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg'>
                  {error}
                </div>
              )}

              {success && (
                <div className='p-4 bg-green-500/20 border border-green-500/30 text-green-400 rounded-lg'>
                  {success}
                </div>
              )}

              {/* 계정 정보 */}
              <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                <div>
                  <label className='block text-sm font-medium text-white mb-2'>
                    사용자명 *
                  </label>
                  <div className='flex gap-2'>
                    <Input
                      type='text'
                      value={userFormData.username}
                      onChange={e =>
                        handleUserInputChange('username', e.target.value)
                      }
                      className='flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                      placeholder='사용자명을 입력하세요'
                      required
                    />
                    <Button
                      type='button'
                      onClick={() => checkUsernameAvailability(userFormData.username)}
                      disabled={checkingUsername || !userFormData.username}
                      className='px-4 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
                    >
                      {checkingUsername ? '확인중...' : '중복확인'}
                    </Button>
                  </div>
                  {usernameAvailable !== null && (
                    <p className={`text-sm mt-1 ${usernameAvailable ? 'text-green-400' : 'text-red-400'}`}>
                      {usernameAvailable ? '사용 가능한 사용자명입니다.' : '이미 사용 중인 사용자명입니다.'}
                    </p>
                  )}
                </div>

                <div>
                  <label className='block text-sm font-medium text-white mb-2'>
                    성명 *
                  </label>
                  <Input
                    type='text'
                    value={userFormData.fullName}
                    onChange={e =>
                      handleUserInputChange('fullName', e.target.value)
                    }
                    className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    placeholder='성명을 입력하세요'
                    required
                  />
                </div>
              </div>

              {/* 비밀번호 */}
              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  비밀번호 *
                </label>
                <Input
                  type='password'
                  value={userFormData.password}
                  onChange={e =>
                    handleUserInputChange('password', e.target.value)
                  }
                  className='w-full bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                  placeholder='비밀번호를 입력하세요'
                  required
                />
              </div>



              {/* 기업 정보 */}
              <div>
                <label className='block text-sm font-medium text-white mb-2'>
                  소속 기업 ID *
                </label>
                <div className='flex gap-2'>
                  <Input
                    type='text'
                    value={userFormData.companyId}
                    onChange={e =>
                      handleUserInputChange('companyId', e.target.value)
                    }
                    className='flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/20'
                    placeholder='소속 기업 ID를 입력하세요'
                    required
                  />
                  <Button
                    type='button'
                    onClick={() => checkCompanyIdAvailability(userFormData.companyId)}
                    disabled={checkingCompanyId || !userFormData.companyId}
                    className='px-4 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
                  >
                    {checkingCompanyId ? '확인중...' : '기업확인'}
                  </Button>
                </div>
                {companyIdAvailable !== null && (
                  <p className={`text-sm mt-1 ${companyIdAvailable ? 'text-green-400' : 'text-red-400'}`}>
                    {companyIdAvailable ? '존재하는 기업입니다.' : '존재하지 않는 기업입니다.'}
                  </p>
                )}
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
          )}
        </div>
      </div>

      {/* 주소 검색 모달 */}
      <AddressSearchModal
        isOpen={isAddressModalOpen}
        onClose={() => setIsAddressModalOpen(false)}
        onSelect={handleAddressSelect}
      />

    </div>
  );
}
