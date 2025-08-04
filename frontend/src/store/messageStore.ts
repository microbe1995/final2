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
    set({ message });
  },

  sendMessage: async () => {
    const { message } = get();
    
    if (!message.trim()) {
      set({ error: '메시지를 입력해주세요.' });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const response = await axios.post('/api/gateway/message', {
        message: message
      }, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      set({ 
        response: response.data, 
        isLoading: false,
        message: '' // 성공 시 입력 필드 초기화
      });

      console.log('메시지 전송 성공:', response.data);
    } catch (error: any) {
      console.error('메시지 전송 실패:', error);
      set({ 
        error: error.response?.data?.detail || '메시지 전송에 실패했습니다.',
        isLoading: false 
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },

  clearResponse: () => {
    set({ response: null });
  }
})); 