# 한국어 번호판 인식기

한국어 자동차 번호판 검출 및 인식 시스템 (객체 검출 기반)

## 주요 기능

- 번호판 검출 및 원근 보정
- 객체 검출 기반 문자 검출
- GUI 애플리케이션

---

## Linux

### 릴리즈 다운로드 (권장)

```bash
# 다운로드 및 압축 해제
wget https://github.com/sauce-git/korean-license-plate-detector/releases/latest/download/korean-license-plate-detector-linux.tar.gz
tar -xzf korean-license-plate-detector-linux.tar.gz

# 실행
cd korean-license-plate-detector
./korean-license-plate-detector
```

### 소스에서 빌드

```bash
git clone https://github.com/sauce-git/korean-license-plate-detector.git
cd korean-license-plate-detector
make build
./dist/korean-license-plate-detector/korean-license-plate-detector
```

---

## Windows

### 릴리즈 다운로드 (권장)

```powershell
# 다운로드 및 압축 해제
# https://github.com/sauce-git/korean-license-plate-detector/releases/latest 에서
# korean-license-plate-detector-windows.zip 다운로드

# 압축 해제 후 실행
.\korean-license-plate-detector\korean-license-plate-detector.exe
```

### 소스에서 빌드 (WSL2)

```bash
git clone https://github.com/sauce-git/korean-license-plate-detector.git
cd korean-license-plate-detector
make build
# WSL2에서는 Windows .exe를 생성할 수 없음
```

**실제 Windows .exe가 필요하면 릴리즈를 사용하세요.**

---

## macOS

### 소스에서 빌드

```bash
git clone https://github.com/sauce-git/korean-license-plate-detector.git
cd korean-license-plate-detector
make build
./dist/korean-license-plate-detector/korean-license-plate-detector
```

> **macOS 릴리즈는 제공되지 않습니다.**

---

## 디버그 모드

```bash
# Linux/macOS
./korean-license-plate-detector --debug

# Windows
.\korean-license-plate-detector.exe --debug
```

로그: `~/.korean-license-plate-detector/app.log`

---

## 환경 변수

```bash
export HF_MODEL_REPO=sauce-hug/korean-license-plate-detector
export HF_MODEL_CACHE=.cache
make build
```

---

## 라이센스

Apache License 2.0
