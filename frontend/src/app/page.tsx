'use client';

import React, { useState } from 'react';
import { useMessageStore } from '../store/messageStore';

export default function Home() {
  const { 
    message, 
    isLoading, 
    error, 
    response, 
    setMessage, 
    sendMessage, 
    clearError, 
    clearResponse 
  } = useMessageStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      await sendMessage();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    if (error) clearError();
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            GreenSteel MSA 시스템
          </h1>
          <p className="text-lg text-gray-600">
            Next.js + FastAPI Gateway + 마이크로서비스 아키텍처
          </p>
        </div>

        {/* 메인 입력 영역 */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 입력 필드 */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                무엇이든 물어보세요
              </label>
              <textarea
                id="message"
                value={message}
                onChange={handleInputChange}
                placeholder="메시지를 입력하세요..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-lg"
                rows={6}
                disabled={isLoading}
              />
            </div>

            {/* 전송 버튼 */}
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={isLoading || !message.trim()}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-medium"
              >
                {isLoading ? '전송 중...' : '전송하기'}
              </button>
            </div>
          </form>

          {/* 에러 메시지 */}
          {error && (
            <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              <div className="flex justify-between items-center">
                <span>{error}</span>
                <button
                  onClick={clearError}
                  className="text-red-500 hover:text-red-700 font-bold text-xl"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* 성공 응답 */}
          {response && (
            <div className="mt-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold text-lg">전송 성공!</h3>
                <button
                  onClick={clearResponse}
                  className="text-green-500 hover:text-green-700 font-bold text-xl"
                >
                  ×
                </button>
              </div>
              <div className="bg-white p-3 rounded border">
                <pre className="text-sm overflow-x-auto">
                  {JSON.stringify(response, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* 시스템 정보 */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>💡 입력한 메시지는 터미널에서 실시간으로 확인할 수 있습니다</p>
          <p>🔧 프론트엔드: Next.js + TypeScript + Zustand | 백엔드: FastAPI Gateway + MSA</p>
        </div>
      </div>
    </main>
  );
} 