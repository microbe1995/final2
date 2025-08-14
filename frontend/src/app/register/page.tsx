'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function RegisterPage() {
  const router = useRouter();

  // Form state management
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: ''
  });

  // Form input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Register form submission
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 비밀번호 확인 검증
    if (formData.password !== formData.confirmPassword) {
      alert('❌ 비밀번호가 일치하지 않습니다.');
      return;
    }
    
    // 입력된 데이터를 JSON 형태로 alert에 표시
    const registerData = {
      "회원가입 정보": {
        "사용자명": formData.username,
        "이메일": formData.email,
        "전체 이름": formData.full_name || "미입력",
        "비밀번호": formData.password
      }
    };
    
    // JSON을 보기 좋게 포맷팅하여 alert에 표시
    alert(JSON.stringify(registerData, null, 2));
    
    // 프론트엔드 로그: 입력값들을 JSON 형태로 출력
    console.log('📝 프론트엔드 회원가입 입력값:', JSON.stringify(registerData, null, 2));
    
    try {
      // 환경별 API URL 설정
      let apiUrl: string;
      
      if (process.env.NODE_ENV === 'production') {
        // 프로덕션 환경 (Vercel) - Gateway 프록시 엔드포인트 사용
        apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL + '/auth/register';
      } else {
        // 개발 환경 (로컬) - Gateway 프록시 엔드포인트 사용
        apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL + '/auth/register';
      }
      
      // 환경 변수가 없으면 기본값 사용
      if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
        apiUrl = 'http://localhost:8080/api/v1/auth/register';
      }
      
      console.log(`😂 apiUrl: ${apiUrl}`);
      console.log(`🌍 환경: ${process.env.NODE_ENV}`);
      console.log(`🔗 전체 URL: ${apiUrl}`);
      
      // 전송할 데이터 준비
      const requestData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined
      };
      
      console.log('🚀 Gateway로 전송할 데이터:', requestData);
      
      // 비동기 요청 처리
      const response = await axios.post(apiUrl, requestData);
      console.log('✅ 회원가입 성공:', response.data);
      
      // 성공 메시지 표시
      alert(`🎉 회원가입이 성공적으로 완료되었습니다!\n\n사용자명: ${response.data.user.username}\n이메일: ${response.data.user.email}\n사용자 ID: ${response.data.user.id}`);
      
      // 대시보드로 이동
      router.replace('/dashboard');
      
    } catch (error: any) {
      console.error('❌ 회원가입 실패:', error);
      
      // 에러 응답 처리
      if (error.response && error.response.data) {
        alert(`❌ 회원가입 실패: ${error.response.data.detail || error.response.data.message || '알 수 없는 오류'}`);
      } else if (error.code === 'ERR_NETWORK') {
        alert('❌ Gateway에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
      } else {
        alert('❌ 회원가입에 실패했습니다. 서버 연결을 확인해주세요.');
      }
    }
  };

  // Go back to login page
  const handleBackToLogin = () => {
    router.replace('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Register Title */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              회원가입
            </h1>
            <p className="text-gray-600 mt-2">새 계정을 만들어 서비스를 이용하세요</p>
          </div>

          {/* Register Form */}
          <form onSubmit={handleRegister} className="space-y-6">
            {/* Username Input */}
            <div className="relative">
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="사용자명"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Full Name Input */}
            <div className="relative">
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                placeholder="전체 이름 (선택사항)"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
              />
            </div>

            {/* Email Input */}
            <div className="relative">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="이메일"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Password Input */}
            <div className="relative">
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="비밀번호 (최소 8자)"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Confirm Password Input */}
            <div className="relative">
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="비밀번호 확인"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Buttons */}
            <div className="space-y-4 pt-4">
              {/* Register Button */}
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 rounded-xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
              >
                회원가입
              </button>

              {/* Back to Login Button */}
              <button
                type="button"
                onClick={handleBackToLogin}
                className="w-full bg-white border-2 border-gray-300 text-gray-800 py-3 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium text-lg shadow-sm"
              >
                로그인으로 돌아가기
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 