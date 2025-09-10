# CBAM 프로젝트 개발 작업 방식 가이드

## 📋 개요
이 문서는 CBAM(Carbon Border Adjustment Mechanism) 프로젝트의 개발 작업을 수행할 때 따라야 할 체계적인 방식과 절차를 정리한 가이드입니다.

## 🎯 핵심 원칙

### 1. 문제 진단 우선
- **항상 문제를 정확히 진단한 후 해결책을 제시**
- 사용자가 보고한 현상과 실제 원인을 구분
- 로그, 콘솔 오류, 네트워크 상태 등을 종합적으로 분석

### 2. 기존 기능 보호
- **"현재 있는 기능들에 문제가 없도록 해야 한다"** - 사용자 요구사항
- 수정 시 기존 기능들의 정상 작동을 보장
- 변경사항이 다른 기능에 미치는 영향을 사전 검토

### 3. 단계별 접근
- 문제 분석 → 원인 파악 → 해결책 설계 → 구현 → 테스트 → 검증
- 각 단계마다 명확한 설명과 근거 제시

## 🔍 문제 진단 프로세스

### 1단계: 현상 파악
```markdown
- 사용자가 보고한 구체적인 현상 파악
- 예상되는 정상 동작과 실제 동작의 차이점 식별
- 관련된 UI 요소, 데이터, API 엔드포인트 확인
```

### 2단계: 로그 및 오류 분석
```bash
# 콘솔 로그 확인
- 브라우저 개발자 도구의 Console 탭
- Network 탭에서 API 요청/응답 상태
- 서버 로그 (Railway, Vercel 등)

# API 테스트
- PowerShell을 사용한 API 직접 호출
- 데이터베이스 상태 확인
```

### 3단계: 코드 분석
```typescript
// 관련 파일들 순차적 분석
1. 프론트엔드: React 컴포넌트, 훅, API 호출 로직
2. 백엔드: 서비스, 컨트롤러, 리포지토리, 스키마
3. 데이터베이스: 테이블 구조, 관계, 제약조건
```

## 🛠️ 해결책 구현 방식

### 1. 백엔드 수정 우선
```python
# 1. 비즈니스 로직 수정
- 서비스 레이어에서 핵심 로직 구현
- 데이터 검증 및 유효성 검사 강화
- 에러 처리 및 로깅 개선

# 2. API 엔드포인트 수정
- 컨트롤러에서 요청/응답 처리 개선
- 스키마 정의 업데이트
- HTTP 상태 코드 및 에러 메시지 정확성

# 3. 데이터베이스 로직 수정
- 리포지토리에서 쿼리 최적화
- 트랜잭션 처리 개선
- 데이터 일관성 보장
```

### 2. 프론트엔드 수정
```typescript
// 1. 상태 관리 개선
- React 상태 업데이트 로직 수정
- 실시간 데이터 동기화 구현
- 캐시 무효화 및 새로고침 로직

// 2. API 호출 최적화
- 요청/응답 처리 개선
- 에러 핸들링 강화
- 로딩 상태 관리

// 3. UI/UX 개선
- 사용자 피드백 제공
- 실시간 업데이트 반영
- 직관적인 인터페이스
```

### 3. 통합 및 동기화
```typescript
// 이벤트 기반 통신
- 커스텀 이벤트를 통한 컴포넌트 간 통신
- 실시간 데이터 동기화
- 상태 변경 전파

// API 연동
- 백엔드 API와 프론트엔드 상태 동기화
- 데이터 일관성 보장
- 실시간 업데이트 구현
```

## 📝 작업 기록 방식

### 1. 문제 분석 기록
```markdown
## 1단계: 문제 진단
- **현상**: 사용자가 보고한 구체적인 문제
- **원인**: 코드 분석을 통한 근본 원인
- **영향 범위**: 문제가 미치는 다른 기능들
```

### 2. 해결 과정 기록
```markdown
## 2단계: 해결 방법
- **수정 파일**: 변경된 파일 목록
- **수정 내용**: 구체적인 코드 변경사항
- **이유**: 왜 이렇게 수정했는지 설명
```

### 3. 테스트 및 검증
```markdown
## 3단계: 테스트
- **API 테스트**: PowerShell을 통한 직접 테스트
- **기능 테스트**: 수정된 기능의 정상 작동 확인
- **회귀 테스트**: 기존 기능들의 정상 작동 확인
```

## 🔧 구체적인 작업 사례

### 사례 1: 제품 판매량 수정 시 실시간 배출량 전파 문제

#### 문제 진단
```markdown
**현상**: 블룸 제품의 판매량을 수정해도 압연→형강으로 이어지는 배출량 전파가 실시간으로 반영되지 않음

**원인**: 
1. 제품 수량 업데이트 후 노드들의 배출량이 새로고침되지 않음
2. 연결된 공정들의 배출량도 업데이트되지 않음
3. 전체 그래프의 배출량 전파가 자동으로 실행되지 않음
```

#### 해결 방법
```typescript
// 1. useProcessManager.ts 수정
const handleProductQuantityUpdate = useCallback(async (productQuantityForm) => {
  // 제품 수량 업데이트
  await axiosClient.put(apiEndpoints.cbam.product.update(selectedProduct.id), productQuantityForm);
  
  // 전체 그래프 배출량 재계산
  await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate);
  
  // 연결된 공정들의 배출량 새로고침
  for (const process of connectedProcesses) {
    await axiosClient.post(apiEndpoints.cbam.edge.saveProcessEmission(process.id));
  }
  
  // 캔버스 노드 새로고침 이벤트 발생
  window.dispatchEvent(new CustomEvent('cbam:refreshAllNodesAfterProductUpdate', {
    detail: { productId: selectedProduct.id }
  }));
}, [selectedProduct, processes]);

// 2. useProcessCanvas.ts 수정
const refreshAllNodesAfterProductUpdate = useCallback(async (productId) => {
  // 전체 그래프 배출량 전파
  await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate);
  
  // 모든 제품 노드 새로고침
  const productNodes = nodes.filter(n => n.type === 'product');
  for (const node of productNodes) {
    await refreshProductEmission((node.data as any)?.id);
  }
  
  // 모든 공정 노드 새로고침
  const processNodes = nodes.filter(n => n.type === 'process');
  for (const node of processNodes) {
    await refreshProcessEmission((node.data as any)?.id);
  }
}, [nodes, refreshProductEmission, refreshProcessEmission]);

// 3. 이벤트 리스너 추가
useEffect(() => {
  const handler = async (event: CustomEvent) => {
    const { productId } = event.detail;
    if (productId) {
      await refreshAllNodesAfterProductUpdate(productId);
    }
  };
  
  window.addEventListener('cbam:refreshAllNodesAfterProductUpdate' as any, handler);
  return () => window.removeEventListener('cbam:refreshAllNodesAfterProductUpdate' as any, handler);
}, [refreshAllNodesAfterProductUpdate]);
```

### 사례 2: 엣지 유효성 검증 로직 추가

#### 문제 진단
```markdown
**현상**: 이상한 엣지들이 생성됨 (제품-제품 연결, 다른 제품에 귀속된 공정 간 연결 등)

**원인**: 엣지 생성 시 유효성 검증 로직이 부족함
```

#### 해결 방법
```python
# 1. 백엔드 유효성 검증 추가 (edge_service.py)
async def _validate_edge(self, edge_data) -> Dict[str, Any]:
    # 엣지 종류별 연결 규칙 검증
    validation_rules = {
        'consume': [('product', 'process')],  # 제품 → 공정
        'produce': [('process', 'product')],  # 공정 → 제품
        'continue': [('process', 'process')]  # 공정 → 공정
    }
    
    # 동일 노드 간 연결 방지
    if source_id == target_id:
        return {'valid': False, 'error': '동일한 노드 간 연결은 허용되지 않습니다.'}
    
    # 제품-제품 연결 방지
    if source_type == 'product' and target_type == 'product':
        return {'valid': False, 'error': '제품 간 직접 연결은 허용되지 않습니다.'}
    
    # 공정-공정 연결 시 같은 제품에 귀속된 공정들끼리만 연결 가능
    if edge_kind == 'continue' and source_type == 'process' and target_type == 'process':
        same_product_check = await self._check_same_product_processes(source_id, target_id)
        if not same_product_check['valid']:
            return same_product_check

# 2. 프론트엔드 유효성 검증 추가
export const validateEdgeConnection = (sourceId, targetId, sourceType, targetType) => {
  // 클라이언트 측 사전 검증
  if (sourceId === targetId) {
    return { valid: false, error: '동일한 노드 간 연결은 허용되지 않습니다.' };
  }
  
  if (sourceType === 'product' && targetType === 'product') {
    return { valid: false, error: '제품 간 직접 연결은 허용되지 않습니다.' };
  }
  
  // 유효한 연결 규칙 검증
  const validConnections = [
    { source: 'process', target: 'process' },
    { source: 'process', target: 'product' },
    { source: 'product', target: 'process' }
  ];
  
  const isValidConnection = validConnections.some(
    conn => conn.source === sourceType && conn.target === targetType
  );
  
  if (!isValidConnection) {
    return { valid: false, error: '유효하지 않은 연결입니다.' };
  }
  
  return { valid: true, error: null };
};
```

## 🧪 테스트 방식

### 1. API 직접 테스트
```powershell
# PowerShell을 사용한 API 테스트
Write-Host "=== API 테스트 ===";
$response = Invoke-WebRequest -Uri "https://gateway-production-22ef.up.railway.app/api/v1/cbam/product/76" -Method GET -Headers @{"Content-Type"="application/json"};
$product = $response.Content | ConvertFrom-Json;
Write-Host "제품 데이터: $($product.product_sell)";
```

### 2. 기능 테스트
```markdown
1. 수정된 기능의 정상 작동 확인
2. 기존 기능들의 정상 작동 확인 (회귀 테스트)
3. 에러 상황에서의 적절한 처리 확인
4. 사용자 경험 개선 확인
```

### 3. 데이터 일관성 확인
```markdown
1. 데이터베이스 상태 확인
2. API 응답 데이터 검증
3. 프론트엔드 상태 동기화 확인
4. 실시간 업데이트 반영 확인
```

## 📚 파일 구조 이해

### 프론트엔드 구조
```
frontend/src/
├── hooks/
│   ├── useProcessCanvas.ts      # React Flow 캔버스 관리
│   ├── useProcessManager.ts     # 제품/공정 상태 관리
│   └── useReactFlowAPI.ts       # React Flow API 연동
├── components/
│   └── templates/               # 레이아웃 컴포넌트
└── app/
    └── (protected)/cbam/        # CBAM 관련 페이지
```

### 백엔드 구조
```
service/cbam-service/app/domain/
├── product/                     # 제품 관련
├── process/                     # 공정 관련
├── edge/                        # 엣지 관련
├── calculation/                 # 배출량 계산
└── productprocess/              # 제품-공정 관계
```

## 🚨 주의사항

### 1. 기존 기능 보호
- 수정 시 기존 기능들의 정상 작동을 반드시 확인
- 변경사항이 다른 기능에 미치는 영향을 사전 검토
- 테스트를 통한 회귀 검증 필수

### 2. 데이터 일관성
- 데이터베이스와 프론트엔드 상태의 동기화 보장
- 실시간 업데이트 시 모든 관련 노드들의 일관성 유지
- 트랜잭션 처리로 데이터 무결성 보장

### 3. 사용자 경험
- 명확한 에러 메시지 제공
- 실시간 피드백 제공
- 직관적인 인터페이스 유지

## 🔄 작업 완료 후 체크리스트

- [ ] 문제가 정확히 해결되었는지 확인
- [ ] 기존 기능들이 정상 작동하는지 확인
- [ ] 새로운 기능이 예상대로 작동하는지 확인
- [ ] 에러 처리가 적절한지 확인
- [ ] 사용자 경험이 개선되었는지 확인
- [ ] 코드 품질이 유지되었는지 확인
- [ ] 테스트를 통한 검증 완료

## 📞 커밋 메시지 가이드

```bash
# 수정 사항과 이유를 명확히 작성
git add .
git commit -m "fix: 제품 수량 변경 시 실시간 배출량 전파 구현

- useProcessManager에서 제품 수량 업데이트 후 전체 그래프 배출량 재계산 추가
- useProcessCanvas에서 이벤트 기반 노드 새로고침 로직 추가
- 제품 수량 변경 시 압연→형강으로 이어지는 배출량이 실시간으로 반영되도록 수정
- 기존 기능들의 정상 작동 보장"
```

---

이 가이드를 따라 작업하면 CBAM 프로젝트의 일관성 있고 안정적인 개발이 가능합니다.
