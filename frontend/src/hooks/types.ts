/**
 * CBAM 관련 타입 정의
 * 단일 책임: 모든 훅에서 사용하는 공통 타입 정의
 */

export interface Install {
  id: number;
  install_name: string;
  reporting_year?: string;
}

export interface Product {
  id: number;
  product_name: string;
  product_category?: string;
  product_amount?: number;
  product_sell?: number;
  product_eusell?: number;
  install_id: number;
  cncode_total?: string;
  goods_name?: string;
  aggrgoods_name?: string;
}

export interface Process {
  id: number;
  process_name: string;
  // 공정 소속 사업장 ID (백엔드 응답 포함)
  install_id?: number;
  // 선택적으로 내려오는 사업장명
  install_name?: string;
  start_period?: string;
  end_period?: string;
  products?: Product[];
}
