# 🧩 Frontend Atomic Design Pattern

## 📁 폴더 구조

### **atoms/** - 원자 컴포넌트
가장 기본적인 UI 요소들 (버튼, 입력 필드, 아이콘 등)
- 재사용 가능한 최소 단위 컴포넌트
- 상태나 비즈니스 로직 없음
- 순수한 UI 표현만 담당

### **molecules/** - 분자 컴포넌트
atoms를 조합한 간단한 UI 블록 (폼 필드, 카드 등)
- 2-3개의 atoms로 구성
- 간단한 상태 관리
- 재사용 가능한 UI 블록

### **organisms/** - 유기체 컴포넌트
molecules와 atoms를 조합한 복잡한 UI 섹션 (헤더, 사이드바, 폼 등)
- 페이지의 주요 섹션을 구성
- 비즈니스 로직 포함 가능
- 독립적인 기능 단위

### **templates/** - 템플릿
organisms를 배치하는 페이지 레이아웃
- 페이지의 구조와 레이아웃 정의
- 실제 데이터나 상태 없음
- 재사용 가능한 페이지 구조

### **pages/** - 페이지
실제 데이터와 상태를 가진 완성된 페이지
- templates에 실제 데이터 주입
- 라우팅과 연결
- 비즈니스 로직 포함

## 🔄 마이그레이션 계획

1. **atoms/** - Button, Input, Icon 등 기본 컴포넌트
2. **molecules/** - FormField, Card, Modal 등
3. **organisms/** - Navigation, Footer, AuthForm 등
4. **templates/** - MainLayout, AuthLayout 등
5. **pages/** - 기존 app 폴더의 페이지들

## 📋 컴포넌트 분류 기준

- **atoms**: 1-2개의 props, 단순한 스타일링
- **molecules**: 3-5개의 props, 간단한 상태
- **organisms**: 5개 이상의 props, 복잡한 상태
- **templates**: 레이아웃과 구조만 담당
- **pages**: 실제 데이터와 비즈니스 로직
