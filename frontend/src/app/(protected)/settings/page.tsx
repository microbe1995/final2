'use client';

import React, { useState } from 'react';
import CommonShell from '@/components/common/CommonShell';
import TabGroup from '@/components/atomic/molecules/TabGroup';
import Input from '@/components/atomic/atoms/Input';
import Button from '@/components/atomic/atoms/Button';
import { cn } from '@/lib/utils';

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('organization');

  const tabs = [
    {
      id: 'organization',
      label: '조직 프로필',
      content: (
        <div className='space-y-6'>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            <Input
              label='조직 이름 (한국어)'
              placeholder='조직명을 입력하세요'
            />
            <Input
              label='조직 이름 (영어)'
              placeholder='Organization name in English'
            />
          </div>

          <Input
            label='허용된 도메인'
            placeholder='example.com'
            helperText='이메일 도메인을 입력하면 해당 도메인의 사용자만 초대할 수 있습니다'
          />

          <div className='space-y-4'>
            <h3 className='text-lg font-semibold text-ecotrace-text'>
              초대 링크
            </h3>
            <div className='flex gap-3'>
              <Input
                placeholder='초대 링크가 생성됩니다'
                readOnly
                className='flex-1'
              />
              <Button variant='outline' size='lg'>
                링크 복사
              </Button>
            </div>
            <Button variant='secondary' size='lg'>
              이메일로 초대하기
            </Button>
          </div>
        </div>
      ),
    },
    {
      id: 'rbac',
      label: 'RBAC',
      content: (
        <div className='space-y-6'>
          <div className='bg-ecotrace-surface border border-ecotrace-border rounded-lg'>
            <div className='bg-ecotrace-background p-4 border-b border-ecotrace-border'>
              <div className='grid grid-cols-2 gap-4'>
                <span className='font-medium text-ecotrace-text'>역할</span>
                <span className='font-medium text-ecotrace-text'>
                  전체 권한
                </span>
              </div>
            </div>
            <div className='divide-y divide-ecotrace-border'>
              {[
                { role: '소유자', permissions: 'true' },
                { role: '관리자', permissions: 'true' },
                { role: '편집자', permissions: 'true' },
                { role: '뷰어', permissions: 'false' },
              ].map((item, index) => (
                <div key={index} className='grid grid-cols-2 gap-4 p-4'>
                  <span className='text-ecotrace-text'>{item.role}</span>
                  <span
                    className={cn(
                      'text-center',
                      item.permissions === 'true'
                        ? 'text-black'
                        : 'text-ecotrace-text'
                    )}
                  >
                    {item.permissions}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <p className='text-sm text-ecotrace-textSecondary'>
            소유자 역할은 기업 계정에만 적용됩니다.
          </p>
        </div>
      ),
    },
    {
      id: 'users',
      label: '사용자',
      content: (
        <div className='space-y-6'>
          <div className='bg-ecotrace-surface border border-ecotrace-border rounded-lg'>
            <div className='bg-ecotrace-background p-4 border-b border-ecotrace-border'>
              <div className='grid grid-cols-7 gap-4 text-sm'>
                <span className='font-medium text-ecotrace-text'>이름</span>
                <span className='font-medium text-ecotrace-text col-span-2'>
                  이메일
                </span>
                <span className='font-medium text-ecotrace-text'>역할</span>
                <span className='font-medium text-ecotrace-text'>상태</span>
                <span className='font-medium text-ecotrace-text'>2FA</span>
                <span className='font-medium text-ecotrace-text'>작업</span>
              </div>
            </div>
            <div className='divide-y divide-ecotrace-border'>
              {[
                {
                  name: '김민지',
                  email: 'minji.kim@ecotrace.com',
                  role: '관리자',
                  status: '활성',
                  twoFA: '활성화',
                  lastActivity: '2024-07-26',
                },
                {
                  name: '박준호',
                  email: 'junho.park@ecotrace.com',
                  role: '편집자',
                  status: '활성',
                  twoFA: '비활성화',
                  lastActivity: '2024-07-25',
                },
                {
                  name: '최지우',
                  email: 'jiwoo.choi@ecotrace.com',
                  role: '뷰어',
                  status: '비활성',
                  twoFA: '비활성화',
                  lastActivity: '2024-07-24',
                },
              ].map((user, index) => (
                <div key={index} className='grid grid-cols-7 gap-4 p-4'>
                  <span className='text-ecotrace-text'>{user.name}</span>
                  <span className='text-ecotrace-textSecondary col-span-2'>
                    {user.email}
                  </span>
                  <div className='flex justify-center'>
                    <span className='px-3 py-1 bg-ecotrace-secondary text-white text-sm rounded-lg'>
                      {user.role}
                    </span>
                  </div>
                  <div className='flex justify-center'>
                    <span
                      className={cn(
                        'px-3 py-1 text-sm rounded-lg',
                        user.status === '활성'
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-red-500/20 text-red-400'
                      )}
                    >
                      {user.status}
                    </span>
                  </div>
                  <span className='text-ecotrace-textSecondary text-center'>
                    {user.twoFA}
                  </span>
                  <span className='text-ecotrace-textSecondary text-center'>
                    {user.lastActivity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'data-governance',
      label: '데이터 거버넌스',
      content: (
        <div className='space-y-6'>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            <Input
              label='데이터 내보내기 권한'
              placeholder='권한 설정'
              readOnly
            />
            <Input
              label='데이터 보존 기간'
              placeholder='보존 기간 설정'
              readOnly
            />
          </div>

          <Button variant='secondary' size='lg'>
            감사 로그 다운로드
          </Button>
        </div>
      ),
    },
  ];

  return (
    <CommonShell>
      <div className='space-y-6'>
        {/* 헤더 */}
        <div className='flex flex-col gap-3'>
          <h1 className='text-3xl font-bold text-ecotrace-text'>설정</h1>
          <p className='text-ecotrace-textSecondary'>
            계정 설정 및 환경 설정을 관리하세요
          </p>
        </div>

        {/* 탭 네비게이션 */}
        <TabGroup
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          variant='underline'
        />

        {/* 탭 컨텐츠 */}
        <div className='mt-6'>
          {tabs.find(tab => tab.id === activeTab)?.content}
        </div>
      </div>
    </CommonShell>
  );
};

export default SettingsPage;
