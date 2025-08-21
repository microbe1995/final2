'use client';

import { useState, useRef } from 'react';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  AlertCircle,
  Loader2,
  Table,
  MapPin,
  Database,
} from 'lucide-react';
import axios from 'axios';
import * as XLSX from 'xlsx';
import CommonShell from '@/components/CommonShell';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface UploadResponse {
  message: string;
  status: string;
  data: {
    filename: string;
    rows_count: number;
    columns: string[];
    shape: [number, number];
  };
}

interface MappingRule {
  sourceColumn: string;
  targetColumn: string;
  transformation?: string;
}

interface TransformedData {
  original: any[];
  transformed: any[];
  mapping: MappingRule[];
}

const DataUploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [excelData, setExcelData] = useState<any[]>([]);
  const [excelColumns, setExcelColumns] = useState<string[]>([]);
  const [mappingRules, setMappingRules] = useState<MappingRule[]>([]);
  const [transformedData, setTransformedData] =
    useState<TransformedData | null>(null);
  const [isTransforming, setIsTransforming] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      // 엑셀 파일 확장자 검증
      if (!selectedFile.name.match(/\.(xlsx|xls)$/)) {
        setError('엑셀 파일만 업로드 가능합니다 (.xlsx, .xls)');
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError(null);
      setUploadResult(null);
      setExcelData([]);
      setExcelColumns([]);
      setMappingRules([]);
      setTransformedData(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      // 엑셀 파일을 JSON으로 변환
      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet);

      // Excel 데이터와 컬럼 설정
      setExcelData(jsonData);
      setExcelColumns(Object.keys(jsonData[0] || {}));

      // 기본 맵핑 규칙 생성
      const defaultMapping: MappingRule[] = Object.keys(jsonData[0] || {}).map(
        col => ({
          sourceColumn: col,
          targetColumn: col,
          transformation: 'none',
        })
      );
      setMappingRules(defaultMapping);

      // JSON 데이터를 게이트웨이로 전송
      const gatewayUrl =
        process.env.NEXT_PUBLIC_GATEWAY_URL ||
        'https://gateway-production-da31.up.railway.app';
      const response = await axios.post(`${gatewayUrl}/process-data`, {
        filename: file.name,
        data: jsonData,
        rows_count: jsonData.length,
        columns: Object.keys(jsonData[0] || {}),
        shape: [jsonData.length, Object.keys(jsonData[0] || {}).length],
      });

      const result: UploadResponse = response.data;
      setUploadResult(result);

      // 성공 메시지 표시
      alert('서비스까지 전송 성공!');
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(
          err.response?.data?.detail ||
            err.message ||
            '파일 업로드 중 오류가 발생했습니다'
        );
      } else {
        setError(
          err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다'
        );
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];

    if (droppedFile && droppedFile.name.match(/\.(xlsx|xls)$/)) {
      setFile(droppedFile);
      setError(null);
      setUploadResult(null);
      setExcelData([]);
      setExcelColumns([]);
      setMappingRules([]);
      setTransformedData(null);
    } else {
      setError('엑셀 파일만 업로드 가능합니다 (.xlsx, .xls)');
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const resetForm = () => {
    setFile(null);
    setError(null);
    setUploadResult(null);
    setExcelData([]);
    setExcelColumns([]);
    setMappingRules([]);
    setTransformedData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleMappingChange = (
    index: number,
    field: keyof MappingRule,
    value: string
  ) => {
    const newMapping = [...mappingRules];
    newMapping[index] = { ...newMapping[index], [field]: value };
    setMappingRules(newMapping);
  };

  const addMappingRule = () => {
    setMappingRules([
      ...mappingRules,
      { sourceColumn: '', targetColumn: '', transformation: 'none' },
    ]);
  };

  const removeMappingRule = (index: number) => {
    const newMapping = mappingRules.filter((_, i) => i !== index);
    setMappingRules(newMapping);
  };

  const handleTransform = () => {
    setIsTransforming(true);

    try {
      // 맵핑 규칙에 따라 데이터 변환
      const transformed = excelData.map(row => {
        const newRow: any = {};
        mappingRules.forEach(rule => {
          if (rule.sourceColumn && rule.targetColumn) {
            let value = row[rule.sourceColumn];

            // 변환 규칙 적용
            if (
              rule.transformation === 'uppercase' &&
              typeof value === 'string'
            ) {
              value = value.toUpperCase();
            } else if (
              rule.transformation === 'lowercase' &&
              typeof value === 'string'
            ) {
              value = value.toLowerCase();
            } else if (
              rule.transformation === 'trim' &&
              typeof value === 'string'
            ) {
              value = value.trim();
            }

            newRow[rule.targetColumn] = value;
          }
        });
        return newRow;
      });

      setTransformedData({
        original: excelData,
        transformed,
        mapping: mappingRules,
      });
    } catch (err) {
      setError('데이터 변환 중 오류가 발생했습니다');
    } finally {
      setIsTransforming(false);
    }
  };

  const handleSaveToDB = async () => {
    if (!transformedData) return;

    setIsSaving(true);
    try {
      // 변환된 데이터를 DB에 저장하는 API 호출
      const gatewayUrl =
        process.env.NEXT_PUBLIC_GATEWAY_URL ||
        'https://gateway-production-da31.up.railway.app';
      const response = await axios.post(`${gatewayUrl}/save-transformed-data`, {
        filename: file?.name,
        originalData: transformedData.original,
        transformedData: transformedData.transformed,
        mappingRules: transformedData.mapping,
      });

      alert('데이터베이스에 성공적으로 저장되었습니다!');
    } catch (err) {
      setError('데이터베이스 저장 중 오류가 발생했습니다');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <CommonShell>
      <div className='space-y-6'>
        <div className='flex flex-col gap-3'>
          <h1 className='stitch-h1 text-3xl font-bold'>데이터 업로드</h1>
          <p className='stitch-caption'>
            엑셀 파일을 업로드하여 데이터를 수집하고 처리합니다
          </p>
        </div>

        {/* 파일 업로드 영역 */}
        <div className='stitch-card p-6'>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              file
                ? 'border-green-300 bg-green-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              ref={fileInputRef}
              type='file'
              accept='.xlsx,.xls'
              onChange={handleFileSelect}
              className='hidden'
            />

            {!file ? (
              <div>
                <Upload className='mx-auto h-12 w-12 text-gray-400 mb-4' />
                <p className='text-lg text-gray-600 mb-2'>
                  파일을 여기에 드래그하거나 클릭하여 선택하세요
                </p>
                <p className='stitch-caption mb-4'>지원 형식: .xlsx, .xls</p>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant='outline'
                >
                  파일 선택
                </Button>
              </div>
            ) : (
              <div>
                <FileSpreadsheet className='mx-auto h-12 w-12 text-green-500 mb-4' />
                <p className='text-lg text-gray-900 mb-2'>{file.name}</p>
                <p className='stitch-caption mb-4'>
                  파일 크기: {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <div className='space-x-3'>
                  <Button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className='disabled:opacity-50 disabled:cursor-not-allowed'
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className='inline h-4 w-4 mr-2 animate-spin' />
                        업로드 중...
                      </>
                    ) : (
                      '업로드'
                    )}
                  </Button>
                  <Button onClick={resetForm} variant='ghost'>
                    취소
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 오류 메시지 */}
        {error && (
          <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
            <div className='flex items-center'>
              <AlertCircle className='h-5 w-5 text-red-400 mr-2' />
              <p className='stitch-error'>{error}</p>
            </div>
          </div>
        )}

        {/* Excel 데이터 표시 */}
        {excelData.length > 0 && (
          <div className='stitch-card p-6'>
            <div className='flex items-center gap-2 mb-4'>
              <Table className='h-5 w-5' />
              <h3 className='stitch-h1 text-lg font-semibold'>
                Excel 데이터 미리보기
              </h3>
            </div>

            <div className='overflow-x-auto'>
              <table className='min-w-full border border-gray-200'>
                <thead>
                  <tr className='bg-gray-50'>
                    {excelColumns.map((column, index) => (
                      <th
                        key={index}
                        className='border border-gray-200 px-3 py-2 text-left text-sm font-medium text-gray-700'
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {excelData.slice(0, 10).map((row, rowIndex) => (
                    <tr key={rowIndex} className='hover:bg-gray-50'>
                      {excelColumns.map((column, colIndex) => (
                        <td
                          key={colIndex}
                          className='border border-gray-200 px-3 py-2 text-sm text-gray-900'
                        >
                          {String(row[column] || '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {excelData.length > 10 && (
                <p className='stitch-caption mt-2 text-center'>
                  상위 10행만 표시됩니다. 총 {excelData.length}행의 데이터가
                  있습니다.
                </p>
              )}
            </div>
          </div>
        )}

        {/* 맵핑 변환 섹션 */}
        {excelData.length > 0 && (
          <div className='stitch-card p-6'>
            <div className='flex items-center gap-2 mb-4'>
              <MapPin className='h-5 w-5' />
              <h3 className='stitch-h1 text-lg font-semibold'>
                데이터 맵핑 및 변환
              </h3>
            </div>

            <div className='space-y-4'>
              {mappingRules.map((rule, index) => (
                <div
                  key={index}
                  className='flex items-center gap-3 p-3 border border-gray-200 rounded-lg'
                >
                  <div className='flex-1'>
                    <label className='stitch-label block mb-1'>원본 컬럼</label>
                    <select
                      value={rule.sourceColumn}
                      onChange={e =>
                        handleMappingChange(
                          index,
                          'sourceColumn',
                          e.target.value
                        )
                      }
                      className='stitch-input'
                    >
                      <option value=''>컬럼 선택</option>
                      {excelColumns.map(col => (
                        <option key={col} value={col}>
                          {col}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className='flex-1'>
                    <label className='stitch-label block mb-1'>대상 컬럼</label>
                    <Input
                      value={rule.targetColumn}
                      onChange={e =>
                        handleMappingChange(
                          index,
                          'targetColumn',
                          e.target.value
                        )
                      }
                      placeholder='새 컬럼명'
                    />
                  </div>

                  <div className='flex-1'>
                    <label className='stitch-label block mb-1'>변환 규칙</label>
                    <select
                      value={rule.transformation}
                      onChange={e =>
                        handleMappingChange(
                          index,
                          'transformation',
                          e.target.value
                        )
                      }
                      className='stitch-input'
                    >
                      <option value='none'>변환 없음</option>
                      <option value='uppercase'>대문자</option>
                      <option value='lowercase'>소문자</option>
                      <option value='trim'>공백 제거</option>
                    </select>
                  </div>

                  <Button
                    onClick={() => removeMappingRule(index)}
                    variant='ghost'
                    className='text-red-600 hover:text-red-700'
                  >
                    삭제
                  </Button>
                </div>
              ))}

              <Button
                onClick={addMappingRule}
                variant='outline'
                className='w-full'
              >
                + 맵핑 규칙 추가
              </Button>

              <div className='flex gap-3'>
                <Button
                  onClick={handleTransform}
                  disabled={isTransforming}
                  className='flex-1'
                >
                  {isTransforming ? (
                    <>
                      <Loader2 className='inline h-4 w-4 mr-2 animate-spin' />
                      변환 중...
                    </>
                  ) : (
                    '변환하기'
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* 변환된 데이터 표시 */}
        {transformedData && (
          <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
            {/* 원본 데이터 */}
            <div className='stitch-card p-6'>
              <h4 className='stitch-h1 text-md font-semibold mb-3'>
                원본 데이터
              </h4>
              <div className='overflow-x-auto'>
                <table className='min-w-full border border-gray-200 text-xs'>
                  <thead>
                    <tr className='bg-gray-50'>
                      {excelColumns.map((column, index) => (
                        <th
                          key={index}
                          className='border border-gray-200 px-2 py-1 text-left'
                        >
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {transformedData.original
                      .slice(0, 5)
                      .map((row, rowIndex) => (
                        <tr key={rowIndex} className='hover:bg-gray-50'>
                          {excelColumns.map((column, colIndex) => (
                            <td
                              key={colIndex}
                              className='border border-gray-200 px-2 py-1'
                            >
                              {String(row[column] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* 변환된 데이터 */}
            <div className='stitch-card p-6'>
              <h4 className='stitch-h1 text-md font-semibold mb-3'>
                변환된 데이터
              </h4>
              <div className='overflow-x-auto'>
                <table className='min-w-full border border-gray-200 text-xs'>
                  <thead>
                    <tr className='bg-gray-50'>
                      {mappingRules.map((rule, index) => (
                        <th
                          key={index}
                          className='border border-gray-200 px-2 py-1 text-left'
                        >
                          {rule.targetColumn}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {transformedData.transformed
                      .slice(0, 5)
                      .map((row, rowIndex) => (
                        <tr key={rowIndex} className='hover:bg-gray-50'>
                          {mappingRules.map((rule, colIndex) => (
                            <td
                              key={colIndex}
                              className='border border-gray-200 px-2 py-1'
                            >
                              {String(row[rule.targetColumn] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* DB 저장 버튼 */}
        {transformedData && (
          <div className='stitch-card p-6'>
            <div className='flex items-center gap-2 mb-4'>
              <Database className='h-5 w-5' />
              <h3 className='stitch-h1 text-lg font-semibold'>
                데이터베이스 저장
              </h3>
            </div>

            <div className='bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4'>
              <p className='stitch-caption text-blue-800'>
                변환된 데이터를 데이터베이스에 저장합니다. 저장 후에는 원본
                데이터와 변환된 데이터가 모두 보관됩니다.
              </p>
            </div>

            <Button
              onClick={handleSaveToDB}
              disabled={isSaving}
              className='w-full'
            >
              {isSaving ? (
                <>
                  <Loader2 className='inline h-4 w-4 mr-2 animate-spin' />
                  저장 중...
                </>
              ) : (
                '확인하기'
              )}
            </Button>
          </div>
        )}

        {/* 업로드 결과 */}
        {uploadResult && (
          <div className='stitch-card p-6'>
            <div className='flex items-center mb-4'>
              <CheckCircle className='h-6 w-6 text-green-500 mr-2' />
              <h3 className='stitch-h1 text-lg font-semibold'>업로드 성공</h3>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
              <div className='bg-gray-50 rounded-lg p-4'>
                <h4 className='font-medium text-gray-700 mb-2'>파일 정보</h4>
                <p className='stitch-caption'>
                  파일명: {uploadResult.data.filename}
                </p>
                <p className='stitch-caption'>
                  크기: {uploadResult.data.shape[0]}행 ×{' '}
                  {uploadResult.data.shape[1]}열
                </p>
              </div>

              <div className='bg-gray-50 rounded-lg p-4'>
                <h4 className='font-medium text-gray-700 mb-2'>데이터 요약</h4>
                <p className='stitch-caption'>
                  총 행 수: {uploadResult.data.rows_count}
                </p>
                <p className='stitch-caption'>
                  총 열 수: {uploadResult.data.columns.length}
                </p>
              </div>
            </div>

            <div className='mt-4'>
              <h4 className='font-medium text-gray-700 mb-2'>컬럼 목록</h4>
              <div className='flex flex-wrap gap-2'>
                {uploadResult.data.columns.map((column, index) => (
                  <span
                    key={index}
                    className='bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full'
                  >
                    {column}
                  </span>
                ))}
              </div>
            </div>

            <div className='mt-6 p-4 bg-green-50 border border-green-200 rounded-lg'>
              <div className='flex items-center'>
                <CheckCircle className='h-5 w-5 text-green-500 mr-2' />
                <p className='text-green-800 font-medium'>
                  게이트웨이를 통해 datagather_service로 전송 성공!
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 시스템 상태 정보 */}
        <div className='stitch-card p-6'>
          <h3 className='stitch-h1 text-lg font-semibold mb-4'>시스템 상태</h3>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
            <div className='text-center p-4 bg-blue-50 rounded-lg'>
              <h4 className='font-medium text-blue-900'>프론트엔드</h4>
              <p className='stitch-caption'>정상 작동</p>
            </div>
            <div className='text-center p-4 bg-green-50 rounded-lg'>
              <h4 className='font-medium text-green-900'>게이트웨이</h4>
              <p className='stitch-caption'>포트 8080</p>
            </div>
            <div className='text-center p-4 bg-purple-50 rounded-lg'>
              <h4 className='font-medium text-purple-900'>
                DataGather Service
              </h4>
              <p className='stitch-caption'>포트 8083</p>
            </div>
          </div>
        </div>
      </div>
    </CommonShell>
  );
};

export default DataUploadPage;
