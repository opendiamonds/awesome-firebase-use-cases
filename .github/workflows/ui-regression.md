---
description: "UI Regression — run the Playwright suite against an ephemeral stack on every PR and report the failing cases."

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: read

engine: copilot

timeout-minutes: 30

network: defaults

# Deterministic work runs here, before the agent: build the stack, run
# Playwright, tear the stack down. The agent's only job is to read the JSON
# report and explain the failures — it never runs the tests itself.
pre-agent-steps:
  - uses: actions/checkout@v4

  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: npm
      cache-dependency-path: frontend/package-lock.json

  - name: Build and start the ephemeral test stack
    env:
      POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
      JWT_SECRET: ${{ secrets.JWT_SECRET }}
    run: |
      docker compose -f deploy/docker-compose.test.yml up -d --build

  - name: Wait for the stack to answer on 8090
    run: |
      for i in $(seq 1 40); do
        if curl -fsS -o /dev/null http://localhost:8090/; then
          echo "stack up"; exit 0
        fi
        sleep 5
      done
      echo "stack did not come up on 8090" >&2
      docker compose -f deploy/docker-compose.test.yml ps
      docker compose -f deploy/docker-compose.test.yml logs --tail=100
      exit 1

  - name: Install Playwright and browsers
    working-directory: frontend
    run: |
      npm ci
      npx playwright install --with-deps chromium

  - name: Run the regression suite
    working-directory: frontend
    id: playwright
    # continue-on-error so a failing suite still lets the agent comment; the
    # red gate is re-asserted in post-steps after the comment is posted.
    continue-on-error: true
    env:
      BASE_URL: http://localhost:8090
      PW_RUN_ID: ${{ github.run_id }}
    run: npx playwright test

# The report lives at frontend/pw-report.json (see playwright.config.ts). Let
# the agent read it with these bash tools; it needs nothing else.
tools:
  bash:
    - "cat"
    - "ls"
    - "head"
    - "tail"
    - "grep"
    - "wc"

safe-outputs:
  add-comment:
    max: 1
    target: triggering

# Cleanup first (always), then re-raise the failure so the PR check goes red
# when tests failed — the comment is informational, this is the gate.
post-steps:
  - name: Tear down the test stack
    if: always()
    run: docker compose -f deploy/docker-compose.test.yml down -v || true

  - name: Fail the job if any test failed
    if: always()
    working-directory: frontend
    run: |
      if [ ! -f pw-report.json ]; then
        echo "no Playwright report produced — the suite did not run" >&2
        exit 1
      fi
      # Playwright's json reporter records the failure count in stats.unexpected
      # (a retried-then-passed test is stats.flaky, which we allow). Read it
      # authoritatively rather than grepping the nested results.
      unexpected=$(jq '.stats.unexpected' pw-report.json)
      flaky=$(jq '.stats.flaky' pw-report.json)
      echo "unexpected=${unexpected} flaky=${flaky}"
      if [ "${unexpected}" != "0" ]; then
        echo "Playwright reported ${unexpected} failing test(s)" >&2
        exit 1
      fi
      echo "all Playwright tests passed"
---

# UI Regression Reporter

An ephemeral copy of the Cloud-360 stack was just built from this pull request and driven by the Playwright regression suite. Your job is to read the machine-readable result and tell the author, in one PR comment, exactly what failed and why — nothing more.

## Read the result

The JSON report is at `frontend/pw-report.json` (Playwright's `json` reporter). Read it. Its structure nests `suites[].specs[].tests[].results[]`; each spec has a `title` and an `ok` boolean, and failed results carry an `error` with a `message` and a `snippet`.

Do not run any tests yourself, and do not trust the surrounding CI logs over the report — the JSON is the source of truth for what passed and failed.

## Comment

Post exactly one comment, bilingual (Traditional Chinese first, then English).

- **If every test passed**, say so in one line per language, and stop. Do not list the passing cases.
- **If any test failed**, lead with the count (e.g. "2 of 6 UI regression tests failed"). Then, one bullet per failed test:
  - the test title (the human-readable spec name, e.g. *"admin logs in and reaches the workspace"*),
  - the assertion or error that failed, quoted from the report's `error.message` — trimmed to the meaningful line, not the whole stack,
  - if the message makes the cause obvious (a selector that no longer matches, a navigation that did not happen, a timeout), say so in a few words. If it does not, say what the test was checking and stop — do not invent a root cause you cannot see in the report.

Keep it tight and factual. No preamble, no restating these instructions, no praise, no advice about how to fix beyond what the error plainly implies. The author wants to know which cases broke and what the failure was, so they can open the trace — that is the whole deliverable.
