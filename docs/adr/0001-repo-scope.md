# ADR 0001: Cloud-360 Repository Scope

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

- Status: Accepted
- Date: 2026-05-02

## Context

Cloud-360 is being defined through Spec-Driven Development before application implementation begins. The repository needs a clear contract so future changes can extend the platform safely without introducing production configuration, secrets, or uncontrolled cloud operations.

The platform vision is an AI-native multi-cloud architecture, governance, security and operations platform for Cloud Architects, SRE, FinOps and Security teams.

## Decision

This repository tracks the Cloud-360 SDD baseline:

1. Product README.
2. System Requirement Specification under `docs/srs/`.
3. System architecture documents under `docs/architecture/`.
4. User stories under `docs/user-stories/`.
5. Architecture Decision Records under `docs/adr/`.
6. Repository validation script under `scripts/`.
7. Baseline GitHub Actions CI under `.github/workflows/`.

Cloud-360 scope includes:

- AWS / GCP / Azure multi-cloud architecture design.
- Cross-cloud component selection.
- FinOps and cost estimation.
- Terraform / OpenTofu IaC generation.
- Operations optimization.
- AI Chat driven cloud management.
- Agentic AI proactive operations analysis.
- Cloud Security Posture & Policy Advisory.
- draw.io / diagrams.net compatible architecture canvas.
- Web-based desktop and mobile experience.

## Guardrails

The repository must not introduce the following without a future explicit ADR and approval:

- Plaintext cloud credentials or secrets.
- Production-specific deployment configuration.
- Direct production Terraform state or backend configuration.
- Autonomous destructive cloud actions.
- Unreviewed IAM/RBAC, firewall, KMS, storage policy or production-impacting changes.

All write/delete/deploy/permission-changing cloud operations must include:

- plan
- impact analysis
- affected resources
- rollback strategy
- verification steps
- human approval gate
- audit log

## Branch Collaboration Constraint

`feature/cloud_architecture` is a collaborative branch and must remain read-only unless Danniel explicitly authorizes modifications. Do not clean, rebase, force-push, delete, or rewrite that branch.

## Consequences

- README is now allowed to represent Cloud-360 product direction.
- SDD documents become the source of truth for initial implementation.
- CI validates that required contract documents exist and contain key platform concepts.
- Future implementation work should extend this contract through new ADRs and tests.

## English Version

Decision: this repository tracks the Cloud-360 Spec-Driven Development baseline, including the product README, SRS, architecture documents, user stories, ADRs, repository validation script, and baseline CI.

The repository scope includes AWS/GCP/Azure multi-cloud architecture design, component selection, FinOps, Terraform/OpenTofu generation, operations optimization, AI Chat driven cloud management, Agentic AI operations, security posture and policy advisory, draw.io/diagrams.net architecture canvas, Web-based desktop/mobile experience, and MCP/Skill lifecycle governance.

Guardrails: the repository must not contain plaintext cloud credentials, production-specific deployment configuration, direct production Terraform state, autonomous destructive cloud actions, or unreviewed production-impacting changes. The `feature/cloud_architecture` branch remains read-only unless explicitly authorized by Danniel.
