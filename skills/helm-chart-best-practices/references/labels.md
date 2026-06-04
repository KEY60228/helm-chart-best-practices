# Labels and Annotations

Mirrors <https://helm.sh/docs/chart_best_practices/labels/>.

## Rules

### Labels vs annotations
- **Labels** — for metadata Kubernetes or operators need to **query** or **identify** by.
- **Annotations** — for metadata that is not queried, just stored.
- **Helm hooks** are always implemented as annotations, never labels.

### Recommended label set
Apply these to every Helm-managed resource. Definitions are from the [Kubernetes recommended labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/) and reinforced by the Helm best-practices guide.

| Label | Recommendation | Standard template value |
| --- | --- | --- |
| `app.kubernetes.io/name` | REC | `{{ include "<chart>.name" . }}` |
| `helm.sh/chart` | REC | `{{ .Chart.Name }}-{{ .Chart.Version \| replace "+" "_" }}` |
| `app.kubernetes.io/managed-by` | REC | `{{ .Release.Service }}` (always `Helm` for Helm releases) |
| `app.kubernetes.io/instance` | REC | `{{ .Release.Name }}` |
| `app.kubernetes.io/version` | OPT | `{{ .Chart.AppVersion }}` (quote it) |
| `app.kubernetes.io/component` | OPT | Role string, e.g. `frontend`, `worker`, `database` |
| `app.kubernetes.io/part-of` | OPT | Top-level app name, when this chart is part of a multi-chart product |

### Selector labels (a subset!)
Selectors (`spec.selector.matchLabels`, `spec.selector`) must reference **only immutable** labels. The standard subset is:

- `app.kubernetes.io/name`
- `app.kubernetes.io/instance`

**Never** put `helm.sh/chart`, `app.kubernetes.io/version`, or any timestamp-bearing label into a selector. Those values change on upgrade and break the selector.

### Apply the labels consistently
- The REC labels go on **every** Helm-rendered resource — Deployments, Services, ServiceAccounts, ConfigMaps, Secrets, Ingresses, etc.
- Standardize via two helpers in `_helpers.tpl`: a full `<chart>.labels` block and a slimmer `<chart>.selectorLabels` block.

## Examples

```yaml
# Good — _helpers.tpl
{{- define "mychart.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "mychart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

```yaml
# Good — Deployment using both helpers correctly
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mychart.labels" . | nindent 8 }}
```

```yaml
# Bad — selector includes the chart version, which changes on upgrade
spec:
  selector:
    matchLabels:
      helm.sh/chart: mychart-1.0.0    # mutable -> selector breaks on upgrade
```

## Common mistakes
- Putting `helm.sh/chart` or `app.kubernetes.io/version` into selectors. The selector silently fails to match pods after a chart-version bump.
- Forgetting `app.kubernetes.io/managed-by: Helm`. Operators rely on this to know what they own.
- Using arbitrary `app: foo` labels alone — modern tooling expects the `app.kubernetes.io/*` prefix.
- Treating Helm hook directives as labels — they must be annotations.
