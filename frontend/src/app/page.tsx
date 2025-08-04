'use client';

import MessageForm from '../components/MessageForm';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            GreenSteel MSA 시스템
          </h1>
          <p className="text-lg text-gray-600">
            Next.js + FastAPI Gateway + 마이크로서비스 아키텍처
          </p>
        </div>
        
        <MessageForm />
      </div>
    </main>
  );
} 