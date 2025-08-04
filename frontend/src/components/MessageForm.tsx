'use client';

import React, { useState, useEffect } from 'react';
import { useMessageStore } from '../store/messageStore';

const MessageForm: React.FC = () => {
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
    await sendMessage();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    if (error) clearError();
  };

  // 응답이 변경될 때마다 5초 후 자동으로 클리어
  useEffect(() => {
    if (response) {
      const timer = setTimeout(() => {
        clearResponse();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [response, clearResponse]);

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        메시지 전송 시스템
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
            메시지 입력
          </label>
          <textarea
            id="message"
            value={message}
            onChange={handleInputChange}
            placeholder="전송할 메시지를 입력하세요..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={4}
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !message.trim()}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? '전송 중...' : '메시지 전송'}
        </button>
      </form>

      {/* 에러 메시지 */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
          <div className="flex justify-between items-center">
            <span>{error}</span>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700 font-bold"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* 성공 응답 */}
      {response && (
        <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-md">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">전송 성공!</h3>
            <button
              onClick={clearResponse}
              className="text-green-500 hover:text-green-700 font-bold"
            >
              ×
            </button>
          </div>
          <pre className="text-sm bg-white p-2 rounded border overflow-x-auto">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}

      {/* 상태 정보 */}
      <div className="mt-6 p-4 bg-gray-50 rounded-md">
        <h3 className="font-semibold text-gray-700 mb-2">시스템 상태</h3>
        <div className="text-sm text-gray-600 space-y-1">
          <p>• 프론트엔드: Next.js + TypeScript + Zustand</p>
          <p>• 백엔드: FastAPI Gateway + MSA</p>
          <p>• 통신: Axios → Next.js API → Gateway → Service</p>
          <p>• 로그: 터미널에서 실시간 확인 가능</p>
        </div>
      </div>
    </div>
  );
};

export default MessageForm; 