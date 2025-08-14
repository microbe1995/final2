import { create } from 'zustand';

interface MessageState {
  message: string;
  isLoading: boolean;
  error: string | null;
  response: any | null;
}

interface MessageStore extends MessageState {
  setMessage: (message: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setResponse: (response: any) => void;
  clearError: () => void;
  clearResponse: () => void;
  clearMessage: () => void;
}

export const useMessageStore = create<MessageStore>((set) => ({
  message: '',
  isLoading: false,
  error: null,
  response: null,

  setMessage: (message: string) => {
    console.log('📝 프론트엔드: 메시지 입력 변경', { message });
    set({ message });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  setResponse: (response: any) => {
    set({ response });
  },

  clearError: () => {
    console.log('🧹 프론트엔드: 에러 메시지 초기화');
    set({ error: null });
  },

  clearResponse: () => {
    console.log('🧹 프론트엔드: 응답 메시지 초기화');
    set({ response: null });
  },

  clearMessage: () => {
    set({ message: '' });
  }
})); 