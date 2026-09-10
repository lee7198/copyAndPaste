# UI/UX Design System Specification (DESIGN.md)

## 1. Visual Identity & Concept

### 1.1 Core Concept
* **Glassmorphism & Layering:** 반투명 유리 질감과 백그라운드 블러(Frosted Glass Effect)를 활용해 배경과 콘텐츠 레이어 간 시각적 깊이감 형성
* **Floating Card Layout:** 모든 모듈 및 데이터 영역은 공중에 떠 있는 둥근 단독 카드 형태(`Border Radius`)로 구성
* **Non-Native Custom UI:** Windows OS 기본 위젯 스타일을 배제하고, 라운드와 캡슐(Pill) 형태의 커스텀 위젯 스펙 일과 적용

### 1.2 Shadow & Depth (Elevation)
* **Floating Surface Shadow:** `Blur Radius: 24px`, `Y-Offset: 8px`, `Color: rgba(0, 0, 0, 0.18)`
* **Sub-Component Shadow:** `Blur Radius: 12px`, `Y-Offset: 4px`, `Color: rgba(0, 0, 0, 0.08)`

---

## 2. Color System & Themes

### 2.1 Color Palette Table

| Role | Dark Mode Spec | Light Mode Spec |
| :--- | :--- | :--- |
| **Window Backdrop** | `rgba(18, 18, 20, 0.65)` + OS Blur | `rgba(240, 240, 243, 0.65)` + OS Blur |
| **Card Surface** | `rgba(255, 255, 255, 0.07)` | `rgba(255, 255, 255, 0.75)` |
| **Card Border** | `1px solid rgba(255, 255, 255, 0.12)` | `1px solid rgba(0, 0, 0, 0.06)` |
| **Input Background** | `rgba(255, 255, 255, 0.05)` | `rgba(0, 0, 0, 0.03)` |
| **Text - Primary** | `#FFFFFF` | `#111111` |
| **Text - Secondary** | `rgba(255, 255, 255, 0.60)` | `rgba(0, 0, 0, 0.55)` |
| **Accent / Active Pill** | `#FFFFFF` (Text: `#000000`) | `#111111` (Text: `#FFFFFF`) |
| **Focus / Highlight Border**| `rgba(255, 255, 255, 0.35)` | `rgba(0, 0, 0, 0.25)` |

---

## 3. Custom Component Guidelines

### 3.1 Input Fields
* **Shape:** `border-radius: 12px ~ 16px` (네모난 기본 윈도우 인풋 금지)
* **Border:** 기본 테두리 제거(`none`), Focus 시 세련된 Accent Border 활성화
* **Padding:** `top/bottom: 10px`, `left/right: 16px`

### 3.2 Pill Buttons & Navigation Tabs
* **Shape:** 완전히 둥근 캡슐 형태 (`border-radius: 999px` 또는 높이의 50%)
* **Active State:** 반전 컬러(Solid Black/White) 적용으로 현재 위치 명확히 표시
* **Inactive State:** 은은한 반투명 배경 및 hover 시 투명도 증가 애니메이션

### 3.3 Modern Toggle Switches
* **Shape:** 캡슐형 트랙 내 내부 원형 썸(Thumb) 이동 구조
* **Animation:** Smooth Easing 0.2초 트랜지션 적용
* **State Colors:** Off State(`rgba(255, 255, 255, 0.1)`), On State(`Accent Color`)

### 3.4 Data & Calendar Cards
* **Numeric Metrics:** 수치 데이터는 대형 Bold Typography로 강조, 서브 텍스트는 상단에 위성 배열
* **Mini Calendar Grid:** 여백이 넓은 미니멀 숫자 그리드, 선택된 날짜는 원형 Solid 배경으로 강조

---

## 4. Layout Rules & Typography

### 4.1 Typography Scale
* **Large Metric / Display:** `32px ~ 42px`, Bold
* **Header / Section Title:** `18px ~ 22px`, Semi-Bold
* **Body Text:** `13px ~ 15px`, Regular
* **Caption / Label:** `11px ~ 12px`, Regular (Secondary Alpha)

### 4.2 Layout Grid & Corner System
* **Window Outer Corner:** `border-radius: 20px` (프레임리스 투명 영역 적용)
* **Card Corner Radius:** `16px ~ 24px`
* **Card Gap & Margin:** 컴포넌트 간 간격 최소 `12px ~ 16px` 유지
