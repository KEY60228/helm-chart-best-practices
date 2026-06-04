# Dependencies

Mirrors <https://helm.sh/docs/chart_best_practices/dependencies/>.

## Rules

### Versions
- Use **version ranges**, not exact pins, so users automatically pick up patch fixes.
- The patch-level range `~1.2.3` matches `>=1.2.3, <1.3.0`. This is the recommended default.
- A bare `~1.2.3` does **not** match prerelease versions like `1.2.4-rc1`. If you need to match prereleases, use `~1.2.3-0`.

### Repository URLs
- Prefer `https://` URLs.
- `http://` is acceptable when HTTPS is not available, but it is a smell.
- `file://` URLs are for fixed local deployments only and rarely belong in published charts.
- If the repo is registered in the user's index, use the alias form (`@reponame`) or the `alias` field instead of an inline URL.
- Leaving `repository` blank means Helm cannot perform dependency-management operations on that dependency. Don't leave it blank.

### Conditions and tags
- Mark any **optional** dependency with `condition` or `tags`.
- `condition` should reference a sub-chart key, e.g. `condition: somechart.enabled`. This is more readable than naming an unrelated values key.
- `tags` group related optional sub-charts. If several sub-charts together provide one feature, give them a shared tag so users can toggle the whole feature on/off in one place.

## Examples

```yaml
# Good — Chart.yaml dependencies block
dependencies:
  - name: postgresql
    version: "~12.5.6"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "~17.11.3"
    repository: "@bitnami"
    tags:
      - cache
```

```yaml
# Bad — exact pin, http, missing condition
dependencies:
  - name: postgresql
    version: "12.5.6"          # exact pin = no patch upgrades
    repository: "http://charts.example.com"   # HTTP
    # no condition or tag, even though postgres is optional
```

## Common mistakes
- Pinning to an exact version "for stability" — users lose patch security fixes.
- Empty `repository` field — breaks `helm dependency update`.
- Forgetting a `condition` on an optional sub-chart, so users have to remove the dependency entry to disable it.
- Using `condition: enabled` (no namespace) instead of `condition: <chartname>.enabled`.
