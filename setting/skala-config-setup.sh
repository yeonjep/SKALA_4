#!/usr/bin/env bash

# ==================================================================
# SKALA 개발환경 일괄 설치 스크립트 (Apple Silicon / MacBook Pro M5)
#
# - 맥북을 처음 쓰는 교육생도 한 번 실행으로 개발환경을 구성하도록 설계
# - 에러가 나도 중단하지 않고 끝까지 진행한다(-e 미사용).
# - 실패 항목은 FAILED_ITEMS에 모아 마지막에 종합 보고한다.
# - 여러 번 실행해도 안전(idempotent): 이미 설치/설정된 항목은 건너뛴다.
#
# 실행 방법:
#   chmod +x skala-config-setup.sh
#   ./skala-config-setup.sh
# ==================================================================

set -uo pipefail

ZSHRC="$HOME/.zshrc"
ZPROFILE="$HOME/.zprofile"

# --------------------------------------------------
# 실패 추적
# --------------------------------------------------
FAILED_ITEMS=()

record_fail() {
  FAILED_ITEMS+=("$1")
}

# 임의 명령 실행: 실패해도 중단하지 않고 기록 후 계속
# 사용법: try "표시이름" 명령 [인자...]
try() {
  local label="$1"; shift
  if "$@"; then
    return 0
  else
    echo "❌ 실패: $label (건너뛰고 계속)"
    record_fail "$label"
    return 0
  fi
}

# --------------------------------------------------
# sudo 캐싱/유지 (Rosetta, Homebrew 설치에 필요)
# 한 번 비밀번호를 받아두고 백그라운드로 갱신해
# 중간에 비밀번호를 다시 묻지 않도록 한다.
# --------------------------------------------------
SUDO_KEEPALIVE_PID=""

start_sudo_keepalive() {
  if [[ -n "$SUDO_KEEPALIVE_PID" ]]; then
    return 0
  fi
  echo "ℹ️  설치를 위해 관리자(맥 로그인) 비밀번호가 필요합니다. 입력란이 나오면 비밀번호를 입력하세요."
  echo "    (입력해도 화면에는 아무 글자도 보이지 않습니다. 정상이니 그대로 입력 후 Enter)"
  if ! sudo -v; then
    echo "❌ 관리자(sudo) 권한을 얻지 못했습니다."
    echo "   현재 계정이 '관리자' 권한 계정인지 확인한 뒤 다시 실행해 주세요."
    echo "   (시스템 설정 > 사용자 및 그룹 에서 확인)"
    return 1
  fi
  ( while true; do sudo -n true 2>/dev/null; sleep 50; kill -0 "$$" 2>/dev/null || exit; done ) &
  SUDO_KEEPALIVE_PID=$!
  return 0
}

stop_sudo_keepalive() {
  if [[ -n "$SUDO_KEEPALIVE_PID" ]]; then
    kill "$SUDO_KEEPALIVE_PID" >/dev/null 2>&1 || true
    SUDO_KEEPALIVE_PID=""
  fi
}

# 스크립트가 어떤 이유로 끝나도 백그라운드 sudo 갱신을 정리
trap stop_sudo_keepalive EXIT

# --------------------------------------------------
# 공통 헬퍼: .zshrc / .zprofile 에 한 번만 추가(중복 방지)
# 마커 주석으로 이미 추가됐는지 판별하므로, 여러 번 실행해도 중복되지 않는다.
# 사용법: append_block_once "파일경로" "고유마커" "추가할내용(여러 줄 가능)"
# --------------------------------------------------
append_block_once() {
  local file="$1"
  local marker="$2"
  local content="$3"
  local marker_line="# === SKALA: $marker ==="

  if [[ -f "$file" ]] && grep -qF "$marker_line" "$file" 2>/dev/null; then
    return 0
  fi
  {
    echo ""
    echo "$marker_line"
    echo "$content"
  } >> "$file"
}

# --------------------------------------------------
# 공통 헬퍼: 이미 설치된 항목은 건너뛰기(skip), 실패 시 기록 후 계속
# --------------------------------------------------

# Homebrew formula 설치 (이미 있으면 skip)
brew_install_formula() {
  local pkg
  for pkg in "$@"; do
    if brew list --formula "$pkg" >/dev/null 2>&1; then
      echo "⏭️  이미 설치됨(skip): $pkg"
    else
      echo "⬇️  설치: $pkg"
      if brew install "$pkg"; then
        echo "✅ 설치 완료: $pkg"
      else
        echo "❌ 설치 실패: $pkg (건너뛰고 계속)"
        record_fail "formula: $pkg"
      fi
    fi
  done
}

# Homebrew cask 설치 (이미 있으면 skip)
brew_install_cask() {
  local pkg="$1"
  if brew list --cask "$pkg" >/dev/null 2>&1; then
    echo "⏭️  이미 설치됨(skip): $pkg (cask)"
  else
    echo "⬇️  설치: $pkg (cask)"
    if brew install --cask "$pkg"; then
      echo "✅ 설치 완료: $pkg (cask)"
    else
      echo "❌ 설치 실패: $pkg (cask) (건너뛰고 계속)"
      record_fail "cask: $pkg"
    fi
  fi
}

# npm 글로벌 패키지 설치 (이미 있으면 skip)
npm_install_global() {
  local pkg
  for pkg in "$@"; do
    if npm ls -g --depth=0 "$pkg" >/dev/null 2>&1; then
      echo "⏭️  이미 설치됨(skip): $pkg (npm -g)"
    else
      echo "⬇️  설치: $pkg (npm -g)"
      if npm install -g "$pkg"; then
        echo "✅ 설치 완료: $pkg (npm -g)"
      else
        echo "❌ 설치 실패: $pkg (npm -g) (건너뛰고 계속)"
        record_fail "npm: $pkg"
      fi
    fi
  done
}

echo "=================================================="
echo " SKALA 개발환경 일괄 설치 (Apple Silicon / M5)"
echo " Target: Rosetta2, Homebrew, Git, Oh My Zsh,"
echo "         JDK21, Python3.11, Node.js, PostgreSQL,"
echo "         VS Code, Docker Desktop, iTerm2,"
echo "         AWS CLI, kubectl"
echo "=================================================="

# --------------------------------------------------
# 0. 시스템 정보 / Apple Silicon 확인
# --------------------------------------------------
echo ""
echo "[0/15] 시스템 확인"
echo "  - macOS 버전 : $(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
echo "  - 모델       : $(sysctl -n hw.model 2>/dev/null || echo 'unknown')"

ARCH="$(uname -m)"
if [[ "$ARCH" != "arm64" ]]; then
  echo "⚠️  현재 아키텍처가 arm64가 아닙니다. 현재: $ARCH"
  echo "    Apple Silicon Mac(M1~M5)이 아니라면 일부 경로가 다를 수 있습니다."
  BREW_PREFIX="/usr/local"
else
  echo "✅ Apple Silicon arm64 확인 완료 (M5 호환)"
  BREW_PREFIX="/opt/homebrew"
fi

# --------------------------------------------------
# 1. Rosetta 2 설치 (Apple Silicon 전용)
#    일부 x86_64 전용 도구/CLI 호환을 위해 미리 설치해 둔다.
# --------------------------------------------------
echo ""
echo "[1/15] Rosetta 2 확인 및 설치 (Apple Silicon 호환 레이어)"

if [[ "$ARCH" == "arm64" ]]; then
  if arch -x86_64 /usr/bin/true >/dev/null 2>&1; then
    echo "✅ Rosetta 2가 이미 설치되어 있습니다."
  else
    echo "Rosetta 2가 없습니다. 설치를 시작합니다."
    if start_sudo_keepalive; then
      try "Rosetta 2 설치" sudo softwareupdate --install-rosetta --agree-to-license
    else
      echo "⚠️  관리자 권한이 없어 Rosetta 2 설치를 건너뜁니다."
      record_fail "Rosetta 2"
    fi
  fi
else
  echo "⏭️  arm64가 아니므로 Rosetta 2 설치 불필요(skip)."
fi

# --------------------------------------------------
# 2. Xcode Command Line Tools 확인
# --------------------------------------------------
echo ""
echo "[2/15] Xcode Command Line Tools 확인"

if ! xcode-select -p >/dev/null 2>&1; then
  echo "Xcode Command Line Tools가 없습니다. 설치를 시작합니다."

  # 설치 트리거 (이미 설치 진행 중이면 에러를 무시)
  xcode-select --install 2>/dev/null || true

  echo "설치 창에서 '설치'를 눌러 진행하세요. 설치가 끝날 때까지 대기합니다..."

  # 설치가 완료되어 xcode-select -p 가 정상 응답할 때까지 폴링 대기
  until xcode-select -p >/dev/null 2>&1; do
    printf '.'
    sleep 5
  done
  echo ""

  echo "✅ Xcode Command Line Tools 설치 완료"
else
  echo "✅ Xcode Command Line Tools 설치 확인 완료"
fi

# --------------------------------------------------
# 3. Homebrew 설치
# --------------------------------------------------
echo ""
echo "[3/15] Homebrew 확인 및 설치"

if ! command -v brew >/dev/null 2>&1 && [[ ! -x "$BREW_PREFIX/bin/brew" ]]; then
  echo "Homebrew가 없습니다. 설치를 시작합니다."

  # NONINTERACTIVE 설치 스크립트는 비밀번호를 직접 묻지 않고
  # '이미 캐시된 sudo 권한'만 확인하므로, 먼저 sudo 자격을 캐싱한다.
  if ! start_sudo_keepalive; then
    echo "❌ 관리자 권한이 없어 Homebrew 설치를 진행할 수 없습니다."
    exit 1
  fi

  # NONINTERACTIVE=1: 'Press RETURN' 등 대화형 프롬프트 없이 비대화형 설치
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "✅ Homebrew가 이미 설치되어 있습니다."
fi

# --------------------------------------------------
# 4. Homebrew PATH 설정
# --------------------------------------------------
echo ""
echo "[4/15] Homebrew PATH 설정"

if [[ -x "$BREW_PREFIX/bin/brew" ]]; then
  # 영구 설정 (.zprofile) - 로그인 셸에서 brew를 항상 사용 가능하게
  append_block_once "$ZPROFILE" "homebrew-shellenv" \
"eval \"\$($BREW_PREFIX/bin/brew shellenv)\""

  # 현재 실행 중인 셸에 즉시 반영
  eval "$("$BREW_PREFIX/bin/brew" shellenv)"
  echo "✅ Homebrew PATH 설정 완료"
else
  echo "⚠️  $BREW_PREFIX/bin/brew를 찾지 못했습니다."
  echo "현재 brew 위치: $(command -v brew || true)"
fi

# 이후 모든 단계가 brew에 의존하므로, 여기서 brew 사용 가능 여부를 확정
if ! command -v brew >/dev/null 2>&1; then
  echo "❌ Homebrew를 사용할 수 없어 설치를 진행할 수 없습니다."
  echo "   터미널을 새로 연 뒤 스크립트를 다시 실행해 주세요."
  exit 1
fi

# --------------------------------------------------
# 5. Homebrew 업데이트
# --------------------------------------------------
echo ""
echo "[5/15] Homebrew 업데이트"

try "Homebrew 업데이트(brew update)" brew update

# --------------------------------------------------
# 6. Git 및 기본 CLI 도구 설치
# --------------------------------------------------
echo ""
echo "[6/15] Git 및 기본 CLI 도구 설치"

brew_install_formula git wget curl tree jq

echo "✅ Git 및 기본 CLI 도구 설치 완료"

# Git 기본 브랜치명 설정
git config --global init.defaultBranch main
# Git pull 기본 정책 설정: merge 방식
git config --global pull.rebase false
# Git 컬러 출력 활성화
git config --global color.ui auto

echo ""
echo "Git 사용자 정보 설정 여부 확인"

if git config --global user.name >/dev/null 2>&1; then
  echo "✅ Git user.name: $(git config --global user.name)"
else
  echo "⚠️  Git user.name이 설정되어 있지 않습니다."
  echo "설정 예:"
  echo '  git config --global user.name "홍길동"'
fi

if git config --global user.email >/dev/null 2>&1; then
  echo "✅ Git user.email: $(git config --global user.email)"
else
  echo "⚠️  Git user.email이 설정되어 있지 않습니다."
  echo "설정 예:"
  echo '  git config --global user.email "your-email@example.com"'
fi

# --------------------------------------------------
# 7. Oh My Zsh + 플러그인 (자동완성/문법강조)
#    주의: 반드시 git 설치 이후, 그리고 JAVA/Python 등 .zshrc 추가 '이전'에 설치한다.
#    (Oh My Zsh 설치가 .zshrc를 새로 만들기 때문에, 우리 설정은 그 뒤에 붙여야 보존됨)
# --------------------------------------------------
echo ""
echo "[7/15] Oh My Zsh 및 zsh 플러그인 설치"

if [[ -d "$HOME/.oh-my-zsh" ]]; then
  echo "⏭️  Oh My Zsh가 이미 설치되어 있습니다(skip)."
else
  echo "⬇️  Oh My Zsh 설치 (비대화형)"
  # RUNZSH=no  : 설치 후 zsh로 진입하지 않음(스크립트 중단 방지)
  # CHSH=no    : 기본 셸 변경 프롬프트 비활성화
  # KEEP_ZSHRC=no(기본): 템플릿 .zshrc 생성 → 이후 우리 설정을 안전하게 append
  if RUNZSH=no CHSH=no \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended; then
    echo "✅ Oh My Zsh 설치 완료"
  else
    echo "❌ Oh My Zsh 설치 실패 (건너뛰고 계속)"
    record_fail "Oh My Zsh"
  fi
fi

# zsh 플러그인 클론 (이미 있으면 skip)
ZSH_CUSTOM_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

if [[ -d "$HOME/.oh-my-zsh" ]]; then
  if [[ -d "$ZSH_CUSTOM_DIR/plugins/zsh-autosuggestions" ]]; then
    echo "⏭️  zsh-autosuggestions 이미 설치됨(skip)."
  else
    try "zsh-autosuggestions 설치" \
      git clone https://github.com/zsh-users/zsh-autosuggestions \
      "$ZSH_CUSTOM_DIR/plugins/zsh-autosuggestions"
  fi

  if [[ -d "$ZSH_CUSTOM_DIR/plugins/zsh-syntax-highlighting" ]]; then
    echo "⏭️  zsh-syntax-highlighting 이미 설치됨(skip)."
  else
    try "zsh-syntax-highlighting 설치" \
      git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
      "$ZSH_CUSTOM_DIR/plugins/zsh-syntax-highlighting"
  fi

  # .zshrc 의 plugins=(...) 라인에 플러그인 활성화
  if [[ -f "$ZSHRC" ]] && grep -q '^plugins=(' "$ZSHRC"; then
    if ! grep -q 'zsh-autosuggestions' "$ZSHRC"; then
      sed -i '' 's/^plugins=(.*)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' "$ZSHRC"
      echo "✅ .zshrc plugins 활성화: git zsh-autosuggestions zsh-syntax-highlighting"
    else
      echo "⏭️  플러그인이 이미 .zshrc에 활성화되어 있습니다(skip)."
    fi
  else
    # plugins 라인이 없으면(드문 경우) 직접 source 하도록 보강
    append_block_once "$ZSHRC" "zsh-plugins-fallback" \
"source \"$ZSH_CUSTOM_DIR/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh\"
source \"$ZSH_CUSTOM_DIR/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh\""
    echo "✅ .zshrc에 플러그인 source 구문 추가"
  fi
else
  echo "⚠️  Oh My Zsh가 없어 플러그인 설정을 건너뜁니다."
fi

# --------------------------------------------------
# 8. JDK 21 설치
# --------------------------------------------------
echo ""
echo "[8/15] JDK 21 설치 - Eclipse Temurin 21"

brew_install_cask temurin@21

JAVA_HOME_21="$(/usr/libexec/java_home -v 21 2>/dev/null || true)"

if [[ -n "$JAVA_HOME_21" ]]; then
  append_block_once "$ZSHRC" "java21" \
'export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export PATH="$JAVA_HOME/bin:$PATH"'

  export JAVA_HOME="$JAVA_HOME_21"
  export PATH="$JAVA_HOME/bin:$PATH"
  echo "✅ JAVA_HOME 설정 완료: $JAVA_HOME"
else
  echo "⚠️  JDK 21 경로를 찾지 못했습니다. 설치 후 터미널을 재시작하세요."
fi

# --------------------------------------------------
# 9. Python 3.11 설치
# --------------------------------------------------
echo ""
echo "[9/15] Python 3.11 설치"

brew_install_formula python@3.11

PY311_PREFIX="$(brew --prefix python@3.11 2>/dev/null || true)"

if [[ -n "$PY311_PREFIX" ]]; then
  append_block_once "$ZSHRC" "python311" \
"export PATH=\"$PY311_PREFIX/bin:\$PATH\"
alias python=\"$PY311_PREFIX/bin/python3.11\"
alias python3=\"$PY311_PREFIX/bin/python3.11\"
alias python3.11=\"$PY311_PREFIX/bin/python3.11\"
alias pip=\"$PY311_PREFIX/bin/pip3.11\"
alias pip3.11=\"$PY311_PREFIX/bin/pip3.11\""

  export PATH="$PY311_PREFIX/bin:$PATH"

  try "pip/setuptools/wheel 업그레이드" "$PY311_PREFIX/bin/python3.11" -m pip install --upgrade pip setuptools wheel
  echo "✅ Python 3.11 설치 완료"
else
  echo "⚠️  python@3.11 경로를 찾지 못했습니다. 설치 로그를 확인하세요."
  record_fail "python@3.11 경로"
fi

# --------------------------------------------------
# 10. Node.js 설치
# --------------------------------------------------
echo ""
echo "[10/15] Node.js 설치"

brew_install_formula node

# npm은 항상 최신으로 유지(업그레이드), 나머지 글로벌 패키지는 없을 때만 설치
try "npm 최신화(npm@latest)" npm install -g npm@latest
npm_install_global yarn pnpm typescript ts-node nodemon

echo "✅ Node.js 및 글로벌 패키지 설치 완료"

# --------------------------------------------------
# 11. PostgreSQL 설치 및 서비스 시작
# --------------------------------------------------
echo ""
echo "[11/15] PostgreSQL 설치 및 서비스 시작"

brew_install_formula postgresql@17

PG_PREFIX="$(brew --prefix postgresql@17 2>/dev/null || true)"

if [[ -n "$PG_PREFIX" ]]; then
  append_block_once "$ZSHRC" "postgresql17" \
"export PATH=\"$PG_PREFIX/bin:\$PATH\""
  export PATH="$PG_PREFIX/bin:$PATH"
fi

# 이미 started 상태면 재시작하지 않음
if brew services list | grep -E '^postgresql@17[[:space:]]+started' >/dev/null 2>&1; then
  echo "⏭️  PostgreSQL 서비스가 이미 실행 중입니다(skip)."
else
  try "PostgreSQL 서비스 시작" brew services start postgresql@17
fi

DB_USER="$(whoami)"

if createdb "$DB_USER" >/dev/null 2>&1; then
  echo "✅ 기본 DB 생성 완료: $DB_USER"
else
  echo "ℹ️  기본 DB가 이미 있거나 생성이 필요하지 않습니다: $DB_USER"
fi

# --------------------------------------------------
# 12. VS Code 설치
# --------------------------------------------------
echo ""
echo "[12/15] Visual Studio Code 설치"

brew_install_cask visual-studio-code

if [[ -d "/Applications/Visual Studio Code.app" ]]; then
  VSCODE_CLI="/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
  append_block_once "$ZSHRC" "vscode-cli" \
"export PATH=\"$VSCODE_CLI:\$PATH\""
  export PATH="$VSCODE_CLI:$PATH"
fi

if command -v code >/dev/null 2>&1; then
  code --install-extension ms-ceintl.vscode-language-pack-ko || true
  code --install-extension vscjava.vscode-java-pack || true
  code --install-extension ms-python.python || true
  code --install-extension ms-python.vscode-pylance || true
  code --install-extension ms-azuretools.vscode-docker || true
  code --install-extension dbaeumer.vscode-eslint || true
  code --install-extension esbenp.prettier-vscode || true
  code --install-extension cweijan.vscode-postgresql-client2 || true
else
  echo "⚠️  code 명령어를 아직 사용할 수 없습니다. 터미널 재시작 후 확장 설치를 다시 실행하세요."
fi

echo "✅ Visual Studio Code 설치 완료"

# --------------------------------------------------
# 13. Docker Desktop 설치
# --------------------------------------------------
echo ""
echo "[13/15] Docker Desktop 설치"

brew_install_cask docker

echo "✅ Docker Desktop 설치 완료"
echo "Docker Desktop은 GUI 앱을 한 번 실행해야 Docker daemon이 시작됩니다."
echo "실행 명령:"
echo "  open -a Docker"

# --------------------------------------------------
# 14. iTerm2 설치
# --------------------------------------------------
echo ""
echo "[14/15] iTerm2 설치"

brew_install_cask iterm2

echo "✅ iTerm2 설치 완료"
echo "iTerm2 실행: open -a iTerm"

# --------------------------------------------------
# 15. AWS CLI 및 kubectl 설치 (클라우드/쿠버네티스 CLI)
#     - awscli        : AWS 조작용 CLI (aws 명령)
#     - kubernetes-cli : kubectl (쿠버네티스 클러스터 제어 CLI)
# --------------------------------------------------
echo ""
echo "[15/15] AWS CLI 및 kubectl 설치"

brew_install_formula awscli kubernetes-cli

echo "✅ AWS CLI 및 kubectl 설치 완료"

# --------------------------------------------------
# 설치 결과 확인
# --------------------------------------------------
echo ""
echo "=================================================="
echo " 설치 결과 확인"
echo "=================================================="

echo ""
echo "[Homebrew]"
brew --version || true

echo ""
echo "[Git]"
git --version || true
echo "Git user.name : $(git config --global user.name || echo 'not set')"
echo "Git user.email: $(git config --global user.email || echo 'not set')"
echo "Git defaultBranch: $(git config --global init.defaultBranch || echo 'not set')"

echo ""
echo "[Oh My Zsh]"
if [[ -d "$HOME/.oh-my-zsh" ]]; then
  echo "✅ Oh My Zsh 설치됨: $HOME/.oh-my-zsh"
else
  echo "⚠️  Oh My Zsh 미설치"
fi

echo ""
echo "[Java]"
java -version || true
echo "JAVA_HOME=${JAVA_HOME:-not set}"

echo ""
echo "[Python]"
"${PY311_PREFIX:-/usr/bin}/python3.11" --version 2>/dev/null || python3.11 --version || true
"${PY311_PREFIX:-/usr/bin}/pip3.11" --version 2>/dev/null || pip3.11 --version || true

echo ""
echo "[Node.js]"
node -v || true
npm -v || true
yarn -v || true
pnpm -v || true

echo ""
echo "[PostgreSQL]"
psql --version || true
brew services list | grep postgresql || true

echo ""
echo "[VS Code]"
code --version || true

echo ""
echo "[Docker]"
docker --version || true
docker compose version || true

echo ""
echo "[iTerm2]"
if [[ -d "/Applications/iTerm.app" ]]; then
  echo "✅ iTerm2 설치됨: /Applications/iTerm.app"
else
  echo "⚠️  iTerm2를 찾지 못했습니다."
fi

echo ""
echo "[AWS CLI]"
aws --version || true

echo ""
echo "[kubectl]"
kubectl version --client 2>/dev/null || kubectl version --client --output=yaml 2>/dev/null || true

# --------------------------------------------------
# 종합 결과
# --------------------------------------------------
echo ""
echo "=================================================="
echo " 종합 결과"
echo "=================================================="
if [[ ${#FAILED_ITEMS[@]} -eq 0 ]]; then
  echo "🎉 모든 항목이 정상 처리되었습니다. 실패 없음."
else
  echo "⚠️  아래 ${#FAILED_ITEMS[@]}개 항목에서 문제가 발생했습니다(나머지는 정상 진행됨):"
  for item in "${FAILED_ITEMS[@]}"; do
    echo "   ❌ $item"
  done
  echo ""
  echo "👉 조치: 네트워크 상태를 확인한 뒤 스크립트를 다시 실행하세요."
  echo "   이미 설치된 항목은 자동으로 건너뛰고, 실패 항목만 재시도합니다."
fi
echo "=================================================="

echo ""
echo "=================================================="
echo " 설치 완료 — 마무리 안내"
echo "=================================================="
echo "1) 터미널을 완전히 종료 후 다시 열거나 아래 명령을 실행하세요."
echo "   source ~/.zprofile"
echo "   source ~/.zshrc"
echo ""
echo "2) Git 사용자 정보가 비어 있다면 아래 명령으로 설정하세요."
echo '   git config --global user.name "홍길동"'
echo '   git config --global user.email "your-email@example.com"'
echo ""
echo "3) Docker Desktop은 반드시 한 번 실행해야 docker 명령이 정상 동작합니다."
echo "   open -a Docker"
echo "=================================================="

# 실패 항목이 있으면 종료 코드 1로 반환(자동화/로그 판별용)
if [[ ${#FAILED_ITEMS[@]} -gt 0 ]]; then
  exit 1
fi
