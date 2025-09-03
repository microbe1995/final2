네, `calculation/`, `fueldir/`, `matdir/` 도메인들 간의 관계를 분석해드리겠습니다. 먼저 각 도메인의 구조와 역할을 파악해보겠습니다.


[7 tools called]

이제 `calculation/`, `fueldir/`, `matdir/` 도메인들 간의 관계를 명확하게 설명드리겠습니다.

## 🔗 **도메인 간 관계 분석**

### **1. 전체 아키텍처 구조**

```
📊 CBAM 배출량 계산 시스템
├── �� matdir/ (원료직접배출량)
├── ⛽ fueldir/ (연료직접배출량)
└── �� calculation/ (집계 및 최종 계산)
```

### **2. 각 도메인의 역할**

#### **🏭 matdir/ (원료직접배출량)**
- **목적**: 원료 투입에 따른 직접 배출량 계산
- **계산 공식**: `원료직접배출량 = 투입량 × 배출계수 × 산화계수`
- **데이터 소스**: Material Master (원료 마스터 데이터)
- **주요 기능**:
  - 원료별 개별 배출량 계산
  - Material Master와 연동하여 배출계수 자동 조회
  - 공정별 원료 투입량 관리

#### **⛽ fueldir/ (연료직접배출량)**
- **목적**: 연료 소비에 따른 직접 배출량 계산
- **계산 공식**: `연료직접배출량 = 소비량 × 배출계수 × 산화계수`
- **데이터 소스**: Fuel Master (연료 마스터 데이터)
- **주요 기능**:
  - 연료별 개별 배출량 계산
  - Fuel Master와 연동하여 배출계수 자동 조회
  - 공정별 연료 소비량 관리

#### **�� calculation/ (집계 및 최종 계산)**
- **목적**: 개별 배출량들을 집계하여 공정/제품별 총 배출량 계산
- **계산 공식**: `총 직접귀속배출량 = Σ원료직접배출량 + Σ연료직접배출량`
- **데이터 소스**: matdir, fueldir 테이블의 집계 결과
- **주요 기능**:
  - 공정별 직접귀속배출량 집계
  - 제품별 총 배출량 계산
  - 배출량 통계 및 요약

### **3. 데이터 흐름 및 의존성**

```
🔄 데이터 흐름 순서:

1️⃣ matdir/fueldir에서 개별 배출량 계산
   ↓
2️⃣ calculation에서 집계하여 총 배출량 계산
   ↓
3️⃣ process_attrdir_emission 테이블에 저장
```

#### **🔍 구체적인 의존성**

**calculation 도메인이 matdir/fueldir에 의존하는 부분:**

```python
# calculation_repository.py의 calculate_process_attrdir_emission 메서드

# 2. 원료별 직접배출량 계산 (matdir 테이블 기반)
matdir_emission = await conn.fetchrow("""
    SELECT COALESCE(SUM(matdir_em), 0) as total_matdir_emission
    FROM matdir
    WHERE process_id = $1
""", process_id)

# 3. 연료별 직접배출량 계산 (fueldir 테이블 기반)
fueldir_emission = await conn.fetchrow("""
    SELECT COALESCE(SUM(fueldir_em), 0) as total_fueldir_emission
    FROM fueldir
    WHERE process_id = $1
""", process_id)

# 4. 총 직접귀속배출량 계산
total_matdir = float(matdir_emission['total_matdir_emission']) if matdir_emission else 0.0
total_fueldir = float(fueldir_emission['total_fueldir_emission']) if fueldir_emission else 0.0
attrdir_em = total_matdir + total_fueldir
```

### **4. InputManager.tsx에서의 활용**

프론트엔드에서 이 관계가 어떻게 활용되는지:

```typescript
// 1. 개별 배출량 계산 (matdir/fueldir)
const calculateMatdirEmission = async () => {
  const response = await axiosClient.post(apiEndpoints.cbam.matdir.calculate, {
    mat_amount: matdirForm.amount,
    mat_factor: matdirForm.factor,
    oxyfactor: matdirForm.oxyfactor
  });
};

// 2. 자동 집계 (calculation)
const saveAllData = async () => {
  // ... 데이터 저장 후
  
  // 자동 집계: 해당 공정의 직접귀속배출량 계산
  try {
    const aggregationResponse = await axiosClient.post(
      apiEndpoints.cbam.calculation.process.attrdir(selectedProcess.id)
    );
    console.log('✅ 자동 집계 성공:', aggregationResponse.data);
  } catch (aggregationError: any) {
    console.warn('⚠️ 자동 집계 실패:', aggregationError);
  }
};
```

### **5. 핵심 관계 요약**

| 관계 유형 | 설명 | 예시 |
|-----------|------|------|
| **데이터 의존성** | calculation이 matdir/fueldir 데이터를 읽어서 집계 | `SELECT SUM(matdir_em) FROM matdir` |
| **계산 순서** | 1단계: 개별 배출량 → 2단계: 총 배출량 집계 | matdir + fueldir → attrdir |
| **API 호출 순서** | matdir/fueldir 계산 → calculation 집계 | `/matdir/calculate` → `/calculation/process/{id}/attrdir` |
| **데이터 일관성** | matdir/fueldir 변경 시 calculation 재계산 필요 | 원료/연료 추가/수정 시 자동 집계 트리거 |

### **6. 비즈니스 로직 관점**

- **matdir/fueldir**: "개별 투입물의 배출량은 얼마인가?"
- **calculation**: "이 공정의 총 배출량은 얼마인가?"
- **최종 목표**: CBAM 신고를 위한 공정별 총 탄소 배출량 산출

이 구조는 **계층적 계산 모델**을 구현하여, 개별 요소의 배출량을 먼저 계산하고, 이를 집계하여 최종 결과를 도출하는 체계적인 접근 방식을 제공합니다.