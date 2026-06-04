# Contributing

Thanks for your interest in improving `helm-chart-best-practices`! This document covers local development, evaluation, and the release process.

## Repository layout

```
.
├── .claude-plugin/      # Plugin & marketplace manifests for Claude Code
├── .codex-plugin/       # Plugin & marketplace manifests for Codex
├── skills/
│   └── helm-chart-best-practices/
│       ├── SKILL.md     # Skill entry point (this is what the agent loads)
│       ├── references/  # One file per chapter of the upstream guide
│       ├── scripts/     # Helpers (helm lint wrapper, label checker)
│       └── assets/      # Output templates
├── evals/               # Test cases and fixtures used to evaluate the skill
├── .github/workflows/   # CI (release packaging)
└── README.md
```

The skill itself (`skills/helm-chart-best-practices/`) is the single source of truth; both plugin manifests reference it. When bumping the version, update **both** `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` — the release workflow refuses to publish if they drift.

When editing the skill, the file you almost always want is `skills/helm-chart-best-practices/SKILL.md` and the chapter under `references/`.

## Local development

You can iterate on the skill locally by symlinking it into your user skills directory:

```bash
git clone https://github.com/KEY60228/helm-chart-best-practices.git
cd helm-chart-best-practices
ln -s "$(pwd)/skills/helm-chart-best-practices" \
      "$HOME/.claude/skills/helm-chart-best-practices"
```

Edits to `SKILL.md` / `references/*.md` take effect on the next Claude Code session.

To test the bundled scripts directly:

```bash
skills/helm-chart-best-practices/scripts/run_checks.sh evals/fixtures/bad-chart
```

This runs `helm lint`, `helm template`, and the label checker — useful when you change the scripts themselves.

## Evaluation

The `evals/` directory holds the test cases used to measure changes to the skill. The recommended workflow:

1. Edit the skill.
2. Run the evals via the [`skill-creator`](https://code.claude.com/) loop — for each case, spawn one run with the skill and one without (baseline) and compare.
3. Review outputs side-by-side in the eval viewer.
4. Iterate.

Workspace outputs from these runs go under `helm-chart-best-practices-workspace/iteration-N/` and are git-ignored.

When you add a new eval case:

- Add the prompt to `evals/evals.json`.
- Add any required fixture files under `evals/fixtures/<case-name>/`.
- Document the assertions you expect to pass.

## Upstream sync

`references/*.md` paraphrases <https://helm.sh/docs/chart_best_practices/>. When the upstream guide changes:

1. Re-read each of the eight chapters and update the corresponding `references/*.md`.
2. Update example snippets if upstream changed them.
3. Bump `version` in `.claude-plugin/plugin.json`.
4. Cut a new release (see below).

## Releasing

The `.skill` artifact is **not committed**. It is built by CI on tag push and attached to a GitHub Release.

To cut a release:

1. Bump `version` in **both** `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` (SemVer, e.g. `0.1.0` → `0.2.0`).
2. Commit and push the version bump on `main`.
3. Tag the commit and push the tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

The `Release` workflow (`.github/workflows/release.yml`) then:

- Verifies that the git tag matches the `version` in both plugin manifests (refuses to release otherwise).
- Validates the `SKILL.md` frontmatter.
- Zips `skills/helm-chart-best-practices/` into `helm-chart-best-practices.skill`.
- Creates a GitHub Release with auto-generated notes and the `.skill` attached.

### Building the artifact locally

For pre-release smoke testing only — never commit the result:

```bash
(cd skills && zip -r ../helm-chart-best-practices.skill helm-chart-best-practices \
  -x '**/__pycache__/*' '**/*.pyc' '**/.DS_Store')
```

## Filing issues / PRs

- For bugs in the rules themselves, please link to the relevant section of <https://helm.sh/docs/chart_best_practices/>.
- For rule additions that go beyond the upstream guide (security hardening, resource limits, probes, etc.), open an issue first to discuss scope.
- Run the eval suite locally and include a short summary of pass-rate impact in your PR description when changing `SKILL.md` or `references/*.md`.
