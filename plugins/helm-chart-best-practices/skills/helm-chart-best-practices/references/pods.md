# Pods and PodTemplates

Mirrors <https://helm.sh/docs/chart_best_practices/pods/>.

## Rules

### Images
- A container image should use a **fixed tag** or the **SHA digest** of the image.
- Avoid floating tags: `latest`, `head`, `canary`. They are non-reproducible and make rollbacks ambiguous.
- Define the image (and ideally the tag) in `values.yaml` so users can override without forking the chart.
- It is common — and recommended — to split `image.repository` and `image.tag` into separate fields:

  ```yaml
  image:
    repository: "nginx"
    tag: "1.27.1"
    pullPolicy: "IfNotPresent"
  ```

### imagePullPolicy
- `helm create` defaults `imagePullPolicy` to `IfNotPresent` — keep it.
- Expose the policy in `values.yaml` so users can switch to `Always` when they intentionally use floating tags in dev/staging.
- If you leave the field unset entirely, Kubernetes defaults to `IfNotPresent` (and to `Always` for tag `:latest`). Being explicit removes the surprise.

### PodTemplates: declare selectors
- Every PodTemplate-bearing object (`Deployment`, `StatefulSet`, `DaemonSet`, `Job`) must specify a `spec.selector`.
- `spec.selector.matchLabels` must match `spec.template.metadata.labels`.
- **The selector must reference only immutable labels.** The standard pair is `app.kubernetes.io/name` + `app.kubernetes.io/instance`. See [labels.md](./labels.md).
- Never put values that change on upgrade — chart version, app version, release date — in a selector. Doing so detaches old pods on upgrade and is one of the most common Helm bugs in the wild.

### Pull secrets (and other Pod-level fields not covered by the upstream guide)
The upstream guide stops at the three rules above. When asked to scaffold a chart, do not invent new mandatory fields — but expose what users typically need via `values.yaml`:

- `imagePullSecrets` (list of secret refs)
- `nodeSelector`, `tolerations`, `affinity`
- `podAnnotations`, `podLabels`
- `securityContext`, `containerSecurityContext`

Wire these from `values.yaml` into the template with `with`/`toYaml`/`nindent` so users get full control without you opinionating defaults that aren't in the guide.

## Examples

```yaml
# Good — image config in values.yaml
image:
  repository: "ghcr.io/example/webapp"
  tag: "1.4.2"
  pullPolicy: "IfNotPresent"
```

```yaml
# Good — Deployment uses a stable selector
spec:
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mychart.labels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
```

```yaml
# Bad — floating tag, no pull policy, version in selector
spec:
  selector:
    matchLabels:
      app: webapp
      version: "{{ .Chart.AppVersion }}"   # changes on upgrade -> selector breaks
  template:
    spec:
      containers:
        - image: "nginx:latest"            # floating tag
```

## Common mistakes
- Selectors that include `version`, `helm.sh/chart`, or a timestamp.
- Image reference written as a single string `image: "nginx:1.27.1"` in `values.yaml`, which makes per-environment overrides awkward.
- Omitting `imagePullPolicy`, then debugging strange behavior when one cluster pulls and another doesn't.
- Hardcoding `imagePullSecrets` instead of templating from values.
