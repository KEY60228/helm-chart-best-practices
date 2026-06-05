# Values

Mirrors <https://helm.sh/docs/chart_best_practices/values/>.

## Rules

### Naming conventions
- Variable names start with a **lowercase** letter.
- Use **camelCase** to separate words.
- Built-in Helm variables start with uppercase (`.Release.Name`, `.Capabilities.KubeVersion`) — your value names must not collide.
- **No** hyphens, **no** underscores in keys (use `chickenNoodleSoup`, not `chicken-noodle-soup`).

### Flat or nested values
- **Prefer flat structure.** Flat keys remove the need for existence checks in templates.
- Nested keys force you to write `{{ if .Values.server }}{{ .Values.server.name }}{{ end }}` to avoid nil panics.
- Use nesting **only** when many related values exist and at least one is required — there nesting improves readability enough to justify the extra defensiveness.

### Make types clear
- YAML type coercion is treacherous: `foo: false` is a boolean, `foo: "false"` is a string, and `foo: 1234567890` may be reformatted into scientific notation.
- **Quote all strings.** It is the single cheapest defense.
- For ambiguous numerics, store them as strings and cast inside templates with `{{ int $value }}`.
- Explicit YAML type tags (`!!string`) survive only one parse pass and then disappear — they are not a reliable solution.

### Consider how users will use your values
- Values come from three places: `values.yaml`, `-f overrides.yaml`, and `--set key=value`.
- **Maps are `--set`-friendly. Arrays are not.**
- Bad (array): `servers: [{name: foo, port: 80}]` — there is no concise `--set` form.
- Good (map): `servers: { foo: { port: 80 } }` — overridable with `--set servers.foo.port=8080`.

### Document `values.yaml`
- Every property in `values.yaml` must have a documentation comment.
- The comment **must start with the property name**, so it is greppable and tooling-friendly.
- The comment must include at least one sentence describing the property.

## Examples

```yaml
# Good — flat, documented, types are clear
# image is the container image to deploy.
image: "nginx"

# imageTag is the tag of the container image to deploy.
imageTag: "1.27.1"

# replicaCount is the number of replicas of the Deployment.
replicaCount: 3
```

```yaml
# Bad — nested, undocumented, ambiguous types
server:
  name: foo            # no comment, easy to override but hard to document
  port: 8080
  enabled: false       # boolean vs. string ambiguity if used with `--set`
```

```yaml
# Bad — array form blocks `--set`
servers:
  - name: foo
    port: 80
  - name: bar
    port: 81
```

## Common mistakes
- Capitalized first letter (`Image: ...`) — collides with built-ins.
- Underscores or hyphens in keys.
- One-word comments above values (`# port`) — fails the "start with property name + one sentence" rule.
- Long unquoted strings that happen to be YAML keywords (`yes`, `no`, `on`, `off`).
- Arrays of complex objects in `values.yaml` when a map would do.
