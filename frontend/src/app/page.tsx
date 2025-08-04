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

        {/* ChatGPT 스타일 입력 폼 */}
        <form className="w-full" onSubmit={handleSubmit}>
          <div className="bg-white shadow-short flex w-full cursor-text flex-col items-center justify-center overflow-clip bg-clip-padding contain-inline-size rounded-[28px] border border-gray-200">
            <div className="relative flex min-h-14 w-full items-end">
              <div className="relative flex w-full flex-auto flex-col">
                <div className="relative mx-5 flex min-h-14 flex-auto bg-transparent items-start">
                  <div className="text-gray-900 max-h-[25dvh] max-h-52 flex-1 overflow-auto [scrollbar-width:thin] default-browser vertical-scroll-fade-mask">
                    <textarea
                      value={message}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      placeholder="무엇이든 물어보세요"
                      className="w-full resize-none bg-transparent border-0 outline-none text-gray-900 placeholder-gray-500 text-base leading-6 min-h-[56px] py-3"
                      rows={1}
                      disabled={isLoading}
                      style={{
                        minHeight: '24px',
                        maxHeight: '200px'
                      }}
                    />
                  </div>
                </div>
                <div className="justify-content-end relative ms-2 flex w-full flex-auto flex-col">
                  <div className="flex-auto"></div>
                </div>
                <div style={{ height: '48px' }}></div>
              </div>
            </div>

            {/* 하단 액션 버튼들 */}
            <div className="absolute bottom-2.5 flex items-center" style={{ left: 'calc(2.5*var(--spacing))', right: '102px' }}>
              {/* 파일 업로드 버튼 */}
              <div className="relative">
                <div className="flex flex-col">
                  <span className="flex">
                    <button
                      type="button"
                      className="composer-btn p-2 rounded-lg hover:bg-gray-100 transition-colors"
                      aria-label="사진 및 파일 추가"
                    >
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className="icon text-gray-600">
                        <path d="M9.33496 16.5V10.665H3.5C3.13273 10.665 2.83496 10.3673 2.83496 10C2.83496 9.63273 3.13273 9.33496 3.5 9.33496H9.33496V3.5C9.33496 3.13273 9.63273 2.83496 10 2.83496C10.3673 2.83496 10.665 3.13273 10.665 3.5V9.33496H16.5L16.6338 9.34863C16.9369 9.41057 17.165 9.67857 17.165 10C17.165 10.3214 16.9369 10.5894 16.6338 10.6514L16.5 10.665H10.665V16.5C10.665 16.8673 10.3673 17.165 10 17.165C9.63273 17.165 9.33496 16.8673 9.33496 16.5Z"></path>
                      </svg>
                    </button>
                  </span>
                </div>
              </div>

              {/* 도구 버튼 */}
              <button
                type="button"
                className="composer-btn p-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center"
                aria-label="도구 선택하기"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className="icon text-gray-600">
                  <path d="M7.91626 11.0013C9.43597 11.0013 10.7053 12.0729 11.011 13.5013H16.6663L16.801 13.515C17.1038 13.5771 17.3311 13.8453 17.3313 14.1663C17.3313 14.4875 17.1038 14.7555 16.801 14.8177L16.6663 14.8314H11.011C10.7056 16.2601 9.43619 17.3314 7.91626 17.3314C6.39643 17.3312 5.1269 16.2601 4.82153 14.8314H3.33325C2.96598 14.8314 2.66821 14.5336 2.66821 14.1663C2.66839 13.7992 2.96609 13.5013 3.33325 13.5013H4.82153C5.12713 12.0729 6.39665 11.0015 7.91626 11.0013ZM7.91626 12.3314C6.90308 12.3316 6.08148 13.1532 6.0813 14.1663C6.0813 15.1797 6.90297 16.0011 7.91626 16.0013C8.9297 16.0013 9.75122 15.1798 9.75122 14.1663C9.75104 13.153 8.92959 12.3314 7.91626 12.3314ZM12.0833 2.66829C13.6031 2.66829 14.8725 3.73966 15.178 5.16829H16.6663L16.801 5.18196C17.1038 5.24414 17.3313 5.51212 17.3313 5.83333C17.3313 6.15454 17.1038 6.42253 16.801 6.4847L16.6663 6.49837H15.178C14.8725 7.92701 13.6031 8.99837 12.0833 8.99837C10.5634 8.99837 9.29405 7.92701 8.98853 6.49837H3.33325C2.96598 6.49837 2.66821 6.2006 2.66821 5.83333C2.66821 5.46606 2.96598 5.16829 3.33325 5.16829H8.98853C9.29405 3.73966 10.5634 2.66829 12.0833 2.66829ZM12.0833 3.99837C11.0698 3.99837 10.2483 4.81989 10.2483 5.83333C10.2483 6.84677 11.0698 7.66829 12.0833 7.66829C13.0967 7.66829 13.9182 6.84677 13.9182 5.83333C13.9182 4.81989 13.0967 3.99837 12.0833 3.99837Z"></path>
                </svg>
                <span className="ms-1.5 me-0.5 text-gray-600 text-sm">도구</span>
              </button>
            </div>

                         {/* 우측 하단 액션 버튼들 */}
             <div className="absolute end-2.5 bottom-2.5 flex items-center gap-2">
               <div className="ms-auto flex items-center gap-1.5">
                 {/* 음성 입력 버튼 */}
                 <span className="">
                   <button
                     aria-label="음성 입력 버튼"
                     type="button"
                     className="composer-btn p-2 rounded-lg hover:bg-gray-100 transition-colors"
                   >
                     <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className="icon text-gray-600">
                       <path d="M15.7806 10.1963C16.1326 10.3011 16.3336 10.6714 16.2288 11.0234L16.1487 11.2725C15.3429 13.6262 13.2236 15.3697 10.6644 15.6299L10.6653 16.835H12.0833L12.2171 16.8486C12.5202 16.9106 12.7484 17.1786 12.7484 17.5C12.7484 17.8214 12.5202 18.0894 12.2171 18.1514L12.0833 18.165H7.91632C7.5492 18.1649 7.25128 17.8672 7.25128 17.5C7.25128 17.1328 7.5492 16.8351 7.91632 16.835H9.33527L9.33429 15.6299C6.775 15.3697 4.6558 13.6262 3.84992 11.2725L3.76984 11.0234L3.74445 10.8906C3.71751 10.5825 3.91011 10.2879 4.21808 10.1963C4.52615 10.1047 4.84769 10.2466 4.99347 10.5195L5.04523 10.6436L5.10871 10.8418C5.8047 12.8745 7.73211 14.335 9.99933 14.335C12.3396 14.3349 14.3179 12.7789 14.9534 10.6436L15.0052 10.5195C15.151 10.2466 15.4725 10.1046 15.7806 10.1963ZM12.2513 5.41699C12.2513 4.17354 11.2437 3.16521 10.0003 3.16504C8.75675 3.16504 7.74835 4.17343 7.74835 5.41699V9.16699C7.74853 10.4104 8.75685 11.418 10.0003 11.418C11.2436 11.4178 12.2511 10.4103 12.2513 9.16699V5.41699ZM13.5814 9.16699C13.5812 11.1448 11.9781 12.7479 10.0003 12.748C8.02232 12.748 6.41845 11.1449 6.41828 9.16699V5.41699C6.41828 3.43889 8.02221 1.83496 10.0003 1.83496C11.9783 1.83514 13.5814 3.439 13.5814 5.41699V9.16699Z"></path>
                     </svg>
                   </button>
                 </span>

                 {/* 음성 모드 버튼 */}
                 <div className="min-w-9">
                   <span className="">
                     <button
                       data-testid="composer-speech-button"
                       aria-label="음성 모드 시작"
                       className="relative flex h-9 items-center justify-center rounded-full disabled:text-gray-50 disabled:opacity-30 w-9 bg-gray-100 hover:bg-gray-200 transition-colors"
                     >
                       <div className="flex items-center justify-center">
                         <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className="icon text-gray-600">
                           <path d="M7.33496 15.5V4.5C7.33496 4.13275 7.63275 3.83499 8 3.83496C8.36727 3.83496 8.66504 4.13273 8.66504 4.5V15.5C8.66504 15.8673 8.36727 16.165 8 16.165C7.63275 16.165 7.33496 15.8673 7.33496 15.5ZM11.335 13.1309V7.20801C11.335 6.84075 11.6327 6.54298 12 6.54297C12.3673 6.54297 12.665 6.84074 12.665 7.20801V13.1309C12.665 13.4981 12.3672 13.7959 12 13.7959C11.6328 13.7959 11.335 13.4981 11.335 13.1309ZM3.33496 11.3535V8.81543C3.33496 8.44816 3.63273 8.15039 4 8.15039C4.36727 8.15039 4.66504 8.44816 4.66504 8.81543V11.3535C4.66504 11.7208 4.36727 12.0186 4 12.0186C3.63273 12.0186 3.33496 11.7208 3.33496 11.3535ZM15.335 11.3535V8.81543C15.335 8.44816 15.6327 8.15039 16 8.15039C16.3673 8.15039 16.665 8.44816 16.665 8.81543V11.3535C16.665 11.7208 16.3673 12.0186 16 12.0186C15.6327 12.0186 15.335 11.7208 15.335 11.3535Z"></path>
                         </svg>
                       </div>
                     </button>
                   </span>
                 </div>

                 {/* 전송 버튼 */}
                 <button
                   type="submit"
                   disabled={isLoading || !message.trim()}
                   className="flex items-center justify-center w-9 h-9 rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
          </div>
        </form>

        {/* 하단 정보 */}
        <div className="mt-4 text-center text-xs text-gray-500">
          <p>💡 입력한 메시지는 터미널에서 실시간으로 확인할 수 있습니다</p>
          <p>🔧 프론트엔드: Next.js + TypeScript + Zustand | 백엔드: FastAPI Gateway + MSA</p>
        </div>
      </main>
    </div>
  );
} 