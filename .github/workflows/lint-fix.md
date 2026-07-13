---
description: "Lint Fixer — auto-fix the safe, mechanical frontend lint errors on a PR and flag the risky ones for a human."

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: read

engine: copilot

timeout-minutes: 20

network: defaults

# Deterministic first: apply any auto-fixable rules with eslint --fix, then
# capture what remains as JSON for the agent. The agent only handles what
# --fix cannot.
pre-agent-steps:
  - uses: actions/checkout@v4

  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: npm
      cache-dependency-path: frontend/package-lock.json

  - name: Install dependencies
    working-directory: frontend
    run: npm ci

  - name: Apply auto-fixable lint rules
    working-directory: frontend
    continue-on-error: true
    run: npx eslint . --fix

  - name: Capture remaining lint problems as JSON
    working-directory: frontend
    continue-on-error: true
    run: npx eslint . -f json -o eslint-report.json

tools:
  edit:
  bash:
    - "npm run lint"
    - "npm run build"
    - "npx eslint"
    - "git diff"
    - "cat"
    - "head"
    - "tail"
    - "grep"
    - "ls"
    - "wc"

safe-outputs:
  add-comment:
    max: 1
    target: triggering
  push-to-pull-request-branch:
    target: triggering
    max: 1
---

# Lint Fixer

You fix the **safe, mechanical** ESLint errors in the Cloud-360 frontend (`frontend/`) on this pull request, and you leave the risky ones alone. The point is to clear the trivial noise automatically without ever touching logic a human must review.

The remaining problems (after `eslint --fix` already ran) are in `frontend/eslint-report.json`. Read it. It is the authoritative list — do not go hunting for other things to change.

## What you MAY fix

Only these rule categories, and only when the fix is unambiguous:

- **`@typescript-eslint/no-unused-vars`** — remove the unused binding, or, when it is a required callback/catch parameter that genuinely cannot be dropped, rename it with a leading underscore.
- **`@typescript-eslint/no-explicit-any`** — replace `any` with the concrete type **only when the correct type is obvious from the surrounding code** (e.g. the shape is constructed a few lines away, or an existing interface fits). If the right type is not obvious, do NOT guess `unknown` or invent a type — leave it and report it.
- Other purely-syntactic rules where the fix cannot change behaviour.

## What you MUST NOT touch

These are off limits no matter what the report says. They change runtime behaviour or component structure and a frontend owner must review them:

- **`react-hooks/set-state-in-effect`** — do not rewrite `useEffect` bodies. One of these is the auth bootstrap that reads the token from `localStorage`; a wrong "fix" silently breaks login.
- **`react-hooks/exhaustive-deps`** — do not edit hook dependency arrays. Changing them changes when effects run.
- **`react-refresh/only-export-components`** — do not split files or move exports (e.g. pulling `useAuth` out of the context module). That ripples through every import.
- Anything in `backend/`, tests, config, or CI. This workflow is frontend lint only.

If you are unsure whether a fix is safe, it is not. Leave it.

## After fixing

1. Run `npm run build` in `frontend/` (that is `tsc -b && vite build`). If your change does not compile, it is wrong — revert it. Never push code that fails to build.
2. Re-run `npm run lint` to confirm the mechanical errors you targeted are gone.
3. If you changed nothing, push nothing.

## Deliver

- If you fixed anything, push it to this PR's branch.
- Post exactly one comment, bilingual (Traditional Chinese first, then English):
  1. **Auto-fixed** — each error you fixed: the file, the rule, and what you changed, in one line.
  2. **Needs a human** — each error you deliberately left, with the rule and why it needs review (touches auth/effects/exports). Point at issue #427 if it tracks them.
  3. If the build or a re-run of lint still shows errors you could not safely fix, say so plainly — do not imply the PR is now green when it is not.

No preamble, no restating these instructions. If there were no fixable errors, say so in one line per language and stop.
