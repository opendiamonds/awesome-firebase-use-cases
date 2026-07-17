---
description: "Doc Sync — detect when code has drifted from the AIDLC specs and open a PR that closes the gap."

on:
  push:
    branches:
      - ut
    paths:
      - "backend/**"
      - "frontend/**"
      - "deploy/**"
      - "schema*.sql"
  workflow_dispatch:

permissions:
  contents: read

engine: copilot

timeout-minutes: 25

network: defaults

tools:
  edit:
  bash:
    - "python3"
    - "git diff"
    - "git log"
    - "git show"
    - "grep"
    - "ls"
    - "cat"
    - "head"
    - "tail"
    - "wc"
  github:
    toolsets: [context, repos]

safe-outputs:
  create-pull-request:
    title-prefix: "docs(sync): "
    labels: [documentation, doc-sync]
    max: 1
---

# Doc Sync

The specs in `aidlc-docs/` are the product of this repository, not a byproduct. When code changes and the specs do not, the specs quietly become fiction. You close that gap.

You run after a push to `ut` that touched `backend/`, `frontend/`, `deploy/`, or a schema file.

## Step 1 — See what changed

```
git log -1 --stat
git diff HEAD~1...HEAD
```

## Step 2 — Find what the change contradicts

Read the specs that claim to describe the code you just saw change:

- `aidlc-docs/inception/application-design/frontend-backend-specification.md` — API contracts, component design, ORM models
- `aidlc-docs/construction/database-schema.md` — tables, columns, relationships
- `aidlc-docs/inception/requirements/cloud-360-srs.md` — requirements
- `aidlc-docs/inception/user-stories/stories.md` — stories
- `DEPLOY.md` — deployment steps, environment variables

Look for statements that the diff has made **false**. Concrete drift only:

- An API route was added, removed, or its request/response shape changed, and the spec still documents the old one.
- A database table or column changed, and `database-schema.md` still lists the old shape.
- A new environment variable is required, and `DEPLOY.md` or `.env.example` does not mention it.
- A component or service was added or removed, and the architecture section does not know about it.

## Step 3 — Fix it, or say nothing

If you found drift, open **one** pull request that corrects the affected documents.

- Change only what the diff made false. This is not an opportunity to rewrite, reorganise, or improve the prose. A doc-sync PR that touches sections unrelated to the code change will be closed.
- Every `aidlc-docs/**/*.md` you touch must keep both `## 中文版` and `## English Version` in sync. If you correct a fact in one language, correct it in the other. Both halves carry the same substance — a heading over an empty body is not a translation, and `scripts/validate_repo_contract.py` only greps for the headings, so it will not catch you. Do it properly anyway.
- Run `python3 scripts/validate_repo_contract.py` before you finish and make sure it still passes.

The PR body states, bilingually: what changed in the code, which documents were contradicted by it, and what you corrected. One bullet per document.

**If you found no drift, do nothing.** No pull request, no empty commit, no "everything looks fine" PR. Silence is the correct output when the specs already match the code, and manufacturing a PR to look productive wastes a human's review time.
