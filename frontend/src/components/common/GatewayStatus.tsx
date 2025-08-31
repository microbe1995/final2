'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

interface GatewayHealth {
  status: string;
  service: string;
  version: string;
  environment: string;
  services: {
    auth: string;
    cbam: string;
  };
}

const GatewayStatus: React.FC = () => {
  const [gatewayHealth, setGatewayHealth] = useState<GatewayHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testGatewayConnection = async () => {
    setLoading(true);
    setError(null);

    try {
      const healthResponse = await axiosClient.get(apiEndpoints.gateway.health);
      setGatewayHealth(healthResponse.data);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : 'Gateway 연결 실패';
      setError(errorMessage);
      // eslint-disable-next-line no-console
      console.error('Gateway 연결 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testGatewayConnection();
  }, []);

  return (
    <div className='p-6 bg-white rounded-lg shadow-md'>
      <div className='flex items-center justify-between mb-6'>
        <h2 className='text-2xl font-bold text-gray-900'>Gateway 상태</h2>
        <button
          onClick={testGatewayConnection}
          disabled={loading}
          className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50'
        >
          {loading ? '테스트 중...' : '연결 테스트'}
        </button>
      </div>

      <div className='mb-6 p-4 bg-gray-50 rounded-md'>
        <h3 className='text-lg font-semibold mb-2'>연결 정보</h3>
        <p className='text-sm text-gray-600'>
          <strong>Gateway URL:</strong> {process.env.NEXT_PUBLIC_API_BASE_URL || 'https://gateway-production-22ef.up.railway.app'}
        </p>
        <p className='text-sm text-gray-600'>
          <strong>환경:</strong> {process.env.NEXT_PUBLIC_ENV || 'production'}
        </p>
      </div>

      {error && (
        <div className='mb-6 p-4 bg-red-50 border border-red-200 rounded-md'>
          <h3 className='text-lg font-semibold text-red-800 mb-2'>연결 오류</h3>
          <p className='text-red-700'>{error}</p>
        </div>
      )}

      {gatewayHealth && (
        <div className='mb-6 p-4 bg-green-50 border border-green-200 rounded-md'>
          <h3 className='text-lg font-semibold text-green-800 mb-2'>
            Gateway 상태
          </h3>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <div>
              <span className='font-medium'>상태:</span>
              <span
                className={`ml-2 px-2 py-1 rounded-full text-xs ${
                  gatewayHealth.status === 'healthy'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {gatewayHealth.status}
              </span>
            </div>
            <div>
              <span className='font-medium'>서비스:</span>
              <span className='ml-2 text-gray-700'>
                {gatewayHealth.service}
              </span>
            </div>
            <div>
              <span className='font-medium'>버전:</span>
              <span className='ml-2 text-gray-700'>
                {gatewayHealth.version}
              </span>
            </div>
            <div>
              <span className='font-medium'>환경:</span>
              <span className='ml-2 text-gray-700'>
                {gatewayHealth.environment}
              </span>
            </div>
          </div>
        </div>
      )}

      {gatewayHealth && (
        <div className='mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md'>
          <h3 className='text-lg font-semibold text-blue-800 mb-2'>
            연결된 서비스
          </h3>
          <div className='space-y-2'>
            <div className='flex justify-between items-center'>
              <span className='font-medium'>Auth Service:</span>
              <span className='text-sm text-gray-600'>
                {gatewayHealth.services.auth ? '연결됨' : '연결 안됨'}
              </span>
            </div>
            <div className='flex justify-between items-center'>
              <span className='font-medium'>CBAM Service:</span>
              <span className='text-sm text-gray-600'>
                {gatewayHealth.services.cbam ? '연결됨' : '연결 안됨'}
              </span>
            </div>
          </div>
        </div>
      )}

      <div className='p-4 bg-gray-50 rounded-md'>
        <h3 className='text-lg font-semibold mb-2'>사용법</h3>
        <p className='text-sm text-gray-600 mb-2'>
          Gateway는 모든 API 요청을 적절한 마이크로서비스로 라우팅합니다.
        </p>
        <p className='text-sm text-gray-600'>
          <strong>예시:</strong> /api/v1/cbam/install → CBAM Service
        </p>
      </div>
    </div>
  );
};

export default GatewayStatus;
