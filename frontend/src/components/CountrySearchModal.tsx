'use client';

import React, { useState, useEffect } from 'react';
import { Search, MapPin, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface Country {
  id: string;
  korean_name: string;
  country_name: string;
  code: string;
  unlocode?: string;
}

interface CountrySearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (country: Country) => void;
}

export default function CountrySearchModal({
  isOpen,
  onClose,
  onSelect,
}: CountrySearchModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [countries, setCountries] = useState<Country[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 검색어가 변경될 때마다 API 호출
  useEffect(() => {
    if (searchQuery.trim().length >= 2) {
      searchCountries(searchQuery);
    } else {
      setCountries([]);
    }
  }, [searchQuery]);

  const searchCountries = async (query: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/countries/search?query=${encodeURIComponent(query)}&limit=20`
      );

      if (!response.ok) {
        throw new Error('국가 검색에 실패했습니다.');
      }

      const data = await response.json();
      setCountries(data.countries || []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      );
      setCountries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCountrySelect = (country: Country) => {
    onSelect(country);
    onClose();
  };

  const handleClose = () => {
    setSearchQuery('');
    setCountries([]);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4'>
      <div className='stitch-card w-full max-w-2xl max-h-[80vh] overflow-hidden'>
        {/* 헤더 */}
        <div className='flex items-center justify-between p-6 border-b border-white/10'>
          <h2 className='stitch-h1 text-xl font-semibold'>국가 검색</h2>
          <Button
            variant='ghost'
            onClick={handleClose}
            className='text-white/60 hover:text-white hover:bg-white/10'
          >
            <X size={20} />
          </Button>
        </div>

        {/* 검색 입력 */}
        <div className='p-6 border-b border-white/10'>
          <div className='relative'>
            <Search
              className='absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40'
              size={18}
            />
            <Input
              type='text'
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder='국가명, 국가코드, UNLOCODE를 입력하세요...'
              className='pl-10 bg-white/5 border-white/20 text-white placeholder:text-white/40 focus:border-primary focus:bg-white/10'
            />
          </div>
          <p className='stitch-caption mt-3 text-white/60'>
            최소 2글자 이상 입력하면 검색이 시작됩니다.
          </p>
        </div>

        {/* 검색 결과 */}
        <div className='flex-1 overflow-y-auto max-h-96'>
          {loading && (
            <div className='p-8 text-center'>
              <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto'></div>
              <p className='stitch-caption mt-3 text-white/60'>검색 중...</p>
            </div>
          )}

          {error && (
            <div className='p-6 text-center'>
              <p className='stitch-error'>{error}</p>
            </div>
          )}

          {!loading &&
            !error &&
            countries.length === 0 &&
            searchQuery.trim().length >= 2 && (
              <div className='p-8 text-center'>
                <MapPin className='h-12 w-12 text-white/20 mx-auto mb-3' />
                <p className='stitch-caption text-white/60'>
                  검색 결과가 없습니다.
                </p>
              </div>
            )}

          {!loading && !error && countries.length > 0 && (
            <div className='divide-y divide-white/10'>
              {countries.map(country => (
                <div
                  key={country.id}
                  onClick={() => handleCountrySelect(country)}
                  className='p-4 hover:bg-white/5 cursor-pointer transition-colors'
                >
                  <div className='flex items-center justify-between'>
                    <div className='flex-1'>
                      <div className='flex items-center gap-2'>
                        <MapPin size={16} className='text-primary' />
                        <span className='font-medium text-white'>
                          {country.korean_name}
                        </span>
                        <span className='stitch-caption text-white/60'>
                          ({country.country_name})
                        </span>
                      </div>
                      <div className='flex items-center gap-4 mt-2 text-sm text-white/60'>
                        <span>코드: {country.code}</span>
                        {country.unlocode && (
                          <span>UNLOCODE: {country.unlocode}</span>
                        )}
                      </div>
                    </div>
                    <div className='text-right'>
                      <span className='inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary/20 text-primary border border-primary/30'>
                        선택
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 푸터 */}
        <div className='p-6 border-t border-white/10 bg-white/5'>
          <div className='flex justify-between items-center text-sm text-white/60'>
            <span>총 {countries.length}개 결과</span>
            <span>Enter 키로 첫 번째 결과 선택</span>
          </div>
        </div>
      </div>
    </div>
  );
}
