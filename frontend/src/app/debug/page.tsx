'use client';

import { useEffect, useState } from 'react';

export default function DebugPage() {
  const [envVars, setEnvVars] = useState<Record<string, unknown>>({});

  useEffect(() => {
    const envStatus = {
      NODE_ENV: process.env.NODE_ENV,
      NEXT_PUBLIC_KAKAO_MAP_API_KEY: process.env.NEXT_PUBLIC_KAKAO_MAP_API_KEY,
      NEXT_PUBLIC_GATEWAY_URL: process.env.NEXT_PUBLIC_GATEWAY_URL,
      NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
    };
    setEnvVars(envStatus);
  }, []);

  return (
    <div className='min-h-screen bg-gray-900 text-white p-8'>
      <div className='max-w-4xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8'>🔍 환경 변수 디버깅 페이지</h1>

        <div className='bg-gray-800 rounded-lg p-6 mb-6'>
          <h2 className='text-xl font-semibold mb-4'>📋 환경 변수 상태</h2>
          <div className='space-y-3'>
            {Object.entries(envVars).map(([key, value]) => (
              <div
                key={key}
                className='flex items-center justify-between p-3 bg-gray-700 rounded'
              >
                <span className='font-mono text-sm'>{key}</span>
                <span className='font-mono text-sm max-w-xs truncate'>
                  {String(value || 'undefined')}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className='bg-blue-900 border border-blue-600 rounded-lg p-4'>
          <h3 className='font-semibold text-blue-300 mb-2'>📚 추가 정보</h3>
          <p className='text-blue-200 mb-3'>
            자세한 설정 방법은 다음 문서를 참조하세요:
          </p>
          <div className='space-y-2 text-sm text-blue-200'>
            <p>
              •{' '}
              <a
                href='/KAKAO_API_SETUP.md'
                className='underline hover:text-blue-100'
              >
                카카오 API 설정 가이드
              </a>
            </p>
            <p>
              •{' '}
              <a
                href='https://developers.kakao.com/'
                target='_blank'
                rel='noopener noreferrer'
                className='underline hover:text-blue-100'
              >
                카카오 개발자 콘솔
              </a>
            </p>
            <p>
              •{' '}
              <a
                href='https://vercel.com/docs/projects/environment-variables'
                target='_blank'
                rel='noopener noreferrer'
                className='underline hover:text-blue-100'
              >
                Vercel 환경 변수 문서
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
