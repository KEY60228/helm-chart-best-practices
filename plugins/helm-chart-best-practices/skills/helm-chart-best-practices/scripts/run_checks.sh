#!/usr/bin/env bash
# run_checks.sh — mechanical pre-flight checks for a Helm chart.
#
# Usage: scripts/run_checks.sh <chart-dir>
#
# Runs (when the tool is available):
#   - helm lint                 -> catches manifest-level issues
#   - helm template             -> catches render-time errors
#   - check_labels.py           -> warns on missing recommended labels
#
# Each step prints a clearly-labeled section so the wrapping skill can
# read the output and incorporate it into the review report.

set -u

CHART_DIR="${1:-}"
if [[ -z "${CHART_DIR}" ]]; then
  echo "usage: $0 <chart-dir>" >&2
  exit 64
fi
if [[ ! -f "${CHART_DIR}/Chart.yaml" ]]; then
  echo "error: ${CHART_DIR}/Chart.yaml not found — is this a Helm chart directory?" >&2
  exit 64
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXIT=0

section() { printf "\n=== %s ===\n" "$1"; }

section "helm lint"
if command -v helm >/dev/null 2>&1; then
  helm lint "${CHART_DIR}" || EXIT=$?
else
  echo "skipped: 'helm' not installed"
fi

section "helm template (render check)"
if command -v helm >/dev/null 2>&1; then
  if ! helm template "_review_" "${CHART_DIR}" >/dev/null; then
    echo "helm template failed — see error above" >&2
    EXIT=1
  else
    echo "ok"
  fi
else
  echo "skipped: 'helm' not installed"
fi

section "label coverage (recommended Helm labels)"
if command -v python3 >/dev/null 2>&1; then
  python3 "${SCRIPT_DIR}/check_labels.py" "${CHART_DIR}" || EXIT=$?
else
  echo "skipped: python3 not available"
fi

section "summary"
if [[ ${EXIT} -eq 0 ]]; then
  echo "all checks passed"
else
  echo "one or more checks reported issues (exit ${EXIT})"
fi
exit ${EXIT}
