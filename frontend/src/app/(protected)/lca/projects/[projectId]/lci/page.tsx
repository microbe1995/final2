'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import { saveLci, getLciData } from '@/lib/actions';
import type { LciItem } from '@/lib/types';

export default function LciPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [lciItems, setLciItems] = useState<LciItem[]>([]);

  const [newItem, setNewItem] = useState<Omit<LciItem, 'id'>>({
    processName: '',
    category: '',
    unit: '',
    value: 0,
    uncertainty: 0,
    dataQuality: '',
    source: '',
    notes: '',
  });

  const handleAddItem = () => {
    if (newItem.processName && newItem.category && newItem.unit) {
      const item: LciItem = {
        ...newItem,
        id: `item-${Date.now()}`,
      };
      setLciItems([...lciItems, item]);
      setNewItem({
        processName: '',
        category: '',
        unit: '',
        value: 0,
        uncertainty: 0,
        dataQuality: '',
        source: '',
        notes: '',
      });
    }
  };

  const handleRemoveItem = (id: string) => {
    setLciItems(lciItems.filter(item => item.id !== id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const result = await saveLci(projectId, lciItems);
      if (result.success) {
        setMessage('LCI 데이터가 성공적으로 저장되었습니다!');
      } else {
        setMessage(`오류: ${result.message}`);
      }
    } catch (error) {
      setMessage(`오류가 발생했습니다: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='min-h-screen p-8'>
      <div className='max-w-6xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8'>생명주기 인벤토리 (LCI)</h1>

        {/* 새 항목 추가 폼 */}
        <div className='bg-card p-6 rounded-lg border mb-8'>
          <h2 className='text-xl font-semibold mb-4'>새 LCI 항목 추가</h2>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
            <div>
              <label className='block text-sm font-medium mb-2'>공정명</label>
              <input
                type='text'
                value={newItem.processName}
                onChange={e =>
                  setNewItem({ ...newItem, processName: e.target.value })
                }
                className='w-full p-2 border rounded-md bg-background'
                placeholder='예: 전기 생산'
                required
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>카테고리</label>
              <select
                value={newItem.category}
                onChange={e =>
                  setNewItem({ ...newItem, category: e.target.value })
                }
                className='w-full p-2 border rounded-md bg-background'
                required
              >
                <option value=''>카테고리 선택</option>
                <option value='energy'>에너지</option>
                <option value='material'>자재</option>
                <option value='transport'>운송</option>
                <option value='waste'>폐기물</option>
                <option value='emission'>배출</option>
              </select>
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>단위</label>
              <input
                type='text'
                value={newItem.unit}
                onChange={e => setNewItem({ ...newItem, unit: e.target.value })}
                className='w-full p-2 border rounded-md bg-background'
                placeholder='예: kWh, kg, km'
                required
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>수치</label>
              <input
                type='number'
                value={newItem.value}
                onChange={e =>
                  setNewItem({ ...newItem, value: parseFloat(e.target.value) })
                }
                className='w-full p-2 border rounded-md bg-background'
                step='0.01'
                required
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>
                불확실성 (%)
              </label>
              <input
                type='number'
                value={newItem.uncertainty}
                onChange={e =>
                  setNewItem({
                    ...newItem,
                    uncertainty: parseFloat(e.target.value),
                  })
                }
                className='w-full p-2 border rounded-md bg-background'
                step='0.1'
                min='0'
                max='100'
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-2'>
                데이터 품질
              </label>
              <select
                value={newItem.dataQuality}
                onChange={e =>
                  setNewItem({ ...newItem, dataQuality: e.target.value })
                }
                className='w-full p-2 border rounded-md bg-background'
              >
                <option value=''>품질 선택</option>
                <option value='high'>높음</option>
                <option value='medium'>보통</option>
                <option value='low'>낮음</option>
              </select>
            </div>
            <div className='md:col-span-2'>
              <label className='block text-sm font-medium mb-2'>출처</label>
              <input
                type='text'
                value={newItem.source}
                onChange={e =>
                  setNewItem({ ...newItem, source: e.target.value })
                }
                className='w-full p-2 border rounded-md bg-background'
                placeholder='데이터 출처를 입력하세요'
              />
            </div>
            <div className='md:col-span-3'>
              <label className='block text-sm font-medium mb-2'>비고</label>
              <textarea
                value={newItem.notes}
                onChange={e =>
                  setNewItem({ ...newItem, notes: e.target.value })
                }
                className='w-full p-2 border rounded-md bg-background h-20'
                placeholder='추가 설명이나 참고사항을 입력하세요'
              />
            </div>
          </div>
          <div className='mt-4'>
            <button
              type='button'
              onClick={handleAddItem}
              className='bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90'
            >
              항목 추가
            </button>
          </div>
        </div>

        {/* LCI 항목 목록 */}
        <div className='bg-card p-6 rounded-lg border mb-8'>
          <h2 className='text-xl font-semibold mb-4'>LCI 항목 목록</h2>
          {lciItems.length === 0 ? (
            <p className='text-muted-foreground'>추가된 LCI 항목이 없습니다.</p>
          ) : (
            <div className='overflow-x-auto'>
              <table className='w-full'>
                <thead>
                  <tr className='border-b'>
                    <th className='text-left p-2'>공정명</th>
                    <th className='text-left p-2'>카테고리</th>
                    <th className='text-left p-2'>수치</th>
                    <th className='text-left p-2'>단위</th>
                    <th className='text-left p-2'>불확실성</th>
                    <th className='text-left p-2'>데이터 품질</th>
                    <th className='text-left p-2'>출처</th>
                    <th className='text-left p-2'>비고</th>
                    <th className='text-left p-2'>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {lciItems.map(item => (
                    <tr key={item.id} className='border-b'>
                      <td className='p-2'>{item.processName}</td>
                      <td className='p-2'>{item.category}</td>
                      <td className='p-2'>{item.value}</td>
                      <td className='p-2'>{item.unit}</td>
                      <td className='p-2'>{item.uncertainty}%</td>
                      <td className='p-2'>{item.dataQuality}</td>
                      <td className='p-2'>{item.source}</td>
                      <td className='p-2'>{item.notes}</td>
                      <td className='p-2'>
                        <button
                          onClick={() => handleRemoveItem(item.id)}
                          className='text-red-600 hover:text-red-800'
                        >
                          삭제
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* 제출 버튼 */}
        <div className='flex justify-end'>
          <button
            onClick={handleSubmit}
            disabled={loading || lciItems.length === 0}
            className='bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50'
          >
            {loading ? '저장 중...' : 'LCI 데이터 저장'}
          </button>
        </div>

        {/* 메시지 표시 */}
        {message && (
          <div
            className={`p-4 rounded-md mt-4 ${
              message.includes('성공')
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {message}
          </div>
        )}
      </div>
    </div>
  );
}
