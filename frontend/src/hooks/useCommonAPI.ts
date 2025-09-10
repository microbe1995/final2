import { useState, useCallback } from 'react';
import axiosClient from '@/lib/axiosClient';

/**
 * 공통 API 패턴 훅
 * 단일 책임: 모든 API 훅에서 공통으로 사용하는 패턴 제공
 */
export const useCommonAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 공통 GET 요청 패턴
  const getRequest = useCallback(async <T>(
    url: string,
    params?: any
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.get(url, { params });
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '요청 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('API 요청 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 공통 POST 요청 패턴
  const postRequest = useCallback(async <T>(
    url: string,
    data?: any
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.post(url, data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '요청 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('API 요청 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 공통 PUT 요청 패턴
  const putRequest = useCallback(async <T>(
    url: string,
    data?: any
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.put(url, data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '요청 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('API 요청 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 공통 DELETE 요청 패턴
  const deleteRequest = useCallback(async <T>(
    url: string
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosClient.delete(url);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '요청 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('API 요청 실패:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 에러 초기화
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    getRequest,
    postRequest,
    putRequest,
    deleteRequest,
    clearError
  };
};
