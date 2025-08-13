import { create } from 'zustand';
import axios from 'axios';

interface MessageState {
  message: string;
  isLoading: boolean;
  error: string | null;
  response: any | null;
  setMessage: (message: string) => void;
  sendMessage: () => Promise<void>;
  clearError: () => void;
  clearResponse: () => void;
}

export const useMessageStore = create<MessageState>((set, get) => ({
  message: '',
  isLoading: false,
  error: null,
  response: null,

  setMessage: (message: string) => {
    console.log('📝 프론트엔드: 메시지 입력 변경', { message });
    set({ message });
  },

  sendMessage: async () => {
    const { message } = get();
    
    console.log('\n' + '='.repeat(60));
    console.log('🚀 프론트엔드: 메시지 전송 시작');
    console.log('='.repeat(60));
    console.log('📝 전송할 메시지:', message);
    console.log('⏰ 전송 시간:', new Date().toISOString());
    console.log('='.repeat(60) + '\n');
    
    if (!message.trim()) {
      console.error('❌ 프론트엔드: 메시지가 비어있습니다.');
      set({ error: '메시지를 입력해주세요.' });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      console.log('📡 프론트엔드: API 요청 전송 중...');
      
      // API URL 구성 (환경변수 기반)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL 
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1/gateway/message`
        : 'https://gateway-production-22ef.up.railway.app/api/v1/gateway/message';
      
      console.log('🔧 Message API URL:', apiUrl);
      
      const response = await axios.post(apiUrl, {
        message: message
      }, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log('\n' + '='.repeat(60));
      console.log('✅ 프론트엔드: 메시지 전송 성공');
      console.log('='.repeat(60));
      console.log('📤 서버 응답:', response.data);
      console.log('⏰ 응답 시간:', new Date().toISOString());
      console.log('='.repeat(60) + '\n');

      set({ 
        response: response.data, 
        isLoading: false,
        message: '' // 성공 시 입력 필드 초기화
      });

    } catch (error: any) {
      console.error('\n' + '='.repeat(60));
      console.error('❌ 프론트엔드: 메시지 전송 실패');
      console.error('='.repeat(60));
      console.error('🔍 에러 상세:', error);
      console.error('📄 에러 응답:', error.response?.data);
      console.error('⏰ 에러 시간:', new Date().toISOString());
      console.error('='.repeat(60) + '\n');
      
      set({ 
        error: error.response?.data?.detail || '메시지 전송에 실패했습니다.',
        isLoading: false 
      });
    }
  },

  clearError: () => {
    console.log('🧹 프론트엔드: 에러 메시지 초기화');
    set({ error: null });
  },

  clearResponse: () => {
    console.log('🧹 프론트엔드: 응답 메시지 초기화');
    set({ response: null });
  }
})); 