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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (message.trim() && !isLoading) {
        sendMessage();
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 헤더 */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-semibold text-gray-900">GreenSteel MSA 시스템</h1>
          <p className="text-sm text-gray-600">Next.js + FastAPI Gateway + 마이크로서비스 아키텍처</p>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4">
        {/* 채팅 영역 */}
        <div className="flex-1 mb-4">
          {response && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
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
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
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
        </div>

        {/* 입력 폼 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative flex min-h-14 w-full items-end">
              <div className="relative flex w-full flex-auto flex-col">
                <div className="relative mx-4 flex min-h-14 flex-auto bg-transparent items-start py-3">
                  <div className="w-full max-h-[25dvh] max-h-52 flex-1 overflow-auto">
                    <textarea
                      value={message}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      placeholder="무엇이든 물어보세요"
                      className="w-full resize-none bg-transparent border-0 outline-none text-gray-900 placeholder-gray-500 text-base leading-6"
                      rows={1}
                      disabled={isLoading}
                      style={{
                        minHeight: '24px',
                        maxHeight: '200px'
                      }}
                    />
                  </div>
                </div>
              </div>
              
              {/* 전송 버튼 */}
              <div className="flex items-end p-3">
                <button
                  type="submit"
                  disabled={isLoading || !message.trim()}
                  className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  aria-label="전송하기"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* 하단 정보 */}
        <div className="mt-4 text-center text-xs text-gray-500">
          <p>💡 입력한 메시지는 터미널에서 실시간으로 확인할 수 있습니다</p>
          <p>🔧 프론트엔드: Next.js + TypeScript + Zustand | 백엔드: FastAPI Gateway + MSA</p>
        </div>
      </main>
    </div>
  );
} 