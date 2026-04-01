# 한국어 번호판 인식기

한국어 자동차 번호판 검출 및 인식 시스템 (ONNX Runtime 기반)

## 주요 기능

- **번호판 검출** - 차량 이미지에서 번호판 영역 검출
- **원근 보정** - 번호판 모서리 검출 및 이미지 변형 보정
- **문자 검출** - 한글 및 숫자 문자 검출 (YOLO 기반)
- **GUI 애플리케이션** - 사용하기 쉬운 데스크톱 인터페이스

## 동작 원리

1. **번호판 검출** - YOLO 모델이 차량 이미지에서 번호판 영역을 검출
2. **모서리 검출** - 번호판의 4개 모서리 좌표 검출
3. **원근 변환** - 기울어지거나 각도가 있는 번호판 이미지 보정
4. **문자 검출** - 각 문자를 개별 객체로 검출하여 클래스 분류
5. **문자 정렬** - 기하학적 분석을 통한 문자 순서 정렬

### YOLO 기반 문자 검출을 사용하는 이유

전통적인 OCR 대신 YOLO 기반 문자 검출 방식을 사용합니다:

- **불분명한 번호판** - 조명, 그림자, 날씨 등으로 흐릿한 번호판에서도 개별 문자 검출 가능
- **찌그러진 번호판** - 사고로 변형된 번호판에서 문자 간격이 불규칙해도 각 문자를 독립적으로 검출
- **부분 가려짐** - 일부 문자가 가려진 경우에도 보이는 문자만 검출하여 결과 반환

## 릴리즈 다운로드 (권장)

[최신 릴리즈](https://github.com/sauce-git/korean-license-plate-detector/releases/latest)에서 다운로드하세요.

- **Linux**: `korean-license-plate-detector-linux.tar.gz`
- **Windows**: `korean-license-plate-detector-windows.zip`

> **macOS**: macOS 릴리즈는 제공되지 않습니다. 소스에서 직접 빌드하세요.

### Linux/Windows 사용법

압축 해제 후 실행 파일을 바로 사용할 수 있습니다.

```bash
# Linux
./korean-license-plate-detector/korean-license-plate-detector

# Windows
korean-license-plate-detector\korean-license-plate-detector.exe
```

### 디버그 모드

```bash
# Linux
./korean-license-plate-detector/korean-license-plate-detector --debug

# Windows
korean-license-plate-detector\korean-license-plate-detector.exe --debug
```

로그는 `~/.korean-license-plate-detector/app.log`에 저장됩니다.

### macOS 사용법 (소스 빌드)

```bash
# 저장소 클론
git clone https://github.com/sauce-git/korean-license-plate-detector.git
cd korean-license-plate-detector

# 의존성 설치
make install

# 빌드 및 실행
make build
./dist/korean-license-plate-detector/korean-license-plate-detector
```

### 릴리즈 다운로드

릴리즈는 현재 제공되지 않습니다. 소스에서 직접 빌드하여 사용하세요.

## 빌드

### Linux / macOS

```bash
make build
```

빌드된 실행 파일은 작성한 컴퓨터에서만 실행 가능합니다. 다른 사용자가 실행하려면 각 플랫폼에 맞는 빌드가 필요합니다.

### Windows

WSL2 또는 Linux 환경에서 빌드하세요:

```bash
make build
```

빌드된 실행 파일은 `dist/korean-license-plate-detector/`에 생성됩니다.

## 설정

| 환경 변수 | 설명 | 기본값 |
|----------|------|--------|
| `HF_MODEL_REPO` | Hugging Face 모델 저장소 | `sauce-hug/korean-license-plate-detector` |
| `HF_MODEL_CACHE` | 로컬 캐시 디렉토리 | `.cache` |

```bash
export HF_MODEL_REPO=sauce-hug/korean-license-plate-detector
make build
```

## 모델

모델은 Hugging Face에서 자동으로 다운로드됩니다:

- **plate_detect_v1** - 번호판 검출
- **vertex_detect_v1** - 모서리 검출
- **syllable_detect_v1** - 문자 검출

모델 저장소: [sauce-hug/korean-license-plate-detector](https://huggingface.co/sauce-hug/korean-license-plate-detector)

## 라이센스

Apache License 2.0. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
