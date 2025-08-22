import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { FileText } from 'lucide-react';

interface ReportGenerationFormProps {
  onGenerate: (format: 'pdf' | 'excel' | 'word') => void;
  className?: string;
}

const ReportGenerationForm: React.FC<ReportGenerationFormProps> = ({
  onGenerate,
  className = '',
}) => {
  const [selectedFormat, setSelectedFormat] = useState<
    'pdf' | 'excel' | 'word'
  >('pdf');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate(selectedFormat);
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className}`}>
      <div>
        <label className='block text-sm font-medium mb-2'>출력 형식</label>
        <div className='space-y-2'>
          {(['pdf', 'excel', 'word'] as const).map(format => (
            <label
              key={format}
              className='flex items-center gap-2 cursor-pointer'
            >
              <input
                type='radio'
                name='format'
                value={format}
                checked={selectedFormat === format}
                onChange={e =>
                  setSelectedFormat(e.target.value as 'pdf' | 'excel' | 'word')
                }
                className='text-primary focus:ring-primary'
              />
              <span className='text-sm capitalize'>{format.toUpperCase()}</span>
            </label>
          ))}
        </div>
      </div>

      <Button type='submit' className='w-full'>
        <FileText className='h-4 w-4 mr-2' />
        보고서 생성
      </Button>
    </form>
  );
};

export default ReportGenerationForm;
