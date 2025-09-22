#!/usr/bin/env bash
set -euo pipefail

# Runner for X.AI batch tests. Usage:
# ./run_xai_batch.sh [--stream] [--temperature <value>] <batch-file>

BATCH_FILE=""
STREAM=0
TEMPERATURE=0.8

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stream)
      STREAM=1; shift ;;
    --temperature)
      TEMPERATURE="$2"; shift 2 ;;
    -*|--*)
      echo "Unknown option $1"; exit 1 ;;
    *)
      BATCH_FILE="$1"; shift ;;
  esac
done

if [[ -z "${BATCH_FILE}" ]]; then
  echo "Usage: $0 [--stream] [--temperature 0.8] <batch-file>" >&2
  exit 2
fi

# Source credentials file if present
if [[ -f "$HOME/.config/env.d/ai.env" ]]; then
  # shellcheck disable=SC1090
  source "$HOME/.config/env.d/ai.env"
fi

if [[ -z "${XAI_API_KEY:-}" ]]; then
  echo "XAI_API_KEY is not set. Export it or place it in ~/.config/env.d/ai.env" >&2
  exit 3
fi

PY="/home/fratq/test/apps/epistemic_LLM_network/venv/bin/python"
SCRIPT="/home/fratq/test/apps/epistemic_LLM_network/scripts/xai_chat_repl.py"

ARGS=("--temperature" "${TEMPERATURE}")
if [[ "$STREAM" -eq 1 ]]; then
  ARGS+=("--stream")
fi

cat "$BATCH_FILE" | "$PY" "$SCRIPT" "${ARGS[@]}"
