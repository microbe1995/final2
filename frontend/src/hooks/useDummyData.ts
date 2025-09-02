import { useState, useEffect } from 'react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

export interface DummyData {
  id: number;
  로트번호: string;
  생산품명: string;
  생산수량: number;
  투입일: string | null;
  종료일: string | null;
  공정: string;
  투입물명: string;
  수량: number;
  단위: string;
  created_at: string;
  updated_at: string;
}

export const useDummyData = () => {
  const [data, setData] = useState<DummyData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDummyData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Railway DB의 dummy 테이블 데이터를 가져오는 API 호출
      // Gateway를 통해 CBAM 서비스의 API를 호출
      const response = await axiosClient.get(apiEndpoints.cbam.dummy.list);
      setData(response.data);
    } catch (err) {
      console.error('Dummy 데이터 조회 실패:', err);
      setError('데이터를 불러오는데 실패했습니다.');
      
      // 임시로 더미 데이터 사용 (API 연동 전까지)
      setData([
        {
          id: 1,
          로트번호: '1',
          생산품명: '코크스',
          생산수량: 95.00,
          투입일: '2025-08-01',
          종료일: '2025-08-05',
          공정: '코크스 생산',
          투입물명: '원료',
          수량: 110.00,
          단위: 'ton',
          created_at: '2025-09-02T01:13:07.456417',
          updated_at: '2025-09-02T01:13:07.456417'
        },
        {
          id: 2,
          로트번호: '2',
          생산품명: '소결광',
          생산수량: 120.00,
          투입일: '2025-08-03',
          종료일: '2025-08-04',
          공정: '소결',
          투입물명: '원료',
          수량: 230.00,
          단위: 'ton',
          created_at: '2025-09-02T01:13:07.456417',
          updated_at: '2025-09-02T01:13:07.456417'
        },
        {
          id: 3,
          로트번호: '2',
          생산품명: '소결광',
          생산수량: 120.00,
          투입일: '2025-08-03',
          종료일: '2025-08-04',
          공정: '소결',
          투입물명: '원료',
          수량: 60.00,
          단위: 'ton',
          created_at: '2025-09-02T01:13:07.456417',
          updated_at: '2025-09-02T01:13:07.456417'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    fetchDummyData();
  };

  useEffect(() => {
    fetchDummyData();
  }, []);

  return {
    data,
    loading,
    error,
    refreshData
  };
};
