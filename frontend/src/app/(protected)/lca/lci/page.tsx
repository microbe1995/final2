'use client';

import { useState } from 'react';
import { saveLci, getLciData, validateLciData } from '@/lib/actions';
import type { LciItem } from '@/lib/types';
import LcaLayout from '@/components/lca/LcaLayout';

export default function LciPage() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [items, setItems] = useState<LciItem[]>([
    {
      id: '1',
      processName: '',
      category: '',
      unit: '',
      value: 0,
      uncertainty: 0,
      dataQuality: '',
      source: '',
      notes: '',
    },
  ]);

  const handleInputChange = (index: number, field: keyof LciItem, value: string | number) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const addItem = () => {
    setItems([
      ...items,
      {
        id: Date.now().toString(),
        processName: '',
        category: '',
        unit: '',
        value: 0,
        uncertainty: 0,
        dataQuality: '',
        source: '',
        notes: '',
      },
    ]);
  };

  const removeItem = (index: number) => {
    if (items.length > 1) {
      const newItems = items.filter((_, i) => i !== index);
      setItems(newItems);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const result = await saveLci('current-project', items);
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

  const handleValidate = async () => {
    setLoading(true);
    setMessage('');

    try {
      const result = await validateLciData('current-project');
      if (result.success) {
        setMessage('LCI 데이터 검증이 완료되었습니다!');
      } else {
        setMessage(`검증 오류: ${result.message}`);
      }
    } catch (error) {
      setMessage(`검증 중 오류가 발생했습니다: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LcaLayout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">생명주기 인벤토리 (LCI)</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* LCI 항목들 */}
          <div className="bg-card p-6 rounded-lg border">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">LCI 데이터 입력</h2>
              <button
                type="button"
                onClick={addItem}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors"
              >
                항목 추가
              </button>
            </div>

            <div className="space-y-6">
              {items.map((item, index) => (
                <div key={item.id} className="border border-border/30 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">항목 {index + 1}</h3>
                    {items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeItem(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        삭제
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        공정명 *
                      </label>
                      <input
                        type="text"
                        value={item.processName}
                        onChange={(e) => handleInputChange(index, 'processName', e.target.value)}
                        className="w-full p-2 border rounded-md bg-background"
                        placeholder="예: 철광석 채굴"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        카테고리 *
                      </label>
                      <select
                        value={item.category}
                        onChange={(e) => handleInputChange(index, 'category', e.target.value)}
                        className="w-full p-2 border rounded-md bg-background"
                        required
                      >
                        <option value="">카테고리 선택</option>
                        <option value="원료채취">원료채취</option>
                        <option value="제조">제조</option>
                        <option value="운송">운송</option>
                        <option value="사용">사용</option>
                        <option value="폐기">폐기</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        단위 *
                      </label>
                      <input
                        type="text"
                        value={item.unit}
                        onChange={(e) => handleInputChange(index, 'unit', e.target.value)}
                        className="w-full p-2 border rounded-md bg-background"
                        placeholder="예: kg, MJ, m³"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        수치 *
                      </label>
                      <input
                        type="number"
                        value={item.value}
                        onChange={(e) => handleInputChange(index, 'value', parseFloat(e.target.value) || 0)}
                        className="w-full p-2 border rounded-md bg-background"
                        step="0.01"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        불확실성
                      </label>
                      <input
                        type="number"
                        value={item.uncertainty}
                        onChange={(e) => handleInputChange(index, 'uncertainty', parseFloat(e.target.value) || 0)}
                        className="w-full p-2 border rounded-md bg-background"
                        step="0.01"
                        placeholder="표준편차"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        데이터 품질
                      </label>
                      <select
                        value={item.dataQuality}
                        onChange={(e) => handleInputChange(index, 'dataQuality', e.target.value)}
                        className="w-full p-2 border rounded-md bg-background"
                      >
                        <option value="">품질 선택</option>
                        <option value="높음">높음</option>
                        <option value="보통">보통</option>
                        <option value="낮음">낮음</option>
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium mb-2">
                        데이터 출처
                      </label>
                      <input
                        type="text"
                        value={item.source}
                        onChange={(e) => handleInputChange(index, 'source', e.target.value)}
                        className="w-full p-2 border rounded-md bg-background"
                        placeholder="데이터 출처 또는 참고문헌"
                      />
                    </div>

                    <div className="md:col-span-3">
                      <label className="block text-sm font-medium mb-2">
                        비고
                      </label>
                      <textarea
                        value={item.notes}
                        onChange={(e) => handleInputChange(index, 'notes', e.target.value)}
                        className="w-full p-2 border rounded-md bg-background h-20"
                        placeholder="추가 설명이나 특이사항"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 버튼들 */}
          <div className="flex justify-center space-x-4">
            <button
              type="button"
              onClick={handleValidate}
              disabled={loading}
              className="bg-secondary text-secondary-foreground px-6 py-3 rounded-lg hover:bg-secondary/90 disabled:opacity-50 font-medium"
            >
              데이터 검증
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 disabled:opacity-50 font-medium"
            >
              {loading ? '저장 중...' : 'LCI 저장'}
            </button>
          </div>
        </form>

        {/* 메시지 표시 */}
        {message && (
          <div className={`mt-6 p-4 rounded-md ${
            message.includes('성공') || message.includes('완료') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message}
          </div>
        )}
      </div>
    </LcaLayout>
  );
}
