'use client';

import React, { useState } from 'react';
import { useMessageStore } from '@/store/messageStore';

export default function Dashboard() {
  const {
    message,
    isLoading,
    error,
    response,
    setMessage,
    clearError,
    clearResponse
  } = useMessageStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // 메시지 전송 기능은 현재 구현되지 않음
    console.log('📝 입력된 메시지:', message);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    if (error) clearError();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (message.trim() && !isLoading) {
        // 메시지 전송 기능은 현재 구현되지 않음
        console.log('📝 Enter로 입력된 메시지:', message);
      }
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-4">
      {/* 상단 질문 */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-medium text-gray-900">무슨 작업을 하고 계세요?</h1>
        <div className="mt-4 flex justify-center space-x-4">
          <a 
            href="/cbam" 
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            🏭 CBAM 계산기
          </a>
        </div>
      </div>

      {/* 메인 입력 필드 */}
      <div className="w-full max-w-2xl">
        <form onSubmit={handleSubmit} className="relative">
          <div className="bg-white border border-gray-200 rounded-[28px] shadow-sm relative">
            {/* 입력 영역 */}
            <div className="relative p-4">
              <textarea
                value={message}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="무엇이든 물어보세요 (현재는 입력만 가능)"
                className="w-full resize-none bg-transparent border-0 outline-none text-gray-900 placeholder-gray-400 text-base leading-6 min-h-[120px] pr-20"
                rows={4}
                disabled={isLoading}
              />
            </div>

            {/* 우상단 아이콘들 */}
            <div className="absolute top-3 right-3 flex items-center gap-2">
              {/* 전구 아이콘 */}
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6A4.997 4.997 0 0 1 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z" fill="#22c55e"/>
                </svg>
              </div>
              
              {/* G 아이콘 */}
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold text-sm">G</span>
              </div>
            </div>

            {/* 좌하단 요소들 */}
            <div className="absolute bottom-3 left-3 flex items-center gap-3">
              {/* + 버튼 */}
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
                aria-label="파일 추가"
              >
                <span className="text-xl font-bold">+</span>
              </button>
              
              {/* 도구 버튼 */}
              <button
                type="button"
                className="flex items-center gap-1 text-gray-600 hover:text-gray-800 transition-colors"
                aria-label="도구"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
                </svg>
                <span className="text-sm">도구</span>
              </button>
            </div>

            {/* 우하단 아이콘들 */}
            <div className="absolute bottom-3 right-3 flex items-center gap-2">
              {/* 마이크 아이콘 */}
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
                aria-label="음성 입력"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/>
                </svg>
              </button>
              
              {/* 음성 모드 아이콘 (|||) */}
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
                aria-label="음성 모드"
              >
                <div className="flex items-end gap-0.5 h-4">
                  <div className="w-0.5 bg-current h-2"></div>
                  <div className="w-0.5 bg-current h-3"></div>
                  <div className="w-0.5 bg-current h-4"></div>
                </div>
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* 응답/에러 표시 영역 */}
      {response && (
        <div className="mt-6 w-full max-w-2xl p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-medium text-green-800">전송 성공!</h3>
            <button
              onClick={clearResponse}
              className="text-green-600 hover:text-green-800 text-lg font-bold"
            >
              ×
            </button>
          </div>
          <div className="bg-white p-3 rounded border text-sm">
            <pre className="whitespace-pre-wrap text-green-700">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-6 w-full max-w-2xl p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex justify-between items-center">
            <span className="text-red-700">{error}</span>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700 font-bold text-xl"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* 하단 정보 */}
      <div className="mt-8 text-center text-xs text-gray-500">
        <p>💡 입력한 메시지는 터미널에서 실시간으로 확인할 수 있습니다</p>
        <p>🔧 프론트엔드: Next.js + TypeScript + Zustand | 백엔드: FastAPI Gateway + MSA</p>
        <p className="mt-2 text-green-600">✅ 최신 업데이트: {new Date().toLocaleString('ko-KR')}</p>
      </div>
    </div>
  );
}