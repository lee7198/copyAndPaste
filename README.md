# Copy & Paste

자주 쓰는 텍스트를 저장하고, 클릭 한 번으로 원문을 복사하는 Windows 앱입니다.

## 실행

Python 3.11 이상에서 기존 가상환경의 의존성을 업데이트하세요.

```powershell
python -m pip install -r requirements.txt
python main.py
```

기존 `data.json` 경로와 키·값·글꼴 필드는 유지합니다. UI 렌더러는 wxPython에서
PySide6(Qt)로 변경했습니다. 이전 실행 파일은 다시 빌드해야 합니다.

```powershell
python -m pip install pyinstaller
python -m PyInstaller main.spec
```

SVG 아이콘은 실행 파일에 포함됩니다. Qt 배포 시 LGPL 등 PySide6 배포 라이선스 조건을 확인하세요.

## 화면과 사용법

- 창 전체 배경은 알파 투명도로 그립니다. 카드·입력칸도 반투명이며 텍스트와 아이콘은 선명하게 유지합니다.
- 제목과 설정·최소화·최대화·닫기 버튼은 창 상단에 직접 배치합니다.
- 개수 표시, 표의 열 헤더, 반복 안내 및 중첩 패널을 제거했습니다.
- 항목 클릭 또는 키보드 Enter로 원문 복사 및 편집. 추가/새 항목/저장/삭제와 입력칸 Enter 저장을 지원합니다.
- 제목을 드래그하여 이동, 더블 클릭하여 최대화/복원합니다. 모서리나 우하단 그립으로 크기를 조절합니다.
- 설정은 같은 창에서 열립니다. 취소 또는 Esc로 복귀하며 편집 중인 텍스트는 보존합니다.

## 배경 설정

설정에서 시스템/라이트/다크 테마, 블러 효과, 배경 불투명도(20–90%)를 선택합니다.
불투명도를 낮추면 실제 데스크톱이 더 많이 비칩니다. 블러 끄기는 불투명 배경입니다.
글자까지 흐려지는 창 전체 opacity나 단순 회색 색상 조절을 사용하지 않습니다.

Windows 10 1809 이상에서 선택적 네이티브 blur/acrylic 효과를 호출합니다.
이 효과는 안정적인 공개 계약이 아닌 `SetWindowCompositionAttribute` API를 사용하므로
OS·그래픽 환경에 따라 지원되지 않을 수 있습니다. 미지원 시 콘텐츠를 숨기지 않고
알파 투명도만 유지합니다. 블러 반경 자체는 Windows가 관리합니다.
실제 Windows 배경 합성은 로컬 데스크톱에서 최종 확인해야 합니다.

설정 파일은 `%APPDATA%/CopyAndPaste/appearance.json`에 저장합니다.
이전 Mica 설정은 부드러운 블러로 변환되며, 기존 패널 농도 설정 대신 새 배경 불투명도 52%로 시작합니다.

## 아이콘 교체

`assets/icons/`의 SVG를 교체하면 됩니다. 24×24 viewBox, 단색 `currentColor`를 사용하면
라이트/다크 테마 색상을 자동 적용합니다. 아이콘명은 settings, minimize, maximize,
restore, close, plus입니다. PNG를 사용할 경우 `icons.py` 로더에 해당 파일 매핑을 추가합니다.

## 검증

```powershell
python -m unittest discover -s tests -p "test_*.py"
python tests/windows_smoke.py
```

Windows smoke는 실제 Qt 위젯, 클립보드 원문, CRUD, 설정 저장/취소,
최소 크기 및 렌더링된 픽셀의 배경 알파·제목 표시를 검사합니다.
Windows 자체 배경 블러 외관은 픽셀 알파 검사와 별개입니다.
Linux에서는 `QT_QPA_PLATFORM=offscreen`으로 렌더러 검사를 실행할 수 있습니다.
