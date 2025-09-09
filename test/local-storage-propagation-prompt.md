## 로컬 스토리지 기반 전파 로직 구현 프롬프트 (Frontend/Service 공용)

### 목표
- 현재 서비스의 전파 규칙(continue/produce/consume)과 재계산 흐름을 DB 없이 로컬 스토리지(localStorage)만으로 동일하게 동작하도록 구현한다.
- 온라인/오프라인 상관없이 일관된 결과가 나오며, 여러 번 호출해도 값이 누적되지 않는 아이들포턴트(idempotent) 전파를 보장한다.
- 프론트 화면은 저장·엣지 변경·투입량 변경 시 즉시 프리뷰를 갱신한다.

### 범위
- 엔진: 전파/재계산 로직을 순수 TypeScript로 구현하여 localStorage로 상태를 읽고/쓴다.
- 데이터: 공정/제품/엣지/제품↔공정(consumption) 관계, 배출량(직접/누적/프리뷰)을 모두 로컬에 저장한다.
- 프론트 연동: 기존 훅/컴포넌트에서 이벤트를 발생시키고, 로컬 엔진이 반영 후 화면을 갱신한다.

---

### 로컬 스토리지 스키마(v1)
- key: `cbam:graph:v1`
- value(JSON):
```json
{
  "processesById": {
    "241": {"id":241,"install_id":10,"process_name":"제선","attrdir_em":112.20,"cumulative_emission":0,"total_matdir_emission":112.20,"total_fueldir_emission":0},
    "242": {"id":242,"install_id":10,"process_name":"제강","attrdir_em":7190.21,"cumulative_emission":0}
  },
  "productsById": {
    "34": {"id":34,"product_name":"블룸","product_amount":150,"product_sell":0,"product_eusell":0,"attr_em":0,"preview_attr_em":0}
  },
  "edges": [
    {"id":1,"source_node_type":"process","source_id":241,"target_node_type":"process","target_id":242,"edge_kind":"continue"},
    {"id":2,"source_node_type":"process","source_id":242,"target_node_type":"product","target_id":34,"edge_kind":"produce"},
    {"id":3,"source_node_type":"product","source_id":34,"target_node_type":"process","target_id":300,"edge_kind":"consume"}
  ],
  "productProcess": [
    {"product_id":34,"process_id":300,"consumption_amount":0}
  ],
  "meta": {"version":1,"updated_at":"ISO-8601"}
}
```

설명
- `processesById[*].attrdir_em`: 공정 직접귀속배출량
- `processesById[*].cumulative_emission`: 전파 결과(누적)
- `productsById[*].attr_em`: 저장된 확정치(선택)
- `productsById[*].preview_attr_em`: 연결 상태 기준 프리뷰(표시용)
- `productProcess`: 제품→공정 consume에서 분배 비율 계산에 쓰이는 소비량
- `edges`: 모든 엣지(continue/produce/consume)

---

### 전파 규칙(서비스 로직을 로컬로 1:1 이식)
1) continue (공정→공정)
- `target.cumulative = source.cumulative_or_attrdir + target.attrdir`
- `source.cumulative_or_attrdir = (source.cumulative_emission || source.attrdir_em)`

2) produce (공정→제품, 표시용)
- `product.preview_attr_em = Σ(연결된 공정들의 cumulative)`
- 누적이 0이면 해당 공정의 `attrdir_em`으로 폴백
- 저장은 하지 않음(저장은 별도 버튼/엔드포인트로 처리 가능)

3) consume (제품→공정)
- 기초: `to_next_process = product_amount - product_sell - product_eusell`
- 분배: 소비량이 있으면 `consumption_amount / total_consumption`, 없으면 균등분배
- 비율: `process_ratio = (allocated_amount / product_amount)` (단, `product_amount <= 0`이면 위 분배비율을 그대로 사용)
- 귀속: `process_emission = product_emission * process_ratio`
- 누적: `target.cumulative += process_emission`

아이들포턴트 보장
- 전파 시작 전에 모든 `cumulative_emission`을 0으로 리셋하고 현재 엣지 기준으로 재계산한다.
- 엣지 삭제/수정/판매량 변경 후에도 항상 리셋→전파 순서를 따른다.

---

### 로컬 엔진 설계(순수 TS)
인터페이스
```ts
type NodeType = 'process' | 'product';
type EdgeKind = 'continue' | 'produce' | 'consume';

interface Process { id: number; install_id?: number; process_name?: string; attrdir_em: number; cumulative_emission: number; total_matdir_emission?: number; total_fueldir_emission?: number; }
interface Product { id: number; product_name?: string; product_amount: number; product_sell: number; product_eusell: number; attr_em: number; preview_attr_em: number; }
interface Edge { id: number; source_node_type: NodeType; source_id: number; target_node_type: NodeType; target_id: number; edge_kind: EdgeKind; }
interface ProductProcess { product_id: number; process_id: number; consumption_amount: number; }

interface GraphState {
  processesById: Record<number, Process>;
  productsById: Record<number, Product>;
  edges: Edge[];
  productProcess: ProductProcess[];
  meta: { version: number; updated_at: string };
}
```

헬퍼
```ts
const LS_KEY = 'cbam:graph:v1';
export function loadState(): GraphState { return JSON.parse(localStorage.getItem(LS_KEY) || '{"processesById":{},"productsById":{},"edges":[],"productProcess":[],"meta":{"version":1,"updated_at":""}}'); }
export function saveState(s: GraphState) { s.meta.updated_at = new Date().toISOString(); localStorage.setItem(LS_KEY, JSON.stringify(s)); }
```

전파 핵심 알고리즘
```ts
export function resetAllCumulative(s: GraphState) {
  Object.values(s.processesById).forEach(p => { p.cumulative_emission = 0; });
}

export function propagateContinue(s: GraphState) {
  const incomingMap = new Map<number, number>();
  s.edges.filter(e => e.edge_kind === 'continue').forEach(e => {
    incomingMap.set(e.target_id, (incomingMap.get(e.target_id) || 0) + 1);
    if (!incomingMap.has(e.source_id)) incomingMap.set(e.source_id, incomingMap.get(e.source_id) || 0);
  });
  const q: number[] = Array.from(incomingMap.entries()).filter(([, c]) => c === 0).map(([id]) => id);
  const push = (id: number) => { if (!q.includes(id)) q.push(id); };
  while (q.length) {
    const pid = q.shift()!;
    s.edges.filter(e => e.edge_kind === 'continue' && e.source_id === pid).forEach(e => {
      const src = s.processesById[e.source_id];
      const tgt = s.processesById[e.target_id];
      if (!src || !tgt) return;
      const sourceCum = src.cumulative_emission || src.attrdir_em || 0;
      const next = sourceCum + (tgt.attrdir_em || 0);
      tgt.cumulative_emission = next;
      push(e.target_id);
    });
  }
}

export function computeProductPreview(s: GraphState, productId: number) {
  const procs = s.edges.filter(e => e.edge_kind === 'produce' && e.target_id === productId).map(e => s.processesById[e.source_id]).filter(Boolean);
  const sum = procs.reduce((acc, p) => acc + (p.cumulative_emission || p.attrdir_em || 0), 0);
  const prod = s.productsById[productId];
  if (prod) prod.preview_attr_em = Number(sum.toFixed(8));
}

export function propagateConsume(s: GraphState) {
  const consumeEdges = s.edges.filter(e => e.edge_kind === 'consume');
  for (const e of consumeEdges) {
    const product = s.productsById[e.source_id];
    const target = s.processesById[e.target_id];
    if (!product || !target) continue;

    const toNext = (product.product_amount || 0) - (product.product_sell || 0) - (product.product_eusell || 0);
    const all = s.productProcess.filter(pp => pp.product_id === product.id);
    const me = all.find(pp => pp.process_id === target.id);
    const totalCons = all.reduce((acc, pp) => acc + (pp.consumption_amount || 0), 0);

    let allocated = 0; let ratio = 0;
    if (totalCons > 0) {
      ratio = (me?.consumption_amount || 0) / totalCons;
      allocated = toNext * ratio;
    } else {
      ratio = all.length > 0 ? 1 / all.length : 0;
      allocated = toNext * ratio;
    }

    const productEmission = s.productsById[product.id].preview_attr_em || s.productsById[product.id].attr_em || 0;
    const processRatio = (product.product_amount > 0) ? (allocated / product.product_amount) : ratio;
    const add = productEmission * processRatio;
    target.cumulative_emission += add;
  }
}

export function propagateFullGraph(s: GraphState) {
  resetAllCumulative(s);
  propagateContinue(s);
  propagateConsume(s);
  Object.keys(s.productsById).forEach(pid => computeProductPreview(s, Number(pid)));
}
```

트리거(이벤트) 설계
- `onEdgeAdded(edge)`: 상태에 추가 → `propagateFullGraph`
- `onEdgeDeleted(id)`: 삭제 → `propagateFullGraph`
- `onProcessAttrdirChanged(processId, attrdir)`: 값 갱신 → `propagateFullGraph`
- `onProductSalesSaved(productId, sell, eusell)`: 값 갱신 → `propagateFullGraph`
- 프런트로 브로드캐스트: `window.dispatchEvent(new CustomEvent('cbam:ls:updated', { detail: { changed: 'graph' } }))`

---

### 프론트 연동(핵심 포인트)
- `useProcessCanvas.ts`에서 현재 사용 중인 이벤트(`cbam:updateProductAmount`, `cbam:refreshProduct`)와 동일한 타이밍에 로컬 엔진을 호출하여 `propagateFullGraph` 수행 후, `refreshProcessEmission/refreshProductEmission` 대신 로컬 상태를 읽어 화면을 갱신한다.
- 제품 관리 모달 저장 버튼(`ProcessSelector.tsx`)에서 서버 저장 대신 로컬 모드 스위치를 제공(환경변수 또는 개발 토글).
- 엣지 생성/삭제 시 서버 호출 전/후 로컬 엔진도 동작시키는 이중 경로를 허용(오프라인 시 로컬만, 온라인 시 서버 우선 후 로컬 동기화).

샘플 UI 갱신 코드(로컬 모드)
```ts
// 제품 프리뷰 반영
const s = loadState();
const prod = s.productsById[productId];
updateProductNodeByProductId(productId, { attr_em: prod.preview_attr_em });

// 공정 누적 반영
const p = s.processesById[processId];
updateNodeData(processNodeId, { processData: { ...old, cumulative_emission: p.cumulative_emission, attr_em: p.attrdir_em } });
```

---

### 상태 변경 API(로컬)
```ts
export function addEdge(edge: Edge) { const s = loadState(); s.edges.push(edge); propagateFullGraph(s); saveState(s); broadcast(); }
export function deleteEdge(edgeId: number) { const s = loadState(); s.edges = s.edges.filter(e => e.id !== edgeId); propagateFullGraph(s); saveState(s); broadcast(); }
export function updateProcessAttrdir(processId: number, attrdir: number) { const s = loadState(); if (s.processesById[processId]) s.processesById[processId].attrdir_em = attrdir; propagateFullGraph(s); saveState(s); broadcast(); }
export function saveProductSales(productId: number, sell: number, eusell: number) { const s = loadState(); const p = s.productsById[productId]; if (p) { p.product_sell = sell; p.product_eusell = eusell; } propagateFullGraph(s); saveState(s); broadcast(); }
function broadcast(){ window.dispatchEvent(new CustomEvent('cbam:ls:updated', { detail: { changed: 'graph' } })); }
```

---

### 오프라인/온라인 동기화 전략(선택)
- 개발/테스트: 로컬 전용 모드(서버 호출 생략)
- 운영: 서버 성공 시 로컬에 미러링(읽기 성능/오프라인 복구용)
- 충돌 해결: 서버 타임스탬프가 최신이면 서버 → 로컬 덮어쓰기, 오프라인 변경분은 큐잉 후 재시도

---

### 수용 기준(테스트 시나리오)
1. 제선(112.20) → 제강(continue) → 제강 누적 = 112.20 + 제강 직접
2. 제강 → 블룸(produce) 연결 시 블룸 프리뷰 = Σ(연결 공정 누적)
3. 블룸(product_amount=150, sell=0, eusell=0), 압연 consume 연결 시 분배 비율/누적이 규칙대로 반영
4. 판매량 저장 후(예: sell=1, eusell=1) `propagateFullGraph`로 하류 공정/제품까지 갱신
5. 엣지 삭제 후 잔존 누적이 남지 않음(리셋→전파 수행 확인)

---

### 작업 순서 체크리스트
- [ ] `localStorage` 헬퍼/타입/전파 함수 추가(별도 모듈 `src/lib/localGraph.ts` 추천)
- [ ] 개발 토글 추가: `NEXT_PUBLIC_LOCAL_GRAPH=1`이면 로컬 모드 동작
- [ ] 엣지 생성/삭제/수정 시 로컬 엔진 연동
- [ ] 공정 투입/연료/원료 저장 시 `updateProcessAttrdir` → `propagateFullGraph`
- [ ] 제품 판매량 저장 시 `saveProductSales` → `propagateFullGraph`
- [ ] 화면 갱신: 공정 누적/제품 프리뷰를 로컬 상태로 반영하는 경로 추가
- [ ] 단위/시나리오 테스트 및 값 검증(위 수용 기준)

---

### 추가 노트
- 모든 합산/비율 계산은 부동소수 오차를 줄이기 위해 소수점 8자리 내로 반올림 후 저장을 권장한다.
- 대규모 그래프에서의 성능을 위해 `process_id → outgoing continue edges` 인덱스를 메모리에 캐시키고, 변경 시만 무효화한다.
- 제품 프리뷰는 실시간 표시 목적이므로 누적 계산 이후 마지막에 일괄 갱신한다.

---

### 완료 기준 메시지(커밋 템플릿)
```
feat(local-graph): 로컬 스토리지 기반 전파 엔진 도입
- reset→continue→consume→product preview 순 전파
- 엣지/공정/제품 판매량 변경 시 자동 재계산
- 프론트 캔버스와 이벤트 연동(cbam:ls:updated)
```


