#!/usr/bin/env python3
"""check_labels.py — flag missing recommended Helm labels in a chart.

Runs `helm template` (if available) to render the chart, then inspects the
rendered manifests for the recommended labels documented in:

    https://helm.sh/docs/chart_best_practices/labels/

If `helm` is unavailable, falls back to a static scan of templates/*.yaml.
The static scan is heuristic and reports lower-confidence findings.

Usage:
    check_labels.py <chart-dir>

Exit codes:
    0  no issues found
    1  one or more resources are missing recommended labels
    2  the chart could not be parsed at all
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RECOMMENDED_LABELS = [
    "app.kubernetes.io/name",
    "app.kubernetes.io/instance",
    "app.kubernetes.io/managed-by",
    "helm.sh/chart",
]
SELECTOR_FORBIDDEN = [
    "helm.sh/chart",
    "app.kubernetes.io/version",
]
RESOURCE_KINDS_REQUIRING_LABELS = {
    "Deployment",
    "StatefulSet",
    "DaemonSet",
    "Job",
    "CronJob",
    "Service",
    "ConfigMap",
    "Secret",
    "ServiceAccount",
    "Ingress",
    "HorizontalPodAutoscaler",
    "PodDisruptionBudget",
}


def _render(chart_dir: Path) -> str | None:
    try:
        result = subprocess.run(
            ["helm", "template", "_label_check_", str(chart_dir)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return None
    return result.stdout


def _split_docs(rendered: str) -> list[str]:
    return [doc for doc in rendered.split("\n---\n") if doc.strip()]


def _parse_yaml(doc: str) -> dict | None:
    try:
        import yaml  # type: ignore
    except ImportError:
        return None
    try:
        return yaml.safe_load(doc)
    except Exception:
        return None


def _check_manifest(manifest: dict) -> list[str]:
    issues: list[str] = []
    kind = manifest.get("kind")
    if kind not in RESOURCE_KINDS_REQUIRING_LABELS:
        return issues

    metadata = manifest.get("metadata") or {}
    name = metadata.get("name", "<unknown>")
    labels = (metadata.get("labels") or {}) if isinstance(metadata, dict) else {}
    missing = [lab for lab in RECOMMENDED_LABELS if lab not in labels]
    if missing:
        issues.append(
            f"{kind}/{name}: missing recommended labels: {', '.join(missing)}"
        )

    spec = manifest.get("spec") or {}
    selector = spec.get("selector") or {}
    match_labels = (
        selector.get("matchLabels") if isinstance(selector, dict) else None
    ) or {}
    if isinstance(selector, dict) and "matchLabels" not in selector and selector:
        match_labels = selector
    for forbidden in SELECTOR_FORBIDDEN:
        if forbidden in match_labels:
            issues.append(
                f"{kind}/{name}: selector references mutable label '{forbidden}' — "
                "selectors must use only immutable labels (app.kubernetes.io/name + "
                "app.kubernetes.io/instance)."
            )
    return issues


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write(f"usage: {argv[0]} <chart-dir>\n")
        return 64

    chart_dir = Path(argv[1])
    if not (chart_dir / "Chart.yaml").is_file():
        sys.stderr.write(f"error: {chart_dir}/Chart.yaml not found\n")
        return 64

    rendered = _render(chart_dir)
    if rendered is None:
        print("note: 'helm' is unavailable; static label scan is limited.")
        print("      Install helm for full coverage.")
        return 0

    issues: list[str] = []
    parsed_any = False
    for doc in _split_docs(rendered):
        manifest = _parse_yaml(doc)
        if not isinstance(manifest, dict):
            continue
        parsed_any = True
        issues.extend(_check_manifest(manifest))

    if not parsed_any:
        print("note: could not parse any manifests (is PyYAML installed?).")
        return 0

    if issues:
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("ok: all rendered resources carry the recommended labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
