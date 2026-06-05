# General Conventions

Mirrors <https://helm.sh/docs/chart_best_practices/conventions/>.

## Rules

### Chart names
- Lowercase letters and numbers only.
- Words may be separated with dashes (`-`).
- **No** uppercase letters, **no** underscores, **no** dots.
- Good: `drupal`, `nginx-lego`, `aws-cluster-autoscaler`.
- Bad: `MyApp`, `my_app`, `my.app`.

### Version numbers
- Follow [SemVer 2](https://semver.org/) wherever possible.
- When a version is stored in a Kubernetes label, replace `+` with `_` because labels do not accept `+`. The standard pattern is `{{ .Chart.Version | replace "+" "_" }}`.
- Docker image tags are an exception — they do not have to be SemVer.

### Formatting YAML
- Two-space indentation.
- **Never** tabs.

### Usage of the words "Helm" and "chart"
- "Helm" (capital H) is the project name.
- "helm" (lowercase) is the client-side command.
- "chart" is not a proper noun, so it is lowercase.
- "Chart.yaml" is a filename and is capitalized.
- When in doubt, use "Helm" (capital).

### Chart templates and namespaces
- Do **not** set `metadata.namespace` in chart templates.
- Let users pick the namespace via `--namespace` (or via their cluster tooling). Templates that hardcode a namespace become awkward for users who install many copies of a chart.

## Examples

```yaml
# Good — Chart.yaml
apiVersion: v2
name: my-web-app
version: 1.4.2
appVersion: "1.4.2"
```

```yaml
# Bad — Chart.yaml
apiVersion: v2
name: MyWebApp        # uppercase
version: v1.4         # not SemVer
```

```yaml
# Bad — explicit namespace in a template
metadata:
  name: {{ include "mychart.fullname" . }}
  namespace: production    # let the user choose, do not hardcode
```

## Common mistakes
- Underscores in chart names (e.g. `my_chart`) — rejected by `helm install`.
- Storing `1.0.0+abc` directly in a label (invalid; must become `1.0.0_abc`).
- Mixed tabs and spaces in a single YAML file — silent rendering bugs.
