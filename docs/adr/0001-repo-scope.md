# ADR 0001: Repository Scope

- Status: Accepted
- Date: 2026-05-02

## Context

This repository is being initialized with a minimal repository contract so future changes have a stable baseline for structure, validation, and CI.

The current top-level README is known to be inaccurate and is intentionally excluded from this contract. This ADR defines the minimal scope without relying on README content.

## Decision

The repository contract is limited to:

1. Ignore local-only, generated, secret, and build artifacts via `.gitignore`.
2. Keep repository-level architectural decisions under `docs/adr/`.
3. Validate the contract with `scripts/validate_repo_contract.py`.
4. Run the validation script in GitHub Actions on pull requests and pushes.

This contract does not introduce production configuration, deployment targets, infrastructure credentials, runtime secrets, or environment-specific settings.

## Scope

In scope:

- Documentation for repository-level decisions.
- Local development hygiene such as `.gitignore`.
- CI validation that checks repository contract files exist and avoids accidental README dependency.

Out of scope:

- Production deployment configuration.
- Infrastructure-as-code for production resources.
- Environment secrets or credentials.
- Application runtime implementation.
- README correction or rewrite.

## Consequences

- Future changes can extend the contract through additional ADRs and validation checks.
- CI provides an early guardrail without assuming application language, package manager, or deployment platform.
- README remediation remains a separate task and must not block this minimal contract.
