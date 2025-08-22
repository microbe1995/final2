'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { X, Save, Trash2 } from 'lucide-react';
import { Node } from '@xyflow/react';

interface ProcessStepData extends Record<string, unknown> {
  name: string;
  type: 'input' | 'process' | 'output';
  description: string;
  parameters: Record<string, any>;
  status: 'active' | 'inactive' | 'error';
}

interface ProcessStepModalProps {
  isOpen: boolean;
  onClose: () => void;
  node: Node<ProcessStepData> | null;
  onSave: (data: ProcessStepData) => void;
}

export default function ProcessStepModal({
  isOpen,
  onClose,
  node,
  onSave,
}: ProcessStepModalProps) {
  const [formData, setFormData] = useState<ProcessStepData>({
    name: '',
    type: 'process',
    description: '',
    parameters: {},
    status: 'active',
  });

  const [newParameterKey, setNewParameterKey] = useState('');
  const [newParameterValue, setNewParameterValue] = useState('');

  useEffect(() => {
    if (node) {
      setFormData(node.data);
    }
  }, [node]);

  const handleInputChange = (field: keyof ProcessStepData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleParameterChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [key]: value,
      },
    }));
  };

  const handleParameterDelete = (key: string) => {
    setFormData(prev => {
      const newParameters = { ...prev.parameters };
      delete newParameters[key];
      return {
        ...prev,
        parameters: newParameters,
      };
    });
  };

  const addParameter = () => {
    if (newParameterKey.trim() && newParameterValue.trim()) {
      handleParameterChange(newParameterKey.trim(), newParameterValue.trim());
      setNewParameterKey('');
      setNewParameterValue('');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleClose = () => {
    setFormData({
      name: '',
      type: 'process',
      description: '',
      parameters: {},
      status: 'active',
    });
    setNewParameterKey('');
    setNewParameterValue('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
      <div className='bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto'>
        {/* 모달 헤더 */}
        <div className='flex items-center justify-between p-6 border-b border-gray-200'>
          <h2 className='text-xl font-semibold text-gray-900'>
            {node ? '프로세스 단계 편집' : '새 프로세스 단계'}
          </h2>
          <button
            onClick={handleClose}
            className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
          >
            <X className='h-5 w-5 text-gray-500' />
          </button>
        </div>

        {/* 모달 본문 */}
        <form onSubmit={handleSubmit} className='p-6 space-y-6'>
          {/* 기본 정보 */}
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <div>
              <label className='block text-sm font-medium text-gray-700 mb-2'>
                단계 이름 *
              </label>
              <input
                type='text'
                value={formData.name}
                onChange={e => handleInputChange('name', e.target.value)}
                className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
                placeholder='단계 이름을 입력하세요'
                required
              />
            </div>

            <div>
              <label className='block text-sm font-medium text-gray-700 mb-2'>
                단계 유형 *
              </label>
              <select
                value={formData.type}
                onChange={e => handleInputChange('type', e.target.value)}
                className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
              >
                <option value='input'>입력 (Input)</option>
                <option value='process'>처리 (Process)</option>
                <option value='output'>출력 (Output)</option>
              </select>
            </div>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              설명
            </label>
            <textarea
              value={formData.description}
              onChange={e => handleInputChange('description', e.target.value)}
              rows={3}
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
              placeholder='단계에 대한 설명을 입력하세요'
            />
          </div>

          {/* 상태 */}
          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              상태
            </label>
            <select
              value={formData.status}
              onChange={e => handleInputChange('status', e.target.value)}
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            >
              <option value='active'>활성 (Active)</option>
              <option value='inactive'>비활성 (Inactive)</option>
              <option value='error'>오류 (Error)</option>
            </select>
          </div>

          {/* 파라미터 관리 */}
          <div className='space-y-4'>
            <div className='flex items-center justify-between'>
              <h3 className='text-lg font-medium text-gray-900'>파라미터</h3>
              <div className='flex gap-2'>
                <input
                  type='text'
                  value={newParameterKey}
                  onChange={e => setNewParameterKey(e.target.value)}
                  placeholder='키'
                  className='px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
                />
                <input
                  type='text'
                  value={newParameterValue}
                  onChange={e => setNewParameterValue(e.target.value)}
                  placeholder='값'
                  className='px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
                />
                <Button
                  type='button'
                  onClick={addParameter}
                  className='px-3 py-1 text-sm bg-green-600 hover:bg-green-700'
                >
                  추가
                </Button>
              </div>
            </div>

            {/* 기존 파라미터 목록 */}
            {Object.keys(formData.parameters).length > 0 ? (
              <div className='space-y-2'>
                {Object.entries(formData.parameters).map(([key, value]) => (
                  <div
                    key={key}
                    className='flex items-center justify-between p-3 bg-gray-50 rounded-lg'
                  >
                    <div className='flex items-center gap-3'>
                      <span className='font-medium text-gray-900'>{key}:</span>
                      <span className='text-gray-600'>{String(value)}</span>
                    </div>
                    <button
                      type='button'
                      onClick={() => handleParameterDelete(key)}
                      className='p-1 hover:bg-red-100 rounded text-red-600'
                    >
                      <Trash2 className='h-4 w-4' />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className='text-gray-500 text-sm text-center py-4'>
                파라미터가 없습니다. 위에서 추가해보세요.
              </p>
            )}
          </div>

          {/* 모달 푸터 */}
          <div className='flex items-center justify-end gap-3 pt-6 border-t border-gray-200'>
            <Button
              type='button'
              variant='outline'
              onClick={handleClose}
              className='flex items-center gap-2'
            >
              취소
            </Button>
            <Button
              type='submit'
              className='flex items-center gap-2 bg-primary hover:bg-primary/90'
            >
              <Save className='h-4 w-4' />
              저장
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
