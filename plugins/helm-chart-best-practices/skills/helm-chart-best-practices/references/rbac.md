# Role-Based Access Control

Mirrors <https://helm.sh/docs/chart_best_practices/rbac/>.

## Rules

### Separate `rbac` and `serviceAccount` keys in `values.yaml`
Keep them as distinct top-level keys. They are related but independent concerns: one creates RBAC objects, the other creates a `ServiceAccount`.

```yaml
rbac:
  # rbac.create indicates whether Role/RoleBinding resources are created.
  create: true

serviceAccount:
  # serviceAccount.create indicates whether a ServiceAccount is created.
  create: true
  # serviceAccount.name overrides the default name (the chart's fullname).
  name: ""
```

### Multi-component charts: one `serviceAccount` per component
If the chart deploys several distinct workloads, give each one its own `serviceAccount` block so users can grant least privilege per component.

```yaml
someComponent:
  serviceAccount:
    create: true
    name: ""
anotherComponent:
  serviceAccount:
    create: true
    name: ""
```

### Default `rbac.create` to `true`
Users who manage RBAC out of band (GitOps, central admin charts) can set it to `false`. Most users will not, and a chart that ships disabled RBAC by default tends to crash on first install.

### Logic for resolving the ServiceAccount name
Implement this consistently via a helper:

- `serviceAccount.create == true` and `serviceAccount.name == ""` → use the chart's fullname.
- `serviceAccount.create == true` and `serviceAccount.name != ""` → use the given name (and create the SA with it).
- `serviceAccount.create == false` and `serviceAccount.name != ""` → use the given name, do **not** create the SA (user manages it).
- `serviceAccount.create == false` and `serviceAccount.name == ""` → use `"default"`.

### Use the `Role` vs `ClusterRole` distinction deliberately
- `Role` / `RoleBinding` — namespaced. Use when the chart only needs permissions in its own namespace.
- `ClusterRole` / `ClusterRoleBinding` — cluster-wide. Use only when truly necessary (e.g. node-watching daemons, admission controllers). Default to namespaced.

## Examples

```yaml
# Good — _helpers.tpl
{{- define "mychart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "mychart.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
```

```yaml
# Good — templates/serviceaccount.yaml
{{- if .Values.serviceAccount.create -}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "mychart.serviceAccountName" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
{{- end }}
```

```yaml
# Good — templates/role.yaml
{{- if .Values.rbac.create -}}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
{{- end }}

---
{{- if .Values.rbac.create -}}
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: {{ include "mychart.fullname" . }}
subjects:
  - kind: ServiceAccount
    name: {{ include "mychart.serviceAccountName" . }}
{{- end }}
```

## Common mistakes
- Conflating `rbac.create` and `serviceAccount.create` into a single switch — users lose the ability to bring their own SA.
- Defaulting `rbac.create` to `false` and then having Deployments crash because the SA has no permissions.
- Using a `ClusterRole` when a namespaced `Role` would suffice. (Reviewers should always question `ClusterRole`.)
- ServiceAccount-name logic inlined into every template instead of one helper — drift is inevitable.
