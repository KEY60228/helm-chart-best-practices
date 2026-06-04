# Templates

Mirrors <https://helm.sh/docs/chart_best_practices/templates/>.

## Rules

### Structure of `templates/`
- Output files that render to YAML use `.yaml`.
- Files that hold only `{{ define }}` blocks (no rendered YAML output) use `.tpl`. The canonical example is `_helpers.tpl`.
- Use **dashes** in filenames, not camelCase: `foo-pod.yaml`, not `fooPod.yaml`.
- One Kubernetes resource per file.
- The filename should reflect the resource kind (e.g. `deployment.yaml`, `service.yaml`, `service-account.yaml`).
- Files that start with `_` are partials — they are not rendered as their own manifests.

### Names of defined templates
- Every `{{ define "..." }}` is **globally accessible** inside a release, so you must namespace them with the chart name to avoid collisions when your chart is used as a subchart.
- Good: `{{- define "nginx.fullname" -}}`
- Bad: `{{- define "fullname" -}}`
- `helm create` produces correctly-namespaced helpers — start from that pattern.

### Formatting templates
- Two-space indentation, never tabs (same as YAML).
- Put a space after `{{` and before `}}`.
- Good: `{{ .foo }}{{ print "foo" }}`
- Bad: `{{.foo}}{{print "foo"}}`
- Use `-` whitespace chomp where possible (`{{- ... -}}`) to keep output clean.

### Whitespace in generated templates
- Keep blank lines in rendered output to a minimum.
- Multiple blank lines are visual noise and can confuse downstream YAML tools.
- A single blank line between logical sections is fine.

### Comments
- **YAML comments** (`# ...`) appear in rendered output. Use them when you want the user to see the comment in the manifest.
- **Template comments** (`{{- /* ... */ -}}`) are stripped during rendering. Use them to explain template logic to other chart authors.
- Mixing the `required` function with adjacent YAML comments has a known rendering pitfall — prefer template comments around `required` calls.

### Use of JSON in templates and output
- YAML is a superset of JSON. For simple short lists, JSON-style inline arrays read better:
  - `args: ["--dirname", "/foo"]`
- For deeply nested structures, stay in YAML — JSON syntax becomes unreadable.
- When a Kubernetes field expects an embedded JSON blob (some init-container configs, annotations), JSON is the correct choice.

## Examples

```yaml
# Good — _helpers.tpl, namespaced define
{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.chart" . }}
{{ include "mychart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

```yaml
# Bad — un-namespaced helper collides as a subchart
{{- define "labels" -}}
...
{{- end }}
```

```yaml
# Good — dashed filename, single resource
# templates/web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
...
```

```yaml
# Bad — camelCase filename
# templates/webDeployment.yaml
```

## Common mistakes
- Two resources in one file (`Service` and `Deployment` together) — harder to read in `helm template` output.
- Unspaced actions like `{{.Values.foo}}` — works but violates the convention.
- Excessive blank lines from forgetting `-` chomps.
- Helpers without a chart-name prefix — invisible time bomb when the chart becomes a subchart.
