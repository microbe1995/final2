'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import Button from '@/components/atomic/atoms/Button';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className='h-full flex items-center justify-center bg-white/5 rounded-lg border border-white/10'>
          <div className='text-center p-8'>
            <AlertTriangle className='h-16 w-16 text-yellow-500 mx-auto mb-4' />
            <h2 className='text-xl font-semibold text-white mb-2'>
              프로세스 플로우 로드 중 오류가 발생했습니다
            </h2>
            <p className='text-white/60 mb-6 max-w-md'>
              React Flow 컴포넌트를 초기화하는 중 문제가 발생했습니다. 페이지를
              새로고침하거나 다시 시도해보세요.
            </p>

            <div className='space-y-3'>
              <Button
                onClick={this.handleReset}
                className='flex items-center gap-2 mx-auto'
              >
                <RefreshCw className='h-4 w-4' />
                다시 시도
              </Button>

              <button
                onClick={() => window.location.reload()}
                className='px-4 py-2 text-sm text-white/60 hover:text-white transition-colors'
              >
                페이지 새로고침
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className='mt-6 text-left'>
                <summary className='text-sm text-white/40 cursor-pointer hover:text-white/60'>
                  오류 상세 정보 (개발 모드)
                </summary>
                <div className='mt-2 p-3 bg-white/5 rounded text-xs text-white/60 font-mono'>
                  <div className='mb-2'>
                    <strong>Error:</strong> {this.state.error.toString()}
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>Component Stack:</strong>
                      <pre className='mt-1 overflow-auto'>
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
