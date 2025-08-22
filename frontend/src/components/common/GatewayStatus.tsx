'use client';

import React, { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { env } from '@/lib/env';

interface GatewayStatus {
  status: string;
  gateway: string;
  timestamp: string;
}

interface ServiceStatus {
  [key: string]: {
    status: string;
    url: string;
    response_time: number;
  };
}

interface RoutingInfo {
  gateway_name: string;
  architecture: string;
  domain_routing: Record<string, unknown>;
  supported_methods: string[];
  timeout_settings: Record<string, unknown>;
  ddd_features: Record<string, unknown>;
}

interface ArchitectureInfo {
  gateway: string;
  architecture: string;
  version: string;
  description: string;
  domains: Record<string, unknown>;
  features: Record<string, unknown>;
  layers: Record<string, unknown>;
}

const GatewayStatus: React.FC = () => {
  const [gatewayHealth, setGatewayHealth] = useState<GatewayStatus | null>(
    null
  );
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(
    null
  );
  const [routingInfo, setRoutingInfo] = useState<RoutingInfo | null>(null);
  const [architectureInfo, setArchitectureInfo] =
    useState<ArchitectureInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testGatewayConnection = async () => {
    setLoading(true);
    setError(null);

    try {
      const healthResponse = await axiosClient.get(apiEndpoints.gateway.health);
      setGatewayHealth(healthResponse.data);

      const statusResponse = await axiosClient.get(apiEndpoints.gateway.status);
      setServiceStatus(statusResponse.data);

      const routingResponse = await axiosClient.get(
        apiEndpoints.gateway.routing
      );
      setRoutingInfo(routingResponse.data);

      const architectureResponse = await axiosClient.get(
        apiEndpoints.gateway.architecture
      );
      setArchitectureInfo(architectureResponse.data);
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
          <strong>Gateway URL:</strong> {env.NEXT_PUBLIC_API_BASE_URL}
        </p>
        <p className='text-sm text-gray-600'>
          <strong>환경:</strong> {env.NEXT_PUBLIC_ENV}
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
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
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
              <span className='font-medium'>이름:</span>
              <span className='ml-2 text-gray-700'>
                {gatewayHealth.gateway}
              </span>
            </div>
            <div>
              <span className='font-medium'>시간:</span>
              <span className='ml-2 text-gray-700'>
                {new Date(gatewayHealth.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      )}

      {serviceStatus && (
        <div className='mb-6'>
          <h3 className='text-lg font-semibold mb-4'>서비스 상태</h3>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            {Object.entries(serviceStatus).map(([serviceName, service]) => (
              <div key={serviceName} className='p-4 border rounded-md'>
                <div className='flex items-center justify-between mb-2'>
                  <span className='font-medium capitalize'>{serviceName}</span>
                  <span
                    className={`px-2 py-1 rounded-full text-xs ${
                      service.status === 'healthy'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {service.status}
                  </span>
                </div>
                <p className='text-sm text-gray-600'>URL: {service.url}</p>
                <p className='text-sm text-gray-600'>
                  응답시간: {service.response_time}ms
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {routingInfo && (
        <div className='mb-6'>
          <h3 className='text-lg font-semibold mb-4'>라우팅 정보</h3>
          <div className='bg-gray-50 p-4 rounded-md'>
            <pre className='text-sm text-gray-700 overflow-x-auto'>
              {JSON.stringify(routingInfo, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {architectureInfo && (
        <div className='mb-6'>
          <h3 className='text-lg font-semibold mb-4'>아키텍처 정보</h3>
          <div className='bg-gray-50 p-4 rounded-md'>
            <pre className='text-sm text-gray-700 overflow-x-auto'>
              {JSON.stringify(architectureInfo, null, 2)}
            </pre>
          </div>
        </div>
      )}

      <div className='mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md'>
        <h3 className='text-lg font-semibold text-blue-800 mb-2'>사용법</h3>
        <ul className='text-sm text-blue-700 space-y-1'>
          <li>• Gateway 서비스가 실행 중인지 확인하세요 (포트 8080)</li>
          <li>
            • 환경 변수 NEXT_PUBLIC_API_BASE_URL이 올바르게 설정되었는지
            확인하세요
          </li>
          <li>
            • &ldquo;연결 테스트&rdquo; 버튼을 클릭하여 Gateway 연결을
            확인하세요
          </li>
          <li>• 오류가 발생하면 Gateway 서비스 로그를 확인하세요</li>
        </ul>
      </div>
    </div>
  );
};

export default GatewayStatus;
