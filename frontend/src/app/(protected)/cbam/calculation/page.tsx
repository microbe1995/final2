'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import Input from '@/components/atomic/atoms/Input';
// StatusBadge has different props, so we'll use simple spans
import { useCalculationAPI } from '@/hooks/useCalculationAPI';
import axiosClient from '@/lib/axiosClient';
import type {
  FuelCalculationRequest,
  MaterialCalculationRequest,
  PrecursorData,
  PrecursorCalculationRequest,
  ElectricityCalculationRequest,
  ProductionProcess,
  CBAMCalculationRequest,
  FuelCalculationResponse,
  MaterialCalculationResponse,
  PrecursorCalculationResponse,
  ElectricityCalculationResponse,
  CBAMCalculationResponse,
  CalculationStatsResponse
} from '@/hooks/useCalculationAPI';

// ============================================================================
// 🧮 CBAM 계산 페이지
// ============================================================================

export default function CalculationPage() {
  const [activeTab, setActiveTab] = useState<'fuel' | 'material' | 'precursor' | 'electricity' | 'process' | 'cbam' | 'stats' | 'boundary' | 'product' | 'operation' | 'node' | 'edge' | 'emission'>('fuel');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  // API Hooks
  const {
    calculateFuelEmission,
    calculateMaterialEmission,
    calculatePrecursorEmission,
    calculateElectricityEmission,
    calculateProcessEmissions,
    getPrecursorList,
    savePrecursorBatch,
    calculateCBAM,
    getCalculationStats,
    getCalculationHistory
  } = useCalculationAPI();

  // Form States
  const [fuelForm, setFuelForm] = useState<FuelCalculationRequest>({
    fuel_name: '',
    fuel_amount: 0
  });

  const [materialForm, setMaterialForm] = useState<MaterialCalculationRequest>({
    material_name: '',
    material_amount: 0
  });

  const [precursorForm, setPrecursorForm] = useState<PrecursorData>({
    user_id: '',
    precursor_name: '',
    emission_factor: 0,
    carbon_content: 0
  });

  const [cbamForm, setCbamForm] = useState<CBAMCalculationRequest>({
    product_name: '',
    product_type: '단순',
    user_id: '',
    production_period: { start: '', end: '' },
    cn_code: '',
    production_quantity: 0,
    processes: [],
    fuels: [],
    materials: [],
    electricity: null,
    precursors: [],
    fuel_emissions: 0,
    material_emissions: 0,
    precursor_emissions: 0
  });

  const [electricityForm, setElectricityForm] = useState<ElectricityCalculationRequest>({
    power_usage: 0,
    emission_factor: 0.4567
  });

  const [processForm, setProcessForm] = useState<ProductionProcess>({
    process_order: 1,
    process_name: '',
    start_date: '',
    end_date: '',
    duration_days: 0,
    input_material_name: '',
    input_material_amount: 0,
    input_fuel_name: '',
    input_fuel_amount: 0,
    power_usage: 0,
    direct_emission: 0,
    indirect_emission: 0,
    precursor_emission: 0,
    total_emission: 0
  });

  // 새로운 테이블 폼 상태들
  const [boundaryForm, setBoundaryForm] = useState({
    name: '',
    boundary_type: 'individual',
    description: '',
    company_id: 1
  });

  const [productForm, setProductForm] = useState({
    name: '',
    cn_code: '',
    period_start: '',
    period_end: '',
    production_qty: 0,
    sales_qty: 0,
    export_qty: 0,
    inventory_qty: 0,
    defect_rate: 0
  });

  const [operationForm, setOperationForm] = useState({
    name: '',
    facility_id: 1,
    category: '',
    boundary_id: 1,
    input_kind: 'material',
    material_id: null,
    fuel_id: null,
    quantity: 0,
    unit_id: 1
  });

  const [nodeForm, setNodeForm] = useState({
    boundary_id: 1,
    node_type: 'product',
    ref_id: 1,
    label: '',
    pos_x: 0,
    pos_y: 0
  });

  const [edgeForm, setEdgeForm] = useState({
    boundary_id: 1,
    sourcenode_id: '',
    targetnode_id: '',
    flow_type: 'material',
    label: ''
  });

  const [emissionForm, setEmissionForm] = useState({
    product_id: 1,
    boundary_id: 1,
    result_unit_id: 1,
    dir_emission: 0,
    indir_emission: 0,
    see: 0
  });

  // Results
  const [results, setResults] = useState<{
    fuel?: FuelCalculationResponse;
    material?: MaterialCalculationResponse;
    precursor?: PrecursorCalculationResponse;
    electricity?: ElectricityCalculationResponse;
    process?: ProductionProcess[];
    cbam?: CBAMCalculationResponse;
    stats?: CalculationStatsResponse;
    boundary?: any;
    product?: any;
    operation?: any;
    node?: any;
    edge?: any;
    emission?: any;
  }>({});

  const [precursorList, setPrecursorList] = useState<PrecursorData[]>([]);

  // ============================================================================
  // 🔥 연료 계산
  // ============================================================================
  
  const handleFuelCalculation = async () => {
    if (!fuelForm.fuel_name || fuelForm.fuel_amount <= 0) {
      setToast({ message: '연료명과 연료량을 올바르게 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateFuelEmission(fuelForm);
      
      if (result) {
        setResults(prev => ({ ...prev, fuel: result }));
        setToast({ message: '연료 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '연료 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Fuel calculation error:', error);
      setToast({ message: '연료 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🧱 원료 계산
  // ============================================================================
  
  const handleMaterialCalculation = async () => {
    if (!materialForm.material_name || materialForm.material_amount <= 0) {
      setToast({ message: '원료명과 원료량을 올바르게 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateMaterialEmission(materialForm);
      
      if (result) {
        setResults(prev => ({ ...prev, material: result }));
        setToast({ message: '원료 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '원료 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Material calculation error:', error);
      setToast({ message: '원료 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🎯 CBAM 종합 계산
  // ============================================================================
  
  const handleCBAMCalculation = async () => {
    if (!cbamForm.product_name) {
      setToast({ message: '제품명을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateCBAM(cbamForm);
      
      if (result) {
        setResults(prev => ({ ...prev, cbam: result }));
        setToast({ message: 'CBAM 종합 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: 'CBAM 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('CBAM calculation error:', error);
      setToast({ message: 'CBAM 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🔬 전구물질 계산
  // ============================================================================
  
  const handlePrecursorCalculation = async () => {
    if (!precursorForm.precursor_name || precursorForm.emission_factor <= 0) {
      setToast({ message: '전구물질명과 배출계수를 올바르게 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculatePrecursorEmission({
        precursor_name: precursorForm.precursor_name,
        precursor_amount: precursorForm.emission_factor, // 임시로 배출계수를 사용량으로 사용
        emission_factor: precursorForm.emission_factor,
        carbon_content: precursorForm.carbon_content
      });
      
      if (result) {
        setResults(prev => ({ ...prev, precursor: result }));
        setToast({ message: '전구물질 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '전구물질 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Precursor calculation error:', error);
      setToast({ message: '전구물질 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // ⚡ 전력 사용 배출량 계산
  // ============================================================================
  
  const handleElectricityCalculation = async () => {
    if (electricityForm.power_usage <= 0) {
      setToast({ message: '전력 사용량을 올바르게 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateElectricityEmission(electricityForm);
      
      if (result) {
        setResults(prev => ({ ...prev, electricity: result }));
        setToast({ message: '전력 사용 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '전력 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Electricity calculation error:', error);
      setToast({ message: '전력 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🏭 생산 공정 계산
  // ============================================================================
  
  const handleProcessCalculation = async () => {
    if (!processForm.process_name || !processForm.start_date || !processForm.end_date) {
      setToast({ message: '공정명과 시작/종료일을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await calculateProcessEmissions([processForm]);
      
      if (result) {
        setResults(prev => ({ ...prev, process: result }));
        setToast({ message: '생산 공정 배출량 계산이 완료되었습니다!', type: 'success' });
      } else {
        setToast({ message: '공정 계산 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Process calculation error:', error);
      setToast({ message: '공정 계산 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🔬 전구물질 관리
  // ============================================================================
  
  const handlePrecursorSave = async () => {
    if (!precursorForm.user_id || !precursorForm.precursor_name) {
      setToast({ message: '사용자 ID와 전구물질명을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await savePrecursorBatch([precursorForm]);
      
      if (result) {
        setToast({ message: `전구물질이 저장되었습니다: ${result.message}`, type: 'success' });
        // 폼 초기화
        setPrecursorForm({
          user_id: precursorForm.user_id, // 사용자 ID는 유지
          precursor_name: '',
          emission_factor: 0,
          carbon_content: 0
        });
      } else {
        setToast({ message: '전구물질 저장 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Precursor save error:', error);
      setToast({ message: '전구물질 저장 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handlePrecursorLoad = async () => {
    if (!precursorForm.user_id) {
      setToast({ message: '사용자 ID를 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const result = await getPrecursorList(precursorForm.user_id);
      
      if (result) {
        setPrecursorList(result.precursors);
        setToast({ message: `${result.total_count}개의 전구물질을 조회했습니다.`, type: 'success' });
      } else {
        setToast({ message: '전구물질 조회 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Precursor load error:', error);
      setToast({ message: '전구물질 조회 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 📊 통계 로드
  // ============================================================================
  
  const loadStats = async () => {
    try {
      const result = await getCalculationStats();
      if (result) {
        setResults(prev => ({ ...prev, stats: result }));
      }
    } catch (error) {
      console.error('Stats load error:', error);
    }
  };

  // 컴포넌트 마운트 시 통계 로드
  useEffect(() => {
    if (activeTab === 'stats') {
      loadStats();
    }
  }, [activeTab]);

  // ============================================================================
  // 🗄️ 새로운 테이블 핸들러들
  // ============================================================================

  const handleBoundaryCreate = async () => {
    if (!boundaryForm.name || !boundaryForm.boundary_type) {
      setToast({ message: '경계명과 경계 유형을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/api/v1/boundary/calc/boundary', boundaryForm);
      
      if (response.status === 200 || response.status === 201) {
        const result = response.data;
        setResults(prev => ({ ...prev, boundary: result }));
        setToast({ message: '경계가 성공적으로 생성되었습니다!', type: 'success' });
        setBoundaryForm({
          name: '',
          boundary_type: 'individual',
          description: '',
          company_id: 1
        }); // 폼 초기화
      } else {
        setToast({ message: '경계 생성 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Boundary creation error:', error);
      setToast({ message: '경계 생성 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleProductCreate = async () => {
    if (!productForm.name || !productForm.period_start || !productForm.period_end) {
      setToast({ message: '제품명과 기간을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      console.log('제품 생성 요청:', productForm);
      
      const response = await axiosClient.post('/api/v1/boundary/product', productForm);
      
      console.log('제품 생성 응답 상태:', response.status);
      
      if (response.status === 200 || response.status === 201) {
        const result = response.data;
        console.log('제품 생성 성공:', result);
        setResults(prev => ({ ...prev, product: result }));
        setToast({ message: '제품이 성공적으로 생성되었습니다!', type: 'success' });
        setProductForm({
          name: '',
          cn_code: '',
          period_start: '',
          period_end: '',
          production_qty: 0,
          sales_qty: 0,
          export_qty: 0,
          inventory_qty: 0,
          defect_rate: 0
        }); // 폼 초기화
      } else {
        console.error('제품 생성 실패:', response.status, response.data);
        setToast({ message: `제품 생성 중 오류가 발생했습니다. (${response.status})`, type: 'error' });
      }
    } catch (error) {
      console.error('Product creation error:', error);
      setToast({ message: '제품 생성 중 네트워크 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleOperationCreate = async () => {
    if (!operationForm.name || !operationForm.input_kind) {
      setToast({ message: '공정명과 입력 종류를 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/api/v1/boundary/calc/operation', operationForm);
      
      if (response.status === 200 || response.status === 201) {
        const result = response.data;
        setResults(prev => ({ ...prev, operation: result }));
        setToast({ message: '공정이 성공적으로 생성되었습니다!', type: 'success' });
        setOperationForm({
          name: '',
          facility_id: 1,
          category: '',
          boundary_id: 1,
          input_kind: 'material',
          material_id: null,
          fuel_id: null,
          quantity: 0,
          unit_id: 1
        }); // 폼 초기화
      } else {
        setToast({ message: '공정 생성 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Operation creation error:', error);
      setToast({ message: '공정 생성 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleNodeCreate = async () => {
    if (!nodeForm.node_type || !nodeForm.ref_id) {
      setToast({ message: '노드 타입과 참조 ID를 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/api/v1/boundary/calc/node', nodeForm);
      
      if (response.status === 200 || response.status === 201) {
        const result = response.data;
        setResults(prev => ({ ...prev, node: result }));
        setToast({ message: '노드가 성공적으로 생성되었습니다!', type: 'success' });
        setNodeForm({
          boundary_id: 1,
          node_type: 'product',
          ref_id: 1,
          label: '',
          pos_x: 0,
          pos_y: 0
        }); // 폼 초기화
      } else {
        setToast({ message: '노드 생성 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Node creation error:', error);
      setToast({ message: '노드 생성 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleEdgeCreate = async () => {
    if (!edgeForm.sourcenode_id || !edgeForm.targetnode_id || !edgeForm.flow_type) {
      setToast({ message: '시작 노드, 도착 노드, 흐름 유형을 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/api/v1/boundary/calc/edge', edgeForm);
      
      if (response.status === 200 || response.status === 201) {
        const result = response.data;
        setResults(prev => ({ ...prev, edge: result }));
        setToast({ message: '엣지가 성공적으로 생성되었습니다!', type: 'success' });
        setEdgeForm({
          boundary_id: 1,
          sourcenode_id: '',
          targetnode_id: '',
          flow_type: 'material',
          label: ''
        }); // 폼 초기화
      } else {
        setToast({ message: '엣지 생성 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Edge creation error:', error);
      setToast({ message: '엣지 생성 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleEmissionCreate = async () => {
    if (!emissionForm.product_id || !emissionForm.boundary_id) {
      setToast({ message: '제품 ID와 경계 ID를 입력해주세요.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/api/v1/boundary/calc/production-emission', emissionForm);
      
      if (response.status === 200 || response.status === 201) {
        const result = response.data;
        setResults(prev => ({ ...prev, emission: result }));
        setToast({ message: '생산 배출량이 성공적으로 생성되었습니다!', type: 'success' });
        setEmissionForm({
          product_id: 1,
          boundary_id: 1,
          result_unit_id: 1,
          dir_emission: 0,
          indir_emission: 0,
          see: 0
        }); // 폼 초기화
      } else {
        setToast({ message: '생산 배출량 생성 중 오류가 발생했습니다.', type: 'error' });
      }
    } catch (error) {
      console.error('Emission creation error:', error);
      setToast({ message: '생산 배출량 생성 중 오류가 발생했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // 🎨 렌더링 함수들
  // ============================================================================

  const renderFuelCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔥 연료 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              연료명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={fuelForm.fuel_name}
              onChange={(e) => setFuelForm(prev => ({ ...prev, fuel_name: e.target.value }))}
              placeholder="예: 천연가스"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              연료량 (톤) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={fuelForm.fuel_amount}
              onChange={(e) => setFuelForm(prev => ({ ...prev, fuel_amount: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleFuelCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          연료 배출량 계산
        </Button>

        {results.fuel && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
            <h4 className="font-semibold text-green-400 mb-3">🔥 연료 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>연료명:</strong> {results.fuel.fuel_name}</p>
              <p><strong>총 배출량:</strong> {results.fuel.emission?.toFixed(2)} tCO₂</p>
              <p><strong>배출계수:</strong> {results.fuel.emission_factor} tCO₂/TJ</p>
              <p><strong>순발열량:</strong> {results.fuel.net_calorific_value} TJ/Gg</p>
              <p><strong>계산식:</strong> {results.fuel.calculation_formula}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderMaterialCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🧱 원료 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              원료명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={materialForm.material_name}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, material_name: e.target.value }))}
              placeholder="예: 철광석"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              원료량 (톤) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={materialForm.material_amount}
              onChange={(e) => setMaterialForm(prev => ({ ...prev, material_amount: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleMaterialCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          원료 배출량 계산
        </Button>

        {results.material && (
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <h4 className="font-semibold text-blue-400 mb-3">🧱 원료 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>원료명:</strong> {results.material.material_name}</p>
              <p><strong>총 배출량:</strong> {results.material.emission?.toFixed(2)} tCO₂</p>
              <p><strong>배출계수:</strong> {results.material.emission_factor} tCO₂/톤</p>
              <p><strong>계산식:</strong> {results.material.calculation_formula}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderPrecursorCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔬 전구물질 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              전구물질명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={precursorForm.precursor_name}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, precursor_name: e.target.value }))}
              placeholder="예: 석회석"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              사용량 (톤) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={precursorForm.emission_factor}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, emission_factor: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              배출계수 (tCO2/톤) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={precursorForm.emission_factor}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, emission_factor: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              탄소함량 (%)
            </label>
            <Input
              type="number"
              value={precursorForm.carbon_content}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, carbon_content: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              max="100"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handlePrecursorCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          전구물질 배출량 계산
        </Button>

        {results.precursor && (
          <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <h4 className="font-semibold text-yellow-400 mb-3">🔬 전구물질 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>전구물질명:</strong> {results.precursor.precursor_name}</p>
              <p><strong>총 배출량:</strong> {results.precursor.emission?.toFixed(2)} tCO₂</p>
              <p><strong>배출계수:</strong> {results.precursor.emission_factor} tCO₂/톤</p>
              <p><strong>탄소함량:</strong> {results.precursor.carbon_content}%</p>
              <p><strong>계산식:</strong> {results.precursor.calculation_formula}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderElectricityCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">⚡ 전력 사용 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              전력 사용량 (MWh) <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={electricityForm.power_usage}
              onChange={(e) => setElectricityForm(prev => ({ ...prev, power_usage: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              배출계수 (tCO2/MWh)
            </label>
            <Input
              type="number"
              value={electricityForm.emission_factor}
              onChange={(e) => setElectricityForm(prev => ({ ...prev, emission_factor: parseFloat(e.target.value) || 0.4567 }))}
              placeholder="0.4567"
              min="0"
              step="0.0001"
              className="w-full"
            />
          </div>
        </div>

        <div className="mb-6 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <p className="text-sm text-blue-300">
            <strong>참고:</strong> 전력배출계수는 2014~2016 연평균 기본값을 사용함 (0.4567 tCO2/MWh)
          </p>
        </div>

        <Button
          onClick={handleElectricityCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          전력 사용 배출량 계산
        </Button>

        {results.electricity && (
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <h4 className="font-semibold text-blue-400 mb-3">⚡ 전력 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>전력 사용량:</strong> {results.electricity.power_usage} MWh</p>
              <p><strong>총 배출량:</strong> {results.electricity.emission?.toFixed(2)} tCO₂</p>
              <p><strong>배출계수:</strong> {results.electricity.emission_factor} tCO₂/MWh</p>
              <p><strong>계산식:</strong> {results.electricity.calculation_formula}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderProcessCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🏭 생산 공정 배출량 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              공정명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={processForm.process_name}
              onChange={(e) => setProcessForm(prev => ({ ...prev, process_name: e.target.value }))}
              placeholder="예: 용해 공정"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              시작일 <span className="text-red-500">*</span>
            </label>
            <Input
              type="date"
              value={processForm.start_date}
              onChange={(e) => setProcessForm(prev => ({ ...prev, start_date: e.target.value }))}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              종료일 <span className="text-red-500">*</span>
            </label>
            <Input
              type="date"
              value={processForm.end_date}
              onChange={(e) => setProcessForm(prev => ({ ...prev, end_date: e.target.value }))}
              className="w-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">투입 연료명</label>
            <Input
              value={processForm.input_fuel_name || ''}
              onChange={(e) => setProcessForm(prev => ({ ...prev, input_fuel_name: e.target.value }))}
              placeholder="예: 천연가스"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">투입 연료량 (톤)</label>
            <Input
              type="number"
              value={processForm.input_fuel_amount || 0}
              onChange={(e) => setProcessForm(prev => ({ ...prev, input_fuel_amount: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">투입 원료명</label>
            <Input
              value={processForm.input_material_name || ''}
              onChange={(e) => setProcessForm(prev => ({ ...prev, input_material_name: e.target.value }))}
              placeholder="예: 철광석"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">투입 원료량 (톤)</label>
            <Input
              type="number"
              value={processForm.input_material_amount || 0}
              onChange={(e) => setProcessForm(prev => ({ ...prev, input_material_amount: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">전력 사용량 (MWh)</label>
            <Input
              type="number"
              value={processForm.power_usage || 0}
              onChange={(e) => setProcessForm(prev => ({ ...prev, power_usage: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleProcessCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          공정 배출량 계산
        </Button>

        {results.process && results.process.length > 0 && (
          <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <h4 className="font-semibold text-purple-400 mb-3">🏭 공정 계산 결과</h4>
            <div className="space-y-2 text-sm">
              {results.process.map((process, index) => (
                <div key={index} className="p-3 bg-gray-800 border border-gray-700 rounded-lg">
                  <p><strong>공정명:</strong> {process.process_name}</p>
                  <p><strong>직접 배출량:</strong> {process.direct_emission?.toFixed(2)} tCO₂</p>
                  <p><strong>간접 배출량:</strong> {process.indirect_emission?.toFixed(2)} tCO₂</p>
                  <p><strong>전구물질 배출량:</strong> {process.precursor_emission?.toFixed(2)} tCO₂</p>
                  <p><strong>총 배출량:</strong> {process.total_emission?.toFixed(2)} tCO₂</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderPrecursorManagement = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔬 전구물질 관리</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">사용자 ID <span className="text-red-500">*</span>
            </label>
            <Input
              value={precursorForm.user_id}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, user_id: e.target.value }))}
              placeholder="사용자 ID"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">전구물질명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={precursorForm.precursor_name}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, precursor_name: e.target.value }))}
              placeholder="예: 석회석"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">배출계수            </label>
            <Input
              type="number"
              value={precursorForm.emission_factor}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, emission_factor: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">탄소함량            </label>
            <Input
              type="number"
              value={precursorForm.carbon_content}
              onChange={(e) => setPrecursorForm(prev => ({ ...prev, carbon_content: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handlePrecursorSave}
            loading={loading}
            variant="primary"
            className="flex-1 md:flex-none"
          >
            전구물질 저장
          </Button>
          
          <Button
            onClick={handlePrecursorLoad}
            loading={loading}
            variant="secondary"
            className="flex-1 md:flex-none"
          >
            전구물질 조회
          </Button>
        </div>

        {/* 전구물질 목록 */}
        {precursorList.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-white mb-3">저장된 전구물질</h4>
            <div className="space-y-2">
              {precursorList.map((precursor, index) => (
                <div key={index} className="p-3 bg-gray-800 border border-gray-700 rounded-lg">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div><strong>이름:</strong> {precursor.precursor_name}</div>
                    <div><strong>배출계수:</strong> {precursor.emission_factor}</div>
                    <div><strong>탄소함량:</strong> {precursor.carbon_content}</div>
                    <div><strong>사용자:</strong> {precursor.user_id}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderCBAMCalculation = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🎯 CBAM 종합 계산</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">제품명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={cbamForm.product_name}
              onChange={(e) => setCbamForm(prev => ({ ...prev, product_name: e.target.value }))}
              placeholder="예: 철강 제품"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">연료 배출량 (tCO₂)            </label>
            <Input
              type="number"
              value={cbamForm.fuel_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, fuel_emissions: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">원료 배출량 (tCO₂)            </label>
            <Input
              type="number"
              value={cbamForm.material_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, material_emissions: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">전구물질 배출량 (tCO₂)            </label>
            <Input
              type="number"
              value={cbamForm.precursor_emissions}
              onChange={(e) => setCbamForm(prev => ({ ...prev, precursor_emissions: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleCBAMCalculation}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          CBAM 종합 계산
        </Button>

        {results.cbam && (
          <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <h4 className="font-semibold text-purple-400 mb-3">🎯 CBAM 계산 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>제품명:</strong> {results.cbam.product_name}</p>
              <p><strong>총 배출량:</strong> {results.cbam.emission?.toFixed(2)} tCO₂eq</p>
              <p><strong>CBAM 요율:</strong> €{results.cbam.cbam_rate}/tCO₂eq</p>
              <p><strong>CBAM 비용:</strong> €{results.cbam.cbam_cost?.toFixed(2)}</p>
              {results.cbam.breakdown && (
                <div className="mt-3 pt-3 border-t border-purple-500/30">
                  <p className="font-semibold mb-1">배출량 세부사항:</p>
                  <p>• 연료 배출량: {results.cbam.breakdown.fuel_emissions.toFixed(2)} tCO₂</p>
                  <p>• 원료 배출량: {results.cbam.breakdown.material_emissions.toFixed(2)} tCO₂</p>
                  <p>• 전구물질 배출량: {results.cbam.breakdown.precursor_emissions.toFixed(2)} tCO₂</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderStats = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">📊 계산 통계</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-blue-400 mb-2">연료 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.fuel_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
          
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-green-400 mb-2">원료 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.material_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
          
          <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-purple-400 mb-2">CBAM 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.cbam_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
          
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4">
            <h4 className="font-semibold text-orange-400 mb-2">전체 계산</h4>
            <p className="text-2xl font-bold">{results.stats?.total_calculations || 0}</p>
            <p className="text-sm text-gray-400">총 계산 횟수</p>
          </div>
        </div>

        {/* 최근 계산 이력 */}
        {results.stats?.recent_calculations && results.stats.recent_calculations.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-white mb-3">최근 계산 이력</h4>
            <div className="space-y-2">
              {results.stats.recent_calculations.map((calc, index) => (
                <div key={index} className="p-3 bg-gray-800 border border-gray-700 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">{calc.type}</span>
                      <span className="text-sm text-gray-300">
                        {new Date(calc.timestamp).toLocaleString('ko-KR')}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-white">
                      {calc.emission.toFixed(2)} tCO₂eq
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderBoundaryForm = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🗺️ 경계 생성</h3>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-white mb-2">
            경계명 <span className="text-red-500">*</span>
          </label>
          <Input
            value={boundaryForm.name}
            onChange={(e) => setBoundaryForm(prev => ({ ...prev, name: e.target.value }))}
            placeholder="예: 철강 생산 경계"
            className="w-full"
          />
        </div>

        <Button
          onClick={handleBoundaryCreate}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          경계 생성
        </Button>

        {results.boundary && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
            <h4 className="font-semibold text-green-400 mb-3">✅ 경계 생성 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>경계 ID:</strong> {results.boundary.boundary_id}</p>
              <p><strong>경계명:</strong> {results.boundary.name}</p>
              <p><strong>생성일:</strong> {results.boundary.created_at}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderProductForm = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">📦 제품 생성</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              제품명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={productForm.name}
              onChange={(e) => setProductForm(prev => ({ ...prev, name: e.target.value }))}
              placeholder="예: 철강 제품"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              CN 코드
            </label>
            <Input
              value={productForm.cn_code}
              onChange={(e) => setProductForm(prev => ({ ...prev, cn_code: e.target.value }))}
              placeholder="예: 7208"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              시작일 <span className="text-red-500">*</span>
            </label>
            <Input
              type="date"
              value={productForm.period_start}
              onChange={(e) => setProductForm(prev => ({ ...prev, period_start: e.target.value }))}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              종료일 <span className="text-red-500">*</span>
            </label>
            <Input
              type="date"
              value={productForm.period_end}
              onChange={(e) => setProductForm(prev => ({ ...prev, period_end: e.target.value }))}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              생산량 (톤)
            </label>
            <Input
              type="number"
              value={productForm.production_qty}
              onChange={(e) => setProductForm(prev => ({ ...prev, production_qty: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              외부판매량 (톤)
            </label>
            <Input
              type="number"
              value={productForm.sales_qty}
              onChange={(e) => setProductForm(prev => ({ ...prev, sales_qty: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleProductCreate}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          제품 생성
        </Button>

        {results.product && (
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <h4 className="font-semibold text-blue-400 mb-3">✅ 제품 생성 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>제품 ID:</strong> {results.product.product_id}</p>
              <p><strong>제품명:</strong> {results.product.name}</p>
              <p><strong>CN 코드:</strong> {results.product.cn_code}</p>
              <p><strong>기간:</strong> {results.product.period_start} ~ {results.product.period_end}</p>
              <p><strong>생산량:</strong> {results.product.production_qty} 톤</p>
              <p><strong>외부판매량:</strong> {results.product.sales_qty} 톤</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderOperationForm = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🏭 공정 생성</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              공정명 <span className="text-red-500">*</span>
            </label>
            <Input
              value={operationForm.name}
              onChange={(e) => setOperationForm(prev => ({ ...prev, name: e.target.value }))}
              placeholder="예: 용해 공정"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              공정 분류
            </label>
            <Input
              value={operationForm.category}
              onChange={(e) => setOperationForm(prev => ({ ...prev, category: e.target.value }))}
              placeholder="예: 제강"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              입력 종류 <span className="text-red-500">*</span>
            </label>
            <select
              value={operationForm.input_kind}
              onChange={(e) => setOperationForm(prev => ({ ...prev, input_kind: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="material">원료 (material)</option>
              <option value="fuel">연료 (fuel)</option>
              <option value="electricity">전력 (electricity)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              사용량
            </label>
            <Input
              type="number"
              value={operationForm.quantity}
              onChange={(e) => setOperationForm(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleOperationCreate}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          공정 생성
        </Button>

        {results.operation && (
          <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <h4 className="font-semibold text-purple-400 mb-3">✅ 공정 생성 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>공정 ID:</strong> {results.operation.operation_id}</p>
              <p><strong>공정명:</strong> {results.operation.name}</p>
              <p><strong>공정 분류:</strong> {results.operation.category}</p>
              <p><strong>입력 종류:</strong> {results.operation.input_kind}</p>
              <p><strong>사용량:</strong> {results.operation.quantity}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderNodeForm = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔘 노드 생성</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              노드 타입 <span className="text-red-500">*</span>
            </label>
            <select
              value={nodeForm.node_type}
              onChange={(e) => setNodeForm(prev => ({ ...prev, node_type: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="product">제품 (product)</option>
              <option value="operation">공정 (operation)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              참조 ID <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={nodeForm.ref_id}
              onChange={(e) => setNodeForm(prev => ({ ...prev, ref_id: parseInt(e.target.value) || 1 }))}
              placeholder="1"
              min="1"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              라벨
            </label>
            <Input
              value={nodeForm.label}
              onChange={(e) => setNodeForm(prev => ({ ...prev, label: e.target.value }))}
              placeholder="화면 표시용 라벨"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              X 좌표
            </label>
            <Input
              type="number"
              value={nodeForm.pos_x}
              onChange={(e) => setNodeForm(prev => ({ ...prev, pos_x: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              step="0.1"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleNodeCreate}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          노드 생성
        </Button>

        {results.node && (
          <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <h4 className="font-semibold text-yellow-400 mb-3">✅ 노드 생성 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>노드 ID:</strong> {results.node.node_id}</p>
              <p><strong>노드 타입:</strong> {results.node.node_type}</p>
              <p><strong>참조 ID:</strong> {results.node.ref_id}</p>
              <p><strong>라벨:</strong> {results.node.label}</p>
              <p><strong>위치:</strong> ({results.node.pos_x}, {results.node.pos_y})</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderEdgeForm = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🔗 엣지 생성</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              시작 노드 ID <span className="text-red-500">*</span>
            </label>
            <Input
              value={edgeForm.sourcenode_id}
              onChange={(e) => setEdgeForm(prev => ({ ...prev, sourcenode_id: e.target.value }))}
              placeholder="예: node-1"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              도착 노드 ID <span className="text-red-500">*</span>
            </label>
            <Input
              value={edgeForm.targetnode_id}
              onChange={(e) => setEdgeForm(prev => ({ ...prev, targetnode_id: e.target.value }))}
              placeholder="예: node-2"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              흐름 유형 <span className="text-red-500">*</span>
            </label>
            <select
              value={edgeForm.flow_type}
              onChange={(e) => setEdgeForm(prev => ({ ...prev, flow_type: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="material">원료 (material)</option>
              <option value="fuel">연료 (fuel)</option>
              <option value="electricity">전력 (electricity)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              라벨
            </label>
            <Input
              value={edgeForm.label}
              onChange={(e) => setEdgeForm(prev => ({ ...prev, label: e.target.value }))}
              placeholder="화면 표시용 라벨"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleEdgeCreate}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          엣지 생성
        </Button>

        {results.edge && (
          <div className="mt-6 p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <h4 className="font-semibold text-orange-400 mb-3">✅ 엣지 생성 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>엣지 ID:</strong> {results.edge.edge_id}</p>
              <p><strong>시작 노드:</strong> {results.edge.sourcenode_id}</p>
              <p><strong>도착 노드:</strong> {results.edge.targetnode_id}</p>
              <p><strong>흐름 유형:</strong> {results.edge.flow_type}</p>
              <p><strong>라벨:</strong> {results.edge.label}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderEmissionForm = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-6">🌱 생산 배출량 생성</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              제품 ID <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={emissionForm.product_id}
              onChange={(e) => setEmissionForm(prev => ({ ...prev, product_id: parseInt(e.target.value) || 1 }))}
              placeholder="1"
              min="1"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              경계 ID <span className="text-red-500">*</span>
            </label>
            <Input
              type="number"
              value={emissionForm.boundary_id}
              onChange={(e) => setEmissionForm(prev => ({ ...prev, boundary_id: parseInt(e.target.value) || 1 }))}
              placeholder="1"
              min="1"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              간접귀속배출량 (tCO₂)
            </label>
            <Input
              type="number"
              value={emissionForm.dir_emission}
              onChange={(e) => setEmissionForm(prev => ({ ...prev, dir_emission: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              직접귀속배출량 (tCO₂)
            </label>
            <Input
              type="number"
              value={emissionForm.indir_emission}
              onChange={(e) => setEmissionForm(prev => ({ ...prev, indir_emission: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              제품 고유 내재배출량 (tCO₂)
            </label>
            <Input
              type="number"
              value={emissionForm.see}
              onChange={(e) => setEmissionForm(prev => ({ ...prev, see: parseFloat(e.target.value) || 0 }))}
              placeholder="0"
              min="0"
              step="0.01"
              className="w-full"
            />
          </div>
        </div>

        <Button
          onClick={handleEmissionCreate}
          loading={loading}
          variant="primary"
          className="w-full md:w-auto"
        >
          생산 배출량 생성
        </Button>

        {results.emission && (
          <div className="mt-6 p-4 bg-teal-500/10 border border-teal-500/30 rounded-lg">
            <h4 className="font-semibold text-teal-400 mb-3">✅ 생산 배출량 생성 결과</h4>
            <div className="space-y-2 text-sm">
              <p><strong>결과 ID:</strong> {results.emission.prod_result_id}</p>
              <p><strong>제품 ID:</strong> {results.emission.product_id}</p>
              <p><strong>경계 ID:</strong> {results.emission.boundary_id}</p>
              <p><strong>간접귀속배출량:</strong> {results.emission.dir_emission} tCO₂</p>
              <p><strong>직접귀속배출량:</strong> {results.emission.indir_emission} tCO₂</p>
              <p><strong>제품 고유 내재배출량:</strong> {results.emission.see} tCO₂</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🧮 CBAM 배출량 계산</h1>
          <p className="text-gray-300">
            연료, 원료, 전구물질의 배출량을 계산하고 CBAM 비용을 산출합니다
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-8">
          {[
            { key: 'fuel', label: '🔥 연료 계산', badge: 'Fuel' },
            { key: 'material', label: '🧱 원료 계산', badge: 'Material' },
            { key: 'precursor', label: '🔬 전구물질', badge: 'Precursor' },
            { key: 'electricity', label: '⚡ 전력 계산', badge: 'Power' },
            { key: 'process', label: '🏭 공정 계산', badge: 'Process' },
            { key: 'cbam', label: '🎯 CBAM 계산', badge: 'CBAM' },
            { key: 'stats', label: '📊 통계', badge: 'Stats' },
            { key: 'boundary', label: '🗺️ 경계', badge: 'Boundary' },
            { key: 'product', label: '📦 제품', badge: 'Product' },
            { key: 'operation', label: '🏭 공정', badge: 'Operation' },
            { key: 'node', label: '🔘 노드', badge: 'Node' },
            { key: 'edge', label: '🔗 엣지', badge: 'Edge' },
            { key: 'emission', label: '🌱 배출량', badge: 'Emission' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {tab.label}
              <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">{tab.badge}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'fuel' && renderFuelCalculation()}
        {activeTab === 'material' && renderMaterialCalculation()}
        {activeTab === 'precursor' && renderPrecursorCalculation()}
        {activeTab === 'electricity' && renderElectricityCalculation()}
        {activeTab === 'process' && renderProcessCalculation()}
        {activeTab === 'cbam' && renderCBAMCalculation()}
        {activeTab === 'stats' && renderStats()}
        {activeTab === 'boundary' && renderBoundaryForm()}
        {activeTab === 'product' && renderProductForm()}
        {activeTab === 'operation' && renderOperationForm()}
        {activeTab === 'node' && renderNodeForm()}
        {activeTab === 'edge' && renderEdgeForm()}
        {activeTab === 'emission' && renderEmissionForm()}

        {/* Toast */}
        {toast && (
          <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            toast.type === 'success' ? 'bg-green-600' :
            toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
          } text-white`}>
            <div className="flex items-center justify-between">
              <span>{toast.message}</span>
              <button
                onClick={() => setToast(null)}
                className="ml-2 text-white hover:text-gray-200"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
