'use client';

import React, { useState } from 'react';
import axios from 'axios';

interface CBAMCalculationRequest {
  product_name: string;
  quantity: number;
  unit: string;
  country_of_origin: string;
  carbon_intensity: number;
  transport_distance: number;
  transport_mode: string;
}

interface CBAMCalculationResponse {
  product_name: string;
  quantity: number;
  unit: string;
  country_of_origin: string;
  carbon_footprint: number;
  cbam_tax_rate: number;
  cbam_tax_amount: number;
  calculation_date: string;
  details: {
    production_emissions: number;
    transport_emissions: number;
    carbon_intensity: number;
    transport_distance: number;
    transport_mode: string;
  };
}

export default function CBAMCalculator() {
  const [formData, setFormData] = useState<CBAMCalculationRequest>({
    product_name: '',
    quantity: 0,
    unit: 'ton',
    country_of_origin: '',
    carbon_intensity: 0,
    transport_distance: 0,
    transport_mode: 'ship'
  });

  const [result, setResult] = useState<CBAMCalculationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' || name === 'carbon_intensity' || name === 'transport_distance' 
        ? parseFloat(value) || 0 
        : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      console.log('🧮 CBAM 계산 요청:', formData);
      
      // 로컬 개발 환경용 API URL (프록시 활용)
      const apiUrl = '/api/v1/cbam/calculate';
      
      console.log('🔧 CBAM API URL:', apiUrl);
      
      const response = await axios.post(apiUrl, formData);
      
      console.log('✅ CBAM 계산 결과:', response.data);
      setResult(response.data);
      
    } catch (err: any) {
      console.error('❌ CBAM 계산 실패:', err);
      setError(err.response?.data?.detail || 'CBAM 계산 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      product_name: '',
      quantity: 0,
      unit: 'ton',
      country_of_origin: '',
      carbon_intensity: 0,
      transport_distance: 0,
      transport_mode: 'ship'
    });
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            🏭 CBAM 계산기
          </h1>
          <p className="text-gray-600 mb-8 text-center">
            Carbon Border Adjustment Mechanism (CBAM) 세금 계산
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 제품명 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  제품명 *
                </label>
                <input
                  type="text"
                  name="product_name"
                  value={formData.product_name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="예: cement, iron_steel, aluminium"
                  required
                />
              </div>

              {/* 수량 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  수량 *
                </label>
                <input
                  type="number"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                  step="0.01"
                  required
                />
              </div>

              {/* 단위 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  단위
                </label>
                <select
                  name="unit"
                  value={formData.unit}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ton">톤 (ton)</option>
                  <option value="kg">킬로그램 (kg)</option>
                  <option value="m3">세제곱미터 (m³)</option>
                </select>
              </div>

              {/* 원산지 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  원산지 *
                </label>
                <input
                  type="text"
                  name="country_of_origin"
                  value={formData.country_of_origin}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="예: China, India, Turkey"
                  required
                />
              </div>

              {/* 탄소 집약도 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  탄소 집약도 (kg CO2/ton) *
                </label>
                <input
                  type="number"
                  name="carbon_intensity"
                  value={formData.carbon_intensity}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                  step="0.01"
                  required
                />
              </div>

              {/* 운송 거리 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  운송 거리 (km)
                </label>
                <input
                  type="number"
                  name="transport_distance"
                  value={formData.transport_distance}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                  step="0.01"
                />
              </div>

              {/* 운송 모드 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  운송 모드
                </label>
                <select
                  name="transport_mode"
                  value={formData.transport_mode}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ship">선박 (Ship)</option>
                  <option value="truck">트럭 (Truck)</option>
                  <option value="train">철도 (Train)</option>
                  <option value="air">항공 (Air)</option>
                </select>
              </div>
            </div>

            {/* 버튼들 */}
            <div className="flex justify-center space-x-4 pt-6">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '계산 중...' : 'CBAM 계산하기'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-3 bg-gray-500 text-white rounded-md hover:bg-gray-600"
              >
                초기화
              </button>
            </div>
          </form>

          {/* 에러 메시지 */}
          {error && (
            <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
              ❌ {error}
            </div>
          )}

          {/* 결과 표시 */}
          {result && (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <h2 className="text-2xl font-bold text-green-800 mb-4">
                🎯 CBAM 계산 결과
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">제품명:</span>
                    <span>{result.product_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">수량:</span>
                    <span>{result.quantity} {result.unit}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">원산지:</span>
                    <span>{result.country_of_origin}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">총 탄소 발자국:</span>
                    <span className="font-bold text-red-600">
                      {result.carbon_footprint.toFixed(2)} kg CO2
                    </span>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">CBAM 세율:</span>
                    <span>€{result.cbam_tax_rate} / ton CO2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">생산 배출량:</span>
                    <span>{result.details.production_emissions.toFixed(2)} kg CO2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">운송 배출량:</span>
                    <span>{result.details.transport_emissions.toFixed(2)} kg CO2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium text-lg">CBAM 세금:</span>
                    <span className="font-bold text-lg text-red-600">
                      €{result.cbam_tax_amount.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-green-200">
                <p className="text-sm text-green-700">
                  계산 일시: {new Date(result.calculation_date).toLocaleString()}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 