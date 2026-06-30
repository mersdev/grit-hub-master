#!/usr/bin/env bash
set -euo pipefail

# setup-login.sh
# Prereq checks + guided PAT/SSO setup + proxy/GHE configuration.

MIN_NODE_MAJOR=16
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=10

GHE_LOGIN_URL="https://dhl.ghe.com/login"
GHE_TOKEN_URL="https://dhl.ghe.com/settings/tokens/new?scopes=repo&description=GRIT-Hub-Setup"
GHE_TOKEN_NEW_URL="https://dhl.ghe.com/settings/tokens"
GHE_ORG_SSO="SMP-Mobile-Customer-Data-Domai"

PROXY_URL="http://cloudproxy.dhl.com:10123"
NO_PROXY_PATTERN="*.dhl.com"
NO_PROXY_PATTERN_EXTRA="*.dhl1.com"
GHE_URI="https://dhl.ghe.com"
MODE="normal"
EFFECTIVE_GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
TOKEN_SOURCE="none"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { printf "%b\n" "${GREEN}[setup-login]${NC} $*"; }
warn() { printf "%b\n" "${YELLOW}[setup-login]${NC} $*"; }
err() { printf "%b\n" "${RED}[setup-login]${NC} $*"; }

has_cmd() { command -v "$1" >/dev/null 2>&1; }

win_path_to_posix() {
  # Convert "C:\Users\name\..." -> "/c/Users/name/..." in a bash-portable way.
  local p="$1"
  p="$(printf '%s' "$p" | sed 's#\\#/#g')"
  if [[ "$p" =~ ^([A-Za-z]):(.*)$ ]]; then
    local drive="${BASH_REMATCH[1]}"
    local rest="${BASH_REMATCH[2]}"
    drive="$(printf '%s' "$drive" | tr '[:upper:]' '[:lower:]')"
    printf '/%s%s' "$drive" "$rest"
  else
    printf '%s' "$p"
  fi
}

load_effective_token() {
  EFFECTIVE_GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
  TOKEN_SOURCE="none"

  if [ -n "${EFFECTIVE_GH_TOKEN:-}" ]; then
    TOKEN_SOURCE="environment"
    return 0
  fi

  # Fallback: read persisted Windows user env vars.
  if has_cmd cmd.exe; then
    local gh_win=""
    local github_win=""
    gh_win="$(cmd.exe /c "echo %GH_TOKEN%" 2>/dev/null | tr -d '\r' | tail -n1)"
    github_win="$(cmd.exe /c "echo %GITHUB_TOKEN%" 2>/dev/null | tr -d '\r' | tail -n1)"

    if [ -n "$gh_win" ] && [ "$gh_win" != "%GH_TOKEN%" ]; then
      EFFECTIVE_GH_TOKEN="$gh_win"
      TOKEN_SOURCE="persisted-windows-env"
      export GH_TOKEN="$EFFECTIVE_GH_TOKEN"
      export GITHUB_TOKEN="$EFFECTIVE_GH_TOKEN"
      return 0
    fi

    if [ -n "$github_win" ] && [ "$github_win" != "%GITHUB_TOKEN%" ]; then
      EFFECTIVE_GH_TOKEN="$github_win"
      TOKEN_SOURCE="persisted-windows-env"
      export GH_TOKEN="$EFFECTIVE_GH_TOKEN"
      export GITHUB_TOKEN="$EFFECTIVE_GH_TOKEN"
      return 0
    fi
  fi
}

usage() {
  cat <<EOF
Usage: $0 [normal|fresh-start|test]

Modes:
  normal       Default workflow. Uses existing GH_TOKEN/GITHUB_TOKEN if present.
               Writes http.noProxy with only: $NO_PROXY_PATTERN
  fresh-start  Always starts from PAT/SSO prompt and runs full setup.
               Writes http.noProxy with only: $NO_PROXY_PATTERN
  test         Always starts from PAT/SSO prompt and runs full setup.
               Writes http.noProxy with: $NO_PROXY_PATTERN and $NO_PROXY_PATTERN_EXTRA
EOF
}

parse_args() {
  if [ "$#" -gt 1 ]; then
    err "Too many arguments."
    usage
    exit 1
  fi

  if [ "$#" -eq 0 ]; then
    MODE="normal"
    return 0
  fi

  case "$1" in
    normal|fresh-start|test)
      MODE="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      err "Unknown mode: $1"
      usage
      exit 1
      ;;
  esac
}

ensure_windows_path() {
  # Some Windows-hosted bash runtimes start with an empty/incomplete PATH.
  local extra=""
  extra+="/c/Program Files/Git/cmd:/c/Program Files/Git/bin:"
  extra+="/c/Program Files/nodejs:/c/Windows/System32:/c/Windows"

  if [ -n "${PATH:-}" ]; then
    PATH="$PATH:$extra"
  else
    PATH="$extra"
  fi
  export PATH
}

open_url() {
  local url="$1"
  if has_cmd xdg-open; then
    xdg-open "$url" >/dev/null 2>&1 || true
  elif has_cmd open; then
    open "$url" >/dev/null 2>&1 || true
  elif has_cmd cmd.exe; then
    cmd.exe /c start "" "$url" >/dev/null 2>&1 || true
  else
    warn "Could not auto-open browser. Open manually: $url"
  fi
}

check_git() {
  if has_cmd git; then
    log "Git detected: $(git --version)"
    return 0
  fi

  if has_cmd git.exe; then
    git() { git.exe "$@"; }
    log "Git detected: $(git.exe --version)"
    return 0
  fi

  if [ -x "/c/Program Files/Git/cmd/git.exe" ]; then
    git() { "/c/Program Files/Git/cmd/git.exe" "$@"; }
    log "Git detected: $( "/c/Program Files/Git/cmd/git.exe" --version)"
    return 0
  fi

  if ! has_cmd git; then
    err "Git is not installed or not in PATH."
    return 1
  fi
}

check_node_npm() {
  if ! has_cmd node && has_cmd node.exe; then
    node() { node.exe "$@"; }
  fi
  if ! has_cmd npm && has_cmd npm.cmd; then
    npm() { npm.cmd "$@"; }
  fi

  if ! has_cmd node; then
    err "Node.js is not installed or not in PATH."
    return 1
  fi
  if ! has_cmd npm; then
    err "npm is not installed or not in PATH."
    return 1
  fi

  local node_version node_major
  node_version="$(node -v | sed 's/^v//')"
  node_major="${node_version%%.*}"
  if [ "$node_major" -lt "$MIN_NODE_MAJOR" ]; then
    err "Node.js $node_version detected. Require ${MIN_NODE_MAJOR}+"
    return 1
  fi

  log "Node.js detected: v$node_version"
  log "npm detected: $(npm -v)"
}

check_python() {
  local pycmd=""
  local pyargs=()

  if has_cmd py.exe && py.exe -3 -c "import sys" >/dev/null 2>&1; then
    pycmd="py.exe"
    pyargs=(-3)
  else
    for candidate in python3 python python.exe; do
      if has_cmd "$candidate" && "$candidate" -c "import sys" >/dev/null 2>&1; then
        pycmd="$candidate"
        break
      fi
    done
  fi

  if [ -z "$pycmd" ]; then
    warn "Python executable is not runnable in this shell. Continuing without Python check."
    return 0
  fi

  local pyver
  pyver="$("$pycmd" "${pyargs[@]}" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
PY
)"

  local major minor
  major="${pyver%%.*}"
  minor="$(printf '%s' "$pyver" | cut -d. -f2)"

  if [ "$major" -lt "$MIN_PYTHON_MAJOR" ] || { [ "$major" -eq "$MIN_PYTHON_MAJOR" ] && [ "$minor" -lt "$MIN_PYTHON_MINOR" ]; }; then
    err "Python $pyver detected. Require ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+"
    return 1
  fi

  log "Python detected: $pyver"
}

check_copilot() {
  if has_cmd copilot; then
    log "GitHub Copilot CLI detected: $(copilot --version 2>/dev/null | head -n1 || echo 'installed')"
  elif has_cmd copilot.exe; then
    log "GitHub Copilot CLI detected: $(copilot.exe --version 2>/dev/null | head -n1 || echo 'installed')"
  else
    warn "Could not verify GitHub Copilot CLI command."
    warn "Please ensure GitHub Copilot extension is installed and signed in (CLI/VS Code/IDE)."
  fi
}

prompt_pat_and_sso() {
  echo
  log "Opening DHL GHE login and token pages..."
  open_url "$GHE_LOGIN_URL"
  sleep 3
  open_url "$GHE_TOKEN_URL"

  cat <<EOF

Create or verify your PAT with these requirements:
1. Token page: $GHE_TOKEN_URL
2. Scope: full repo access (repo) [prefilled in URL]
3. Expiration: choose as needed in UI
4. Generate the token, then right-click in terminal to paste it when prompted.

EOF

  local pat
  while true; do
    read -r -p "Right-click to paste your PAT now (format ghp_xxx): " pat
    echo

    if [ -z "$pat" ]; then
      err "PAT cannot be empty. Please paste your token."
      continue
    fi

    if [[ ! "$pat" =~ ^ghp_[A-Za-z0-9]{36}$ ]]; then
      err "Invalid PAT format. Expected format like: ghp_****************************"
      continue
    fi

    break
  done

  EFFECTIVE_GH_TOKEN="$pat"
  TOKEN_SOURCE="prompted"
  export GH_TOKEN="$pat"
  export GITHUB_TOKEN="$pat"
  log "PAT captured for this shell session (GH_TOKEN/GITHUB_TOKEN)."

  log "Opening a new tab for SSO follow-up..."
  open_url "$GHE_TOKEN_NEW_URL"

  cat <<EOF

Now complete SSO authorization:
1. Click 'Configure SSO'
2. Authorize organization:
   $GHE_ORG_SSO

EOF

  read -r -p "Press Enter after SSO authorization is done... " _
}

persist_token_env() {
  if [ -z "${EFFECTIVE_GH_TOKEN:-}" ]; then
    warn "No token available to persist in environment variables."
    return 0
  fi

  log "Persisting GH_TOKEN/GITHUB_TOKEN for future sessions..."

  # Windows: persist at user scope via setx.
  if has_cmd setx.exe; then
    setx.exe GH_TOKEN "$EFFECTIVE_GH_TOKEN" >/dev/null || warn "Failed to persist GH_TOKEN with setx.exe."
    setx.exe GITHUB_TOKEN "$EFFECTIVE_GH_TOKEN" >/dev/null || warn "Failed to persist GITHUB_TOKEN with setx.exe."
    log "Persisted token via Windows user environment variables."
    return 0
  fi

  # POSIX fallback: write to shell profile for future shells.
  local profile_file="${HOME}/.bashrc"
  touch "$profile_file"
  awk '
    $0 !~ /^export GH_TOKEN=/ && $0 !~ /^export GITHUB_TOKEN=/ { print }
  ' "$profile_file" > "${profile_file}.tmp"
  mv "${profile_file}.tmp" "$profile_file"
  {
    printf 'export GH_TOKEN=%q\n' "$EFFECTIVE_GH_TOKEN"
    printf 'export GITHUB_TOKEN=%q\n' "$EFFECTIVE_GH_TOKEN"
  } >> "$profile_file"
  log "Persisted token in $profile_file."
}

set_proxy_for_git_npm() {
  log "Applying Git proxy settings..."
  git config --global http.proxy "$PROXY_URL"
  git config --global https.proxy "$PROXY_URL"

  log "Applying npm proxy settings..."
  npm config set proxy "$PROXY_URL" >/dev/null
  npm config set https-proxy "$PROXY_URL" >/dev/null

  log "Git and npm proxy configured."
}

update_vscode_settings() {
  if ! has_cmd node; then
    warn "Skipping VS Code settings update because Node.js is unavailable."
    return 0
  fi

  local settings_path=""
  local selected_no_proxy_extra=""
  local ldap_user="${USERNAME:-${USER:-}}"
  local appdata_posix="${APPDATA:-}"
  local userprofile_posix="${USERPROFILE:-}"
  local win_username=""
  local win_appdata=""
  local win_userprofile=""

  # Fallback for Git Bash/MSYS shells where USERNAME/APPDATA may be empty.
  if has_cmd cmd.exe; then
    win_username="$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r' | tail -n1)"
    win_appdata="$(cmd.exe /c "echo %APPDATA%" 2>/dev/null | tr -d '\r' | tail -n1)"
    win_userprofile="$(cmd.exe /c "echo %USERPROFILE%" 2>/dev/null | tr -d '\r' | tail -n1)"
    if [ -z "$ldap_user" ] || [ "$ldap_user" = "user" ]; then
      if [ -n "$win_username" ] && [ "$win_username" != "%USERNAME%" ]; then
        ldap_user="$win_username"
      fi
    fi
    if [ -z "$appdata_posix" ] && [ -n "$win_appdata" ] && [ "$win_appdata" != "%APPDATA%" ]; then
      appdata_posix="$win_appdata"
    fi
    if [ -z "$userprofile_posix" ] && [ -n "$win_userprofile" ] && [ "$win_userprofile" != "%USERPROFILE%" ]; then
      userprofile_posix="$win_userprofile"
    fi
  fi

  # Convert Windows-style env paths (e.g. C:\Users\name\AppData\Roaming) for bash tests.
  if [[ "$appdata_posix" == *\\* ]]; then
    if has_cmd cygpath; then
      appdata_posix="$(cygpath -u "$appdata_posix" 2>/dev/null || printf '%s' "$appdata_posix")"
    else
      appdata_posix="$(win_path_to_posix "$appdata_posix")"
    fi
  fi
  if [[ "$userprofile_posix" == *\\* ]]; then
    if has_cmd cygpath; then
      userprofile_posix="$(cygpath -u "$userprofile_posix" 2>/dev/null || printf '%s' "$userprofile_posix")"
    else
      userprofile_posix="$(win_path_to_posix "$userprofile_posix")"
    fi
  fi

  if [ -n "$ldap_user" ] && [ -d "/c/Users/${ldap_user}/AppData/Roaming/Code/User" ]; then
    settings_path="/c/Users/${ldap_user}/AppData/Roaming/Code/User/settings.json"
  elif [ -n "$ldap_user" ] && [ -d "/mnt/c/Users/${ldap_user}/AppData/Roaming/Code/User" ]; then
    settings_path="/mnt/c/Users/${ldap_user}/AppData/Roaming/Code/User/settings.json"
  elif [ -f "C:/Users/${ldap_user}/AppData/Roaming/Code/User/settings.json" ] || [ -d "C:/Users/${ldap_user}/AppData/Roaming/Code/User" ]; then
    settings_path="C:/Users/${ldap_user}/AppData/Roaming/Code/User/settings.json"
  elif [ -n "$userprofile_posix" ] && [ -d "$userprofile_posix/AppData/Roaming/Code/User" ]; then
    settings_path="$userprofile_posix/AppData/Roaming/Code/User/settings.json"
  elif [ -n "$appdata_posix" ] && [ -f "$appdata_posix/Code/User/settings.json" ]; then
    settings_path="$appdata_posix/Code/User/settings.json"
  elif [ -n "$appdata_posix" ] && [ -d "$appdata_posix/Code/User" ]; then
    settings_path="$appdata_posix/Code/User/settings.json"
  elif [ -f "$HOME/.config/Code/User/settings.json" ]; then
    settings_path="$HOME/.config/Code/User/settings.json"
  elif [ -d "$HOME/.config/Code/User" ]; then
    settings_path="$HOME/.config/Code/User/settings.json"
  elif [ -f "$HOME/Library/Application Support/Code/User/settings.json" ]; then
    settings_path="$HOME/Library/Application Support/Code/User/settings.json"
  elif [ -d "$HOME/Library/Application Support/Code/User" ]; then
    settings_path="$HOME/Library/Application Support/Code/User/settings.json"
  else
    warn "VS Code settings path not found. Skipping VS Code proxy/GHE config."
    return 0
  fi

  log "Updating VS Code settings: $settings_path"
  mkdir -p "$(dirname "$settings_path")"

  show_manual_vscode_settings_steps() {
    local manual_no_proxy="$NO_PROXY_PATTERN"
    if [ "$MODE" = "test" ]; then
      manual_no_proxy="${NO_PROXY_PATTERN}, ${NO_PROXY_PATTERN_EXTRA}"
    fi
    cat <<EOF

Manual action required: could not update VS Code settings automatically.
Open this file and update it manually:
  $settings_path

Add or update these keys in settings.json:
  "http.proxy": "$PROXY_URL"
  "http.noProxy": ["$NO_PROXY_PATTERN"$([ "$MODE" = "test" ] && printf ', "%s"' "$NO_PROXY_PATTERN_EXTRA")]
  "github-enterprise.uri": "$GHE_URI"

If token should be available in VS Code terminal, also set:
  "terminal.integrated.env.windows": { "GH_TOKEN": "<your-token>", "GITHUB_TOKEN": "<your-token>" }
  "terminal.integrated.env.linux": { "GH_TOKEN": "<your-token>", "GITHUB_TOKEN": "<your-token>" }
  "terminal.integrated.env.osx": { "GH_TOKEN": "<your-token>", "GITHUB_TOKEN": "<your-token>" }

Tip: if this is a permission issue, run VS Code once as Administrator, save settings, then reopen normally.
EOF
  }

  local node_settings_path="$settings_path"
  if has_cmd cygpath; then
    node_settings_path="$(cygpath -m "$settings_path" 2>/dev/null || printf '%s' "$settings_path")"
  elif [[ "$settings_path" =~ ^/mnt/([a-zA-Z])/(.*)$ ]]; then
    node_settings_path="$(printf '%s:/%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" | sed 's#\\#/#g')"
  elif [[ "$settings_path" =~ ^/([a-zA-Z])/(.*)$ ]]; then
    node_settings_path="$(printf '%s:/%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" | sed 's#\\#/#g')"
  fi

  if [ "$MODE" = "test" ]; then
    selected_no_proxy_extra="$NO_PROXY_PATTERN_EXTRA"
  fi

  if ! node - "$node_settings_path" "$PROXY_URL" "$NO_PROXY_PATTERN" "$selected_no_proxy_extra" "$GHE_URI" "${EFFECTIVE_GH_TOKEN:-}" <<'NODE'
const fs = require('fs');
const settingsPath = process.argv[2];
const proxy = process.argv[3];
const noProxy = process.argv[4];
const noProxyExtra = process.argv[5];
const gheUri = process.argv[6];
const ghToken = process.argv[7] || '';

if (!settingsPath || typeof settingsPath !== 'string') {
  throw new Error('Missing settings path argument');
}

let json = {};
if (fs.existsSync(settingsPath)) {
  try {
    const raw = fs.readFileSync(settingsPath, 'utf8').trim();
    if (raw) {
      try {
        json = JSON.parse(raw);
      } catch {
        // VS Code settings can be JSONC (comments/trailing commas). Fallback to JS object parse.
        json = Function('"use strict"; return (' + raw + ');')();
      }
    }
  } catch {
    throw new Error('settings.json is not valid JSON: ' + settingsPath);
  }
}

json['http.proxy'] = proxy;
const desiredNoProxy = [noProxy, noProxyExtra].filter(Boolean);
json['http.noProxy'] = Array.isArray(json['http.noProxy'])
  ? Array.from(new Set([...json['http.noProxy'], ...desiredNoProxy]))
  : desiredNoProxy;
json['github-enterprise.uri'] = gheUri;

if (ghToken) {
  json['terminal.integrated.env.windows'] = json['terminal.integrated.env.windows'] || {};
  json['terminal.integrated.env.linux'] = json['terminal.integrated.env.linux'] || {};
  json['terminal.integrated.env.osx'] = json['terminal.integrated.env.osx'] || {};

  json['terminal.integrated.env.windows']['GH_TOKEN'] = ghToken;
  json['terminal.integrated.env.windows']['GITHUB_TOKEN'] = ghToken;
  json['terminal.integrated.env.linux']['GH_TOKEN'] = ghToken;
  json['terminal.integrated.env.linux']['GITHUB_TOKEN'] = ghToken;
  json['terminal.integrated.env.osx']['GH_TOKEN'] = ghToken;
  json['terminal.integrated.env.osx']['GITHUB_TOKEN'] = ghToken;
}

fs.writeFileSync(settingsPath, JSON.stringify(json, null, 2) + '\n');
NODE
  then
    warn "Automatic VS Code settings update failed (likely permission denied on settings.json)."
    show_manual_vscode_settings_steps
    return 0
  fi

  log "VS Code proxy/GHE settings updated."
}

main() {
  parse_args "$@"
  ensure_windows_path
  load_effective_token
  log "Running mode: $MODE"
  log "Checking prerequisites..."
  check_git
  check_node_npm
  check_python
  check_copilot

  if [ "$MODE" = "fresh-start" ] || [ "$MODE" = "test" ]; then
    warn "Mode '$MODE': running PAT/SSO flow from the start."
    prompt_pat_and_sso
  elif [ -n "${EFFECTIVE_GH_TOKEN:-}" ]; then
    log "Found GH_TOKEN/GITHUB_TOKEN in environment. Skipping PAT prompt."
  else
    prompt_pat_and_sso
  fi

  persist_token_env
  set_proxy_for_git_npm
  update_vscode_settings

  cat <<EOF

Done. Summary:
- Verified: Git, Node.js 16+, npm, Python 3.10+
- Mode: $MODE
- Token source: $TOKEN_SOURCE
- Applied proxy:
  - Git: http.proxy + https.proxy = $PROXY_URL
  - npm: proxy + https-proxy = $PROXY_URL
- VS Code: http.proxy=$PROXY_URL, http.noProxy includes $NO_PROXY_PATTERN$([ "$MODE" = "test" ] && printf ' and %s' "$NO_PROXY_PATTERN_EXTRA")
- Set VS Code GHE URI: github-enterprise.uri = $GHE_URI

If VS Code was open, reload window for settings to take effect.
EOF
}

main "$@"
