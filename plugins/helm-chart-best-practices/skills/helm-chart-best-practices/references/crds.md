# Custom Resource Definitions

Mirrors <https://helm.sh/docs/chart_best_practices/custom_resource_definitions/>.

## Background

There are two distinct things to keep straight:

- **CRD declaration** — the YAML of kind `CustomResourceDefinition` that defines a new API.
- **CR instance** — a resource whose `apiVersion`/`kind` is provided by a CRD.

The best practices apply to the declaration.

## Rules

### Two ways to install CRDs

**Method 1 — the `crds/` directory (Helm-managed install).**

- Place each CRD declaration as a `.yaml` file under `crds/` at the chart root.
- CRDs in this directory are **not templated.** They are static YAML — no Go template actions allowed.
- On `helm install`, Helm installs everything in `crds/` first, then waits, then renders the templates.
- If a CRD with the same name already exists, Helm **skips** it and prints a warning.
- `--skip-crds` lets the user bypass installation when they manage CRDs out-of-band (e.g. cluster operators).
- **There is no support for upgrading or deleting CRDs via Helm.** On `helm upgrade`, CRD files in `crds/` are ignored. On `helm uninstall`, CRDs are left in place.

**Method 2 — separate chart for the CRDs.**

- Put the CRD declarations in their own chart (e.g. `my-app-crds`).
- Put the rest of the application in another chart (e.g. `my-app`).
- Users install the CRD chart once, then install/upgrade the application chart freely.
- This is the right approach when you need to ship CRD updates as part of normal release cadence — because Method 1 cannot upgrade them.

### Other constraints
- `--dry-run` does not support CRDs in `crds/`. Pre-flight checks need a different strategy.
- The old `crd-install` hook is removed; do not try to re-introduce it.

## Examples

```
mychart/
├── Chart.yaml
├── values.yaml
├── crds/
│   └── widget-crd.yaml      # static, no {{ ... }}
└── templates/
    └── widget-cr.yaml       # uses .Values, references the CRD's kind
```

```yaml
# Good — crds/widget-crd.yaml (static)
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: widgets.example.com
spec:
  group: example.com
  names:
    kind: Widget
    listKind: WidgetList
    plural: widgets
    singular: widget
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
```

```yaml
# Bad — CRD with template actions in crds/
# Helm will refuse to process this — crds/ is not templated.
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: {{ include "mychart.fullname" . }}-widgets   # NOT ALLOWED
```

## NOTES.txt guidance

If your chart ships CRDs, add a clear note to `NOTES.txt`:

> This chart installs CRDs on first install but does **not** upgrade or delete them.
> To update CRDs, either upgrade them manually with `kubectl apply -f` or install the
> companion `<chart>-crds` chart separately.

## Common mistakes
- Putting CRDs under `templates/` and using template actions — they install once, but every upgrade tries to re-apply them and may fail under newer API server validation.
- Expecting `helm uninstall` to remove CRDs and their CRs — it won't touch CRDs and orphans the CRs.
- Assuming `helm upgrade` ships updated CRD definitions — it does not. Always document the upgrade story.
