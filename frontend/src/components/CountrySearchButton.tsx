'use client';

import React, { useState } from 'react';
import { MapPin, Search } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import CountrySearchModal from './CountrySearchModal';

interface Country {
  id: string;
  korean_name: string;
  country_name: string;
  code: string;
  unlocode?: string;
}

interface CountrySearchButtonProps {
  onCountrySelect: (country: Country) => void;
  selectedCountry?: Country | null;
  className?: string;
}

export default function CountrySearchButton({
  onCountrySelect,
  selectedCountry,
  className = '',
}: CountrySearchButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleCountrySelect = (country: Country) => {
    onCountrySelect(country);
    setIsModalOpen(false);
  };

  return (
    <>
      <div className={`space-y-3 ${className}`}>
        {selectedCountry ? (
          <div className='bg-primary/10 border border-primary/20 rounded-lg p-4'>
            <div className='flex items-center gap-2 mb-2'>
              <MapPin className='h-4 w-4 text-primary' />
              <span className='font-medium text-primary'>선택된 국가</span>
            </div>
            <div className='space-y-1 text-sm text-white/80'>
              <p>
                <strong>한국어명:</strong> {selectedCountry.korean_name}
              </p>
              <p>
                <strong>영문명:</strong> {selectedCountry.country_name}
              </p>
              <p>
                <strong>국가코드:</strong> {selectedCountry.code}
              </p>
              {selectedCountry.unlocode && (
                <p>
                  <strong>UNLOCODE:</strong> {selectedCountry.unlocode}
                </p>
              )}
            </div>
            <Button
              onClick={handleOpenModal}
              variant='outline'
              className='mt-3 w-full'
            >
              <Search className='mr-2' size={16} />
              국가 변경
            </Button>
          </div>
        ) : (
          <Button
            onClick={handleOpenModal}
            variant='outline'
            className='w-full'
          >
            <MapPin className='mr-2' size={16} />
            국가 검색
          </Button>
        )}
      </div>

      <CountrySearchModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSelect={handleCountrySelect}
      />
    </>
  );
}
