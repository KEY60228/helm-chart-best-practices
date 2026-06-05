# helm-chart-best-practices

A reusable Agent Skill and plugin that helps agents **review** and **generate** Helm charts following the [official Helm Chart Best Practices Guide](https://helm.sh/docs/chart_best_practices/).

The skill captures the eight chapters of the official guide — General Conventions, Values, Templates, Dependencies, Labels and Annotations, Pods and PodTemplates, Custom Resource Definitions, and Role-Based Access Control — and turns them into a routine an agent can run on any chart you give it.

## What it does

When the skill triggers, the agent will:

- **Review mode** — Walk a Helm chart directory, run `helm lint` / `helm template` when available, and produce a categorized report of best-practice violations with suggested fixes and references to the upstream guidance.
- **Generate mode** — Scaffold a new chart that already follows the guide (correct chart name, SemVer, standard labels, flat values with documentation, helper templates, secure pod defaults, etc.).
- **Refactor mode** — Apply edits in-place to bring an existing chart up to the guide.

## Installation

### Claude Code

```bash
# Register this repository as a marketplace
/plugin marketplace add KEY60228/helm-chart-best-practices

# Install the plugin
/plugin install helm-chart-best-practices@helm-chart-best-practices
```

### Codex

```bash
# Register this repository as a marketplace
codex plugin marketplace add KEY60228/helm-chart-best-practices

# Install the plugin (also available in the interactive `codex /plugins` browser)
codex plugin install helm-chart-best-practices
```

The repository ships parallel manifests — `.claude-plugin/plugin.json` for Claude Code and `.codex-plugin/plugin.json` for Codex — pointing at the same `skills/helm-chart-best-practices/` source.

### Other agents (open Agent Skills standard)

The skill follows the open [Agent Skills](https://agentskills.io/) standard, so any tool that resolves `~/.agents/skills/` (Codex, Claude Code, Copilot CLI, …) can use it directly without a plugin wrapper:

```bash
git clone https://github.com/KEY60228/helm-chart-best-practices.git
ln -s "$(pwd)/helm-chart-best-practices/skills/helm-chart-best-practices" \
      "$HOME/.agents/skills/helm-chart-best-practices"
```

Or download the `helm-chart-best-practices.skill` artifact from a [Release](https://github.com/KEY60228/helm-chart-best-practices/releases) and unpack it into `~/.agents/skills/`.

## Authoritative source

This skill mirrors the structure and wording of the official Helm documentation at the time of writing. Whenever the upstream guide changes, the references should be refreshed and a new version released.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for local development, evaluation, and release instructions.

## License

Apache-2.0. See [LICENSE](./LICENSE).
