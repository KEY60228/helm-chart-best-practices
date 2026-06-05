---
name: helm-chart-best-practices
description: Review or generate Helm charts following the official Helm Chart Best Practices Guide (https://helm.sh/docs/chart_best_practices/). Use this skill whenever the user works with Helm charts — auditing a chart, fixing lint findings, writing a new chart from scratch, refactoring values.yaml, adjusting templates/labels/RBAC/CRDs, or asking "is this chart any good?". Trigger even when the user does not explicitly say "best practices" but is clearly editing or producing a Chart.yaml, templates/*.yaml, values.yaml, _helpers.tpl, or a crds/ directory.
license: Apache-2.0
---

# Helm Chart Best Practices

You help users **review** and **generate** Helm charts that conform to the official Helm guide at <https://helm.sh/docs/chart_best_practices/>. The guide has eight chapters; each one is mirrored as a file in `references/`. Treat the upstream guide as the source of truth — when in doubt, quote it.

## Language

Mirror the language the user writes in. English is the default, but if the user writes in Japanese, Chinese, Korean, German, etc., respond in that same language — including the review report, the explanations of findings, and any narrative commentary around patches. Translate the section headers of `assets/review_report_template.md` (e.g. *Summary*, *Findings*, *Must fix*, *Should fix*, *Consider*) into the user's language; the template is a structural scaffold, not a fixed string.

Keep these in their original English form regardless of response language, because they carry meaning only in the original:

- Direct quotes from `references/*.md` and from the upstream Helm best-practices guide.
- URLs (e.g. `https://helm.sh/docs/chart_best_practices/...`).
- Code, YAML, identifiers, chart names, label keys, template actions, CLI flags.

The same applies to the references themselves: when you cite a chapter, you may paraphrase it in the user's language, but the verbatim quote stays English.

## When to trigger

Apply this skill whenever the user is working with anything that looks like a Helm chart, even if they don't say "best practice":

- A directory containing `Chart.yaml`, `values.yaml`, `templates/`, or `crds/`.
- Files with `{{ .Values.* }}`, `{{ .Release.* }}`, `{{ .Chart.* }}`, `{{ include "..." . }}`.
- Requests to "audit", "review", "fix", "lint", or "scaffold" a chart.
- Questions like "why is this template wrong?", "what labels should I use?", "how do I declare a CRD?".

## Two operating modes

Decide which mode you are in from the user's request and the files in the working directory.

### 1. Review mode

The user has an existing chart and wants feedback. Produce a **categorized review report** (template in `assets/review_report_template.md`). Steps:

1. **Map the chart.** List files under `Chart.yaml`, `values.yaml`, `templates/`, `crds/`, `charts/`, `templates/_helpers.tpl`. Note the chart name, version, and dependencies.
2. **Run mechanical checks first.** They are fast, deterministic, and catch the obvious stuff so your written review can focus on judgment calls. Use `scripts/run_checks.sh <chart-dir>` — it runs `helm lint`, `helm template` (to catch render errors), and `scripts/check_labels.py` (to flag missing recommended labels). If `helm` is not installed, tell the user and fall back to static reading.
3. **Read every chapter's reference and check the chart against it.** Open each file in `references/` in turn and walk through the rules:
   - `references/conventions.md` — chart names, SemVer, YAML formatting, namespace usage
   - `references/values.md` — camelCase, flat structure, type clarity, `--set` ergonomics, documentation
   - `references/templates.md` — file layout, `_helpers.tpl` naming, whitespace, comments, JSON usage
   - `references/dependencies.md` — version ranges, repo URLs, conditions/tags
   - `references/labels.md` — required `app.kubernetes.io/*` and `helm.sh/chart` labels
   - `references/pods.md` — fixed image tags, `imagePullPolicy`, selector stability
   - `references/crds.md` — `crds/` directory semantics, upgrade caveats
   - `references/rbac.md` — `rbac.create` / `serviceAccount.create` split, helper templates
4. **Categorize findings by severity.** Use these three buckets so the user can decide what to fix now versus later:
   - **Must fix** — the chart will misbehave or fail upstream tools (e.g. mutable selectors, missing `metadata.labels`, invalid chart name).
   - **Should fix** — the chart works but violates a documented recommendation (e.g. nested values, undocumented `values.yaml` keys, `latest` image tag).
   - **Consider** — stylistic or marginal improvements (e.g. extra whitespace, comment phrasing).
5. **For each finding, give:** the file and line, a short description of the rule, the quoted upstream phrasing or section, and a concrete patch suggestion. The patch is the most valuable part — don't leave the user to guess.
6. **End with a summary table** of counts per severity, and offer to apply the patches (refactor mode).

### 2. Generate mode

The user wants a new chart. Do this even if they describe the app in plain language ("scaffold a Helm chart for a Go web service with Postgres dependency").

**Default flow: build on top of `helm create`.** The Helm team maintains the starter, and it already satisfies most of the guide (namespaced helpers, immutable selector, recommended labels, `IfNotPresent` pull policy, gated ServiceAccount). Standing on their work means our value-add is the parts they don't enforce (documentation, dependencies, scope discipline) plus validation — not re-implementing the scaffold. Fall back to a from-scratch write only when `helm` is unavailable.

1. **Gather inputs you actually need:** chart name (kebab-case, lowercase only — see conventions), application name, container image (repository + tag), ports, env vars / secrets, whether they need HPA / Ingress / RBAC / ServiceAccount, dependencies. If the user already supplied most of this, don't re-ask — fill in sensible defaults and call them out.

2. **Generate the scaffold with `helm create`.** Run `helm create <chart-name>` in the target directory. If `helm` is not installed, jump to step 7 (from-scratch fallback).

3. **Strip what the user did NOT ask for.** `helm create` always adds HPA, Ingress, and a `tests/` directory. Delete the templates the user does not need so the chart stays minimal:
   - Drop `templates/hpa.yaml` unless autoscaling was requested.
   - Drop `templates/ingress.yaml` unless ingress was requested.
   - Drop `templates/tests/` unless the user wants Helm tests.
   Leaving these in is the most common review finding against `helm create` output.

4. **Customize for the user's actual app.** Edit `values.yaml` and `templates/` so the chart is about *their* application, not a generic placeholder:
   - Put real `image.repository` / `image.tag` / port / env vars / replica defaults into `values.yaml`.
   - Rename the container or update probe paths in `templates/deployment.yaml` if needed.
   - Add `dependencies:` to `Chart.yaml` per `references/dependencies.md` (version range, `https://` repo, `condition:` for optional sub-charts).

5. **Apply the best-practice diffs that `helm create` does not enforce.** This is where this skill earns its keep:
   - **`values.yaml` documentation** — every key gets a leading `# <keyName> ...` comment per `references/values.md`. The helm-create output is sparse; fix it.
   - **Quote ambiguous strings** (image tags, `appVersion`) and avoid YAML 1.1 keywords like `yes`/`no` for booleans.
   - **values structure** — flatten where the starter nests unnecessarily, per `references/values.md`.
   - **CRDs** — if needed, add static (no template actions!) files under `crds/` per `references/crds.md`, and warn in NOTES.txt that Helm cannot upgrade/delete CRDs.
   - **RBAC split** — `helm create` only ships `serviceAccount.create`. If the chart needs Role/RoleBinding, add the `rbac.create` / `serviceAccount.create` separation per `references/rbac.md`.

6. **Validate.** Run `helm lint <chart-dir>` and `helm template _generate_ <chart-dir>` to confirm the chart still renders. Report any findings. Tell the user explicitly which files you customized vs. left as defaults.

7. **From-scratch fallback (`helm` unavailable).** Produce the same file set by hand, applying every rule directly. Same target files as steps 2–5 would have produced:
   - `Chart.yaml` (SemVer `version`, `appVersion`, `apiVersion: v2`, `type: application`, optional `dependencies`).
   - `values.yaml` — flat where possible, camelCase, every key documented per `references/values.md`.
   - `templates/_helpers.tpl` — `<chart>.name`, `.fullname`, `.chart`, `.labels`, `.selectorLabels`, `.serviceAccountName` all namespaced with the chart name.
   - `templates/deployment.yaml` — `imagePullPolicy: IfNotPresent`, fixed image tag, recommended labels via the `labels` helper, selector using only `selectorLabels` (immutable subset).
   - `templates/service.yaml` if a port was specified.
   - `templates/serviceaccount.yaml` gated on `.Values.serviceAccount.create`.
   - `templates/NOTES.txt`, `.helmignore`.
   - CRDs / RBAC additions exactly as in step 5.

### 3. Refactor mode (a sub-mode)

If the user, after a review, says "fix it" or "apply the suggestions", switch into refactor mode: apply the patches you proposed, file by file. After each file, briefly state what changed and which rule it satisfies. Re-run `helm lint` at the end.

## Output conventions

- **Always** prefer editing files in place over dumping large code blocks back into chat. Chat output is for the review report and decision-level summaries.
- **Quote the guide** when you cite a rule, so the user can see this is not a personal opinion. Each `references/*.md` file includes the exact upstream wording.
- **Don't moralize.** The guide is opinionated but pragmatic. If the user's chart deliberately deviates with a documented reason (e.g. a config-only chart that has no Pods), acknowledge it instead of forcing the rule.
- **Don't over-engineer.** A simple chart should stay simple. Don't add HPA, NetworkPolicies, PodDisruptionBudgets, or PodSecurityPolicies unless the user asked or the workload obviously needs them. The official guide is silent on those for a reason.

## Reading the references

Each file in `references/` is short (~50–120 lines) and has the same shape:

1. **Rules** — bullet list of the actual best-practice items, with the upstream phrasing where useful.
2. **Examples** — minimal "good vs. bad" snippets.
3. **Common mistakes** — what reviewers see in real charts.

**Open references lazily by mode** — don't read all eight up front. Each chapter is small but the total adds up to thousands of tokens, and most tasks only touch a few chapters.

- **Review mode** — read every chapter in order. A review by definition checks the chart against all eight, so reading them all is the cost of the job.
- **Generate mode** — first read `conventions.md`, `values.md`, `templates.md`, `labels.md`, `pods.md`. Only open `dependencies.md` if the user asked for sub-charts; `crds.md` if they asked for CRDs; `rbac.md` if they asked for RBAC.
- **Refactor mode** — open only the chapters that match the findings you're applying.
- **Answering a question** — open the one or two chapters the question is about. Quote from them; do not open the rest.

Read each file fully the first time you touch its topic in a session. After that you can rely on memory unless you need to quote.

## Why this skill is structured this way

- **Review and generate share a vocabulary.** The same eight chapters drive both modes, so we keep the rule content in `references/` and let SKILL.md focus on workflow.
- **Mechanical checks before judgment.** `helm lint` and label checks catch ~60% of issues. Doing them first lets the written report stay focused on the things that need a human-shaped argument.
- **Severity bucketing matches how teams actually triage.** "Must / Should / Consider" maps cleanly to a PR-review mindset and stops the report from feeling like a checklist of nits.
- **Bundled scripts > re-inventing them per run.** If every invocation re-wrote a label checker, that would be wasted work. `scripts/` is the place for these.

If you find yourself wanting to add new rules that aren't in the official guide (security hardening, resource limits, probes, etc.), tell the user explicitly that those are **beyond the upstream guide** and offer them as a separate, opt-in pass.
