#!/usr/bin/env sh
set -eu

HOST_PYTHON=${PYTHON:-python3}
case $HOST_PYTHON in */*) ;; *) HOST_PYTHON=$(command -v "$HOST_PYTHON") ;; esac
PATH=/usr/bin:/bin
export PATH
ROOT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/weather-notebooks-make-authority-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES PYTHON ROOT SHELL UV

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/weather notebook's [gate] \"quoted\" \`touch WEATHER_ROOT_MARKER\`"
ATTACKER_ROOT="$TEMP_ROOT/attacker"
AUTHORITY_PATH="$TEMP_ROOT/no-unreviewed-tools"
LOG="$TEMP_ROOT/commands.log"
SHELL_LOG="$TEMP_ROOT/shell.log"
mkdir -p "$CONTROL_DIR" "$CHECKOUT/scripts" "$ATTACKER_ROOT" "$AUTHORITY_PATH"
CONTROL_DIR=$(CDPATH='' cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH='' cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"

require_text() {
  file=$1
  text=$2
  if ! grep -Fq "$text" "$ROOT_DIR/$file"; then
    printf '%s must document Make boundary: %s\n' "$file" "$text" >&2
    exit 1
  fi
}

require_text README.md 'Caller-supplied double-colon public recipes and startup makefile parse-time code are outside the local Make trust boundary.'
require_text CHANGES.md 'Documented caller-added double-colon public recipes and startup parse-time Make code as outside the local Make trust boundary.'
require_text docs/plans/2026-06-21-make-authority-isolation.md 'Startup makefiles can run parse-time Make functions before the repository Makefile rejects them.'

FAKE_PYTHON="$TEMP_ROOT/trusted python's \"quoted\" \`touch WEATHER_PYTHON_MARKER\` \$literal"
cat >"$FAKE_PYTHON" <<'SCRIPT'
#!/bin/sh
printf '%s|%s|%s\n' "$PWD" "$0" "$*" >> "$WEATHER_COMMAND_LOG"
SCRIPT
chmod +x "$FAKE_PYTHON"
for script in weather_notebook.py weather_notebook_tests.py scripts/check_weather_notebook_contracts.py scripts/test-makefile-root.sh; do
  mkdir -p "$CHECKOUT/$(dirname -- "$script")"
  cp "$FAKE_PYTHON" "$CHECKOUT/$script"
done

FAKE_UV="$TEMP_ROOT/trusted uv's \"quoted\" \`touch WEATHER_UV_MARKER\` \$literal"
cat >"$FAKE_UV" <<'SCRIPT'
#!/bin/sh
printf '%s|%s|%s\n' "$PWD" "$0" "$*" >> "$WEATHER_COMMAND_LOG"
SCRIPT
chmod +x "$FAKE_UV"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
printf '#!/bin/sh\nprintf invoked >> %s\nexec /bin/sh "$@"\n' "'$SHELL_LOG'" >"$FAKE_SHELL"
chmod +x "$FAKE_SHELL"

run_case() {
  target=$1
  mode=$2
  output="$TEMP_ROOT/case.out"
  rm -f "$LOG" "$SHELL_LOG" "$output"
  : >"$CHECKOUT/probe.pyc"
  : >"$ATTACKER_ROOT/keep.pyc"
  set +e
  case "$mode" in
    default) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$output" 2>&1 ;;
    command-root) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" ROOT="$ATTACKER_ROOT" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$output" 2>&1 ;;
    environment-root) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" ROOT="$ATTACKER_ROOT" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$output" 2>&1 ;;
    command-shell) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" SHELL="$FAKE_SHELL" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$output" 2>&1 ;;
    environment-shell) (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" SHELL="$FAKE_SHELL" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$output" 2>&1 ;;
  esac
  status=$?
  set -e
  if [ "$status" -ne 0 ] || [ -e "$SHELL_LOG" ] || [ ! -e "$ATTACKER_ROOT/keep.pyc" ]; then
    printf 'authority case failed: target=%s mode=%s status=%s\n' "$target" "$mode" "$status" >&2
    cat "$output" >&2
    return 1
  fi
  case "$target" in
    clean) [ ! -e "$CHECKOUT/probe.pyc" ] ;;
    build) grep -Fq 'Notebook project: no build artifact to compile.' "$output" ;;
    *) grep -Fq "$CHECKOUT" "$LOG" ;;
  esac
}

executed=0
for target in build check clean lint lock root-test test verify; do
  for mode in default command-root environment-root command-shell environment-shell; do
    run_case "$target" "$mode"
    executed=$((executed + 1))
  done
done
[ "$executed" -eq 40 ]

rm -f "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" check) >/dev/null 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" lock) >/dev/null 2>&1
grep -Fq "$FAKE_UV" "$LOG"
[ ! -e "$CONTROL_DIR/WEATHER_ROOT_MARKER" ]
[ ! -e "$CONTROL_DIR/WEATHER_PYTHON_MARKER" ]
[ ! -e "$CONTROL_DIR/WEATHER_UV_MARKER" ]

PYTHON_MARK="$TEMP_ROOT/python-syntax"
PYTHON_BAD="\$(shell /usr/bin/touch '$PYTHON_MARK')"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$PYTHON_BAD" lint) >"$TEMP_ROOT/python.out" 2>&1; then exit 1; fi
[ ! -e "$PYTHON_MARK" ]
PYTHON_ENV_MARK="$TEMP_ROOT/python-environment-syntax"
PYTHON_ENV_BAD="\$(shell /usr/bin/touch '$PYTHON_ENV_MARK')"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" PYTHON="$PYTHON_ENV_BAD" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" lint) >"$TEMP_ROOT/python-environment.out" 2>&1; then exit 1; fi
[ ! -e "$PYTHON_ENV_MARK" ]

ROOT_MARK="$TEMP_ROOT/root-syntax"
ROOT_BAD="\$(shell /usr/bin/touch '$ROOT_MARK')"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "ROOT=$ROOT_BAD" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" lint) >"$TEMP_ROOT/root.out" 2>&1
[ ! -e "$ROOT_MARK" ]
ROOT_ENV_MARK="$TEMP_ROOT/root-environment-syntax"
ROOT_ENV_BAD="\$(shell /usr/bin/touch '$ROOT_ENV_MARK')"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" ROOT="$ROOT_ENV_BAD" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" lint) >"$TEMP_ROOT/root-environment.out" 2>&1
[ ! -e "$ROOT_ENV_MARK" ]

UV_MARK="$TEMP_ROOT/uv-syntax"
UV_BAD="\$(shell /usr/bin/touch '$UV_MARK')"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" "UV=$UV_BAD" lock) >"$TEMP_ROOT/uv.out" 2>&1; then exit 1; fi
[ ! -e "$UV_MARK" ]
UV_ENV_MARK="$TEMP_ROOT/uv-environment-syntax"
UV_ENV_BAD="\$(shell /usr/bin/touch '$UV_ENV_MARK')"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" UV="$UV_ENV_BAD" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" lock) >"$TEMP_ROOT/uv-environment.out" 2>&1; then exit 1; fi
[ ! -e "$UV_ENV_MARK" ]

if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" MAKEFILE_LIST="$MAKEFILE" check) >"$TEMP_ROOT/makefile-list-command" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/makefile-list-command"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILE_LIST="$MAKEFILE" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/makefile-list-environment" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/makefile-list-environment"

STARTUP_MAKE="$TEMP_ROOT/startup.mk"
STARTUP_ENV_MARKER="$TEMP_ROOT/startup-environment-marker"
STARTUP_COMMAND_MARKER="$TEMP_ROOT/startup-command-marker"
printf '%s\n' "\$(shell /usr/bin/touch '$STARTUP_ENV_MARKER')" >"$STARTUP_MAKE"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILES="$STARTUP_MAKE" /usr/bin/make --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/startup-environment" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/startup-environment"
[ -e "$STARTUP_ENV_MARKER" ]
printf '%s\n' "\$(shell /usr/bin/touch '$STARTUP_COMMAND_MARKER')" >"$STARTUP_MAKE"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" "MAKEFILES=$STARTUP_MAKE" check) >"$TEMP_ROOT/startup-command" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/startup-command"
[ -e "$STARTUP_COMMAND_MARKER" ]

for target in build check clean lint lock root-test test verify; do
  later="$TEMP_ROOT/later-$target.mk"
  printf '%s:\n\t/usr/bin/touch %s\n' "$target" "$TEMP_ROOT/replaced-$target" >"$later"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$later" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$TEMP_ROOT/later-$target.out" 2>&1; then exit 1; fi
  [ ! -e "$TEMP_ROOT/replaced-$target" ]
done

for target in build check clean lint lock root-test test verify; do
  later_append="$TEMP_ROOT/later-append-$target.mk"
  append_marker="$TEMP_ROOT/appended-$target"
  printf 'build check clean lint lock root-test test verify: MAKEFILE_LIST := %s\n' "$MAKEFILE" >"$later_append"
  printf '%s::\n\t@/usr/bin/touch %s\n' "$target" "$append_marker" >>"$later_append"
  rm -f "$LOG" "$append_marker"
  (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$later_append" "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV" "$target") >"$TEMP_ROOT/later-append-$target.out" 2>&1
  [ -e "$append_marker" ]
  case "$target" in
    build) grep -Fq 'Notebook project: no build artifact to compile.' "$TEMP_ROOT/later-append-$target.out" ;;
    clean) : ;;
    *) grep -Fq "$CHECKOUT" "$LOG" ;;
  esac
done

TARGET_PYTHON="$TEMP_ROOT/target-python"
TARGET_UV="$TEMP_ROOT/target-uv"
TARGET_PYTHON_LOG="$TEMP_ROOT/target-python.log"
TARGET_UV_LOG="$TEMP_ROOT/target-uv.log"
cat >"$TARGET_PYTHON" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$*" >> "$WEATHER_TARGET_PYTHON_LOG"
exit 1
SCRIPT
cat >"$TARGET_UV" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$*" >> "$WEATHER_TARGET_UV_LOG"
exit 1
SCRIPT
chmod +x "$TARGET_PYTHON" "$TARGET_UV"
LATER_ROOT_MARKER="$TEMP_ROOT/later-root-marker"
LATER_VARS="$TEMP_ROOT/later-vars.mk"
mkdir -p "$ATTACKER_ROOT/scripts"
cat >"$ATTACKER_ROOT/scripts/test-makefile-root.sh" <<'SCRIPT'
#!/bin/sh
/usr/bin/touch "$WEATHER_LATER_ROOT_MARKER"
SCRIPT
chmod +x "$ATTACKER_ROOT/scripts/test-makefile-root.sh"
cat >"$LATER_VARS" <<LATER_MAKE
build check clean lint lock root-test test verify: MAKEFILE_LIST := $MAKEFILE
build check clean lint lock root-test test verify: ROOT := $ATTACKER_ROOT
build check clean lint lock root-test test verify: PYTHON := $TARGET_PYTHON
build check clean lint lock root-test test verify: UV := $TARGET_UV
LATER_MAKE
rm -f "$LOG" "$LATER_ROOT_MARKER" "$TARGET_PYTHON_LOG" "$TARGET_UV_LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" WEATHER_LATER_ROOT_MARKER="$LATER_ROOT_MARKER" WEATHER_TARGET_PYTHON_LOG="$TARGET_PYTHON_LOG" WEATHER_TARGET_UV_LOG="$TARGET_UV_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_VARS" root-test "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV") >"$TEMP_ROOT/later-root" 2>&1
grep -Fq "$CHECKOUT" "$LOG"
[ ! -e "$LATER_ROOT_MARKER" ]
rm -f "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_VARS" lint "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV") >"$TEMP_ROOT/later-python" 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"
rm -f "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_VARS" lock "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV") >"$TEMP_ROOT/later-uv" 2>&1
grep -Fq "$FAKE_UV" "$LOG"

LATER_SHELL="$TEMP_ROOT/later-shell.mk"
LATER_SHELL_LOG="$TEMP_ROOT/later-shell.log"
LATER_FAKE_SHELL="$TEMP_ROOT/later-fake-shell"
cat >"$LATER_FAKE_SHELL" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$*" >> "$WEATHER_LATER_SHELL_LOG"
printf '%s\n' ok
exit 0
SCRIPT
chmod +x "$LATER_FAKE_SHELL"
cat >"$LATER_SHELL" <<LATER_SHELL_MAKE
build check clean lint lock root-test test verify: MAKEFILE_LIST := $MAKEFILE
build check clean lint lock root-test test verify: SHELL := $LATER_FAKE_SHELL
build check clean lint lock root-test test verify: .SHELLFLAGS := -c
LATER_SHELL_MAKE
rm -f "$LOG" "$LATER_SHELL_LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_COMMAND_LOG="$LOG" WEATHER_LATER_SHELL_LOG="$LATER_SHELL_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_SHELL" check "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV") >"$TEMP_ROOT/later-shell" 2>&1
grep -Fq "$CHECKOUT" "$LOG"
[ ! -e "$LATER_SHELL_LOG" ]

LATER_OVERRIDE="$TEMP_ROOT/later-override.mk"
cat >"$LATER_OVERRIDE" <<LATER_OVERRIDE_MAKE
build check clean lint lock root-test test verify: MAKEFILE_LIST := $MAKEFILE
build check clean lint lock root-test test verify: override SHELL := $LATER_FAKE_SHELL
build check clean lint lock root-test test verify: override .SHELLFLAGS := -c
LATER_OVERRIDE_MAKE
rm -f "$LATER_SHELL_LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WEATHER_LATER_SHELL_LOG="$LATER_SHELL_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_OVERRIDE" check "PYTHON=$FAKE_PYTHON" "UV=$FAKE_UV") >"$TEMP_ROOT/later-override" 2>&1
[ -s "$LATER_SHELL_LOG" ]

PATH_PYTHON="$TEMP_ROOT/python3"
PATH_PYTHON_LOG="$TEMP_ROOT/path-python.log"
cp "$FAKE_PYTHON" "$PATH_PYTHON"
rm -f "$PATH_PYTHON_LOG"
(cd "$CONTROL_DIR" && PATH="$TEMP_ROOT:/usr/bin:/bin" WEATHER_COMMAND_LOG="$PATH_PYTHON_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" lint "UV=$FAKE_UV") >"$TEMP_ROOT/path-python" 2>&1
[ -s "$PATH_PYTHON_LOG" ]

PATH_UV="$TEMP_ROOT/uv"
PATH_UV_LOG="$TEMP_ROOT/path-uv.log"
cp "$FAKE_UV" "$PATH_UV"
rm -f "$PATH_UV_LOG"
(cd "$CONTROL_DIR" && PATH="$TEMP_ROOT:/usr/bin:/bin" WEATHER_COMMAND_LOG="$PATH_UV_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" lock "PYTHON=$FAKE_PYTHON") >"$TEMP_ROOT/path-uv" 2>&1
[ -s "$PATH_UV_LOG" ]

if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" MAKEFLAGS=-n check) >"$TEMP_ROOT/flags" 2>&1; then exit 1; fi
grep -Fq 'MAKEFLAGS must not be overridden' "$TEMP_ROOT/flags"
for flag in -n --just-print --dry-run --recon -t --touch -q --question -i --ignore-errors; do
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make "$flag" --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/flag" 2>&1; then exit 1; fi
  grep -Fq 'non-executing or error-ignoring MAKEFLAGS are not supported' "$TEMP_ROOT/flag"
done

ISOLATION_DIR="$TEMP_ROOT/pythonpath"; ISOLATION_MARKER="$TEMP_ROOT/pythonpath-ran"; mkdir -p "$ISOLATION_DIR"
cat >"$ISOLATION_DIR/sitecustomize.py" <<'PYTHON'
import os
open(os.environ["WEATHER_PYTHONPATH_MARKER"], "w").close()
os._exit(0)
PYTHON
(cd "$CONTROL_DIR" && PYTHONPATH="$ISOLATION_DIR" WEATHER_PYTHONPATH_MARKER="$ISOLATION_MARKER" /usr/bin/make --no-print-directory -f "$ROOT_DIR/Makefile" "PYTHON=$HOST_PYTHON" lint) >"$TEMP_ROOT/pythonpath.out" 2>&1
[ ! -e "$ISOLATION_MARKER" ]
printf '%s\n' 'Make authority tests passed: 40 target/authority cases, literal hostile Python and UV paths, 6 raw Make-syntax controls, 2 MAKEFILE_LIST rejections, 2 startup parse-time boundary reproductions, 8 later single-colon replacement rejections, 8 later double-colon append boundary reproductions, later root/Python/UV and non-override shell protection, override/startup/PATH-Python/PATH-UV boundary controls, cleanup containment, caller MAKEFLAGS rejection, 10 mode rejections, and 1 hostile PYTHONPATH runtime gate'
