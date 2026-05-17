#!/usr/bin/env python3
"""Validate the Cloud-360 repository contract."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    ".gitignore",
    ".github/workflows/ci.yml",
    "aidlc-docs/inception/requirements/cloud-360-srs.md",
    "aidlc-docs/inception/application-design/system-architecture.md",
    "aidlc-docs/inception/user-stories/stories.md",
    "aidlc-docs/inception/user-stories/personas.md",
    "aidlc-docs/inception/decisions/0001-repo-scope.md",
    "aidlc-docs/inception/decisions/0002-agent-routing-layer.md",
    "aidlc-docs/inception/decisions/0003-web-based-experience.md",
    "aidlc-docs/inception/decisions/0004-mcp-skill-management.md",
    "aidlc-docs/inception/decisions/0005-bilingual-documentation.md",
    "aidlc-docs/inception/decisions/0006-adopt-aidlc-framework.md",
    "scripts/validate_repo_contract.py",
    "CLAUDE.md",
    ".aidlc-rule-details/VERSION",
    ".aidlc-rules/aws-aidlc-rules/core-workflow.md",
    ".aidlc-rule-details/extensions/bilingual-docs/bilingual-docs.md",
    ".aidlc-rule-details/extensions/security/baseline/security-baseline.md",
    ".aidlc-rule-details/extensions/testing/property-based/property-based-testing.md",
    "aidlc-docs/README.md",
    "aidlc-docs/aidlc-state.md",
    "aidlc-docs/audit.md",
    ".aidlc-overrides/README.md",
    ".aidlc-overrides/branch-naming.md",
    ".aidlc-overrides/decisions-log.md",
    "aidlc-docs/decisions-log.md",
)

REQUIRED_TEXT = {
    "README.md": (
        "Cloud-360",
        "AWS",
        "GCP",
        "Azure",
        "draw.io",
        "Mobile Web",
        "Cloud Security Posture",
        "human approval gate",
        "MCP & Skill Management",
    ),
    "aidlc-docs/inception/requirements/cloud-360-srs.md": (
        "AI Multi-Cloud Operations",
        "Cloud Security Posture & Policy Advisory",
        "Mobile Web",
        "MCP servers",
        "Terraform / OpenTofu",
        "MCP & Skill Management",
    ),
    "aidlc-docs/inception/application-design/system-architecture.md": (
        "Agent Routing Layer",
        "Cloud Operation Integration Layer",
        "draw.io",
        "Security Policy Advisor Agent",
        "MCP / Skill Registry",
    ),
    "aidlc-docs/inception/user-stories/stories.md": (
        "Architecture Design",
        "Cost Governance",
        "Security Compliance",
        "Mobile",
    ),
    "aidlc-docs/inception/user-stories/personas.md": (
        "Cloud Architect",
        "SRE",
        "Platform Engineer",
        "Security Reviewer",
    ),
    "aidlc-docs/inception/decisions/0001-repo-scope.md": (
        "Spec-Driven Development",
        "feature/cloud_architecture",
        "read-only",
    ),
    "aidlc-docs/inception/decisions/0002-agent-routing-layer.md": (
        "Routing Agent",
        "Security Policy Advisor Agent",
        "human approval",
    ),
    "aidlc-docs/inception/decisions/0003-web-based-experience.md": (
        "Web-first",
        "Mobile Web",
        "Native iOS app",
        "Native Android app",
    ),
    "aidlc-docs/inception/decisions/0004-mcp-skill-management.md": (
        "MCP and Skill Management",
        "Permission and Risk Classification",
        "Agent Routing Integration",
        "Health Checks",
    ),
    "aidlc-docs/inception/decisions/0005-bilingual-documentation.md": (
        "Bilingual Documentation",
        "## 中文版",
        "## English Version",
    ),
    "aidlc-docs/inception/decisions/0006-adopt-aidlc-framework.md": (
        "Adopt AIDLC",
        "AIDLC v0.1.8",
        "Hybrid",
        "extensions/security/baseline/",
        "extensions/testing/property-based/",
        "extensions/bilingual-docs/",
        "## 中文版",
        "## English Version",
    ),
    "CLAUDE.md": (
        "AIDLC",
        ".aidlc-rule-details/",
        ".aidlc-rules/aws-aidlc-rules/core-workflow.md",
        "Pre-enabled Extensions",
        "validate_repo_contract.py",
        "## 中文版",
        "## English Version",
    ),
    "aidlc-docs/aidlc-state.md": (
        "Project Type",
        "Brownfield",
        "Extension Configuration",
        "extensions/security/baseline/",
        "extensions/testing/property-based/",
        "extensions/bilingual-docs/",
        "## 中文版",
        "## English Version",
    ),
    "aidlc-docs/README.md": (
        "AIDLC",
        "Bilingual",
        "## 中文版",
        "## English Version",
    ),
    ".aidlc-overrides/README.md": (
        "Cloud-360 AIDLC Overrides",
        "## 中文版",
        "## English Version",
    ),
    ".aidlc-overrides/branch-naming.md": (
        "Branch Naming Convention",
        "<uploader>/<type>/<slug>",
        "feat",
        "fix",
        "docs",
        "chore",
        "refactor",
        "test",
        "danniel",
        "## 中文版",
        "## English Version",
    ),
    ".aidlc-overrides/decisions-log.md": (
        "Project Decisions Log Rule",
        "aidlc-docs/decisions-log.md",
        "explicit user request",
        "Trigger",
        "Decision",
        "## 中文版",
        "## English Version",
    ),
    "aidlc-docs/decisions-log.md": (
        "Project Decisions Log",
        "## 中文版",
        "## English Version",
    ),
}

FORBIDDEN_NEW_PATH_PARTS = {
    "prod",
    "production",
    "secrets",
}

FORBIDDEN_CONTENT_PATTERNS = (
    "BEGIN " + "PRIVATE KEY",
    "AWS_" + "SECRET_ACCESS_KEY",
    "AZURE_" + "CLIENT_SECRET=",
    "GOOGLE_" + "APPLICATION_CREDENTIALS=",
)


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def git_diff_name_only(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def validate_required_files() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        return fail("Missing required contract files: " + ", ".join(missing))
    return 0


def validate_required_text() -> int:
    violations: list[str] = []
    for rel_path, required_terms in REQUIRED_TEXT.items():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                violations.append(f"{rel_path} missing {term!r}")
    if violations:
        return fail("Required contract text missing: " + "; ".join(violations))
    return 0


def validate_docs_are_bilingual() -> int:
    """Bilingual enforcement applies to all AIDLC artifacts under aidlc-docs/."""
    violations: list[str] = []
    root_dir = ROOT / "aidlc-docs"
    if root_dir.is_dir():
        for path in sorted(root_dir.rglob("*.md")):
            rel_path = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "## 中文版" not in text or "## English Version" not in text:
                violations.append(rel_path)
    if violations:
        return fail(
            "Docs must include both '## 中文版' and '## English Version': "
            + ", ".join(violations)
        )
    return 0


def validate_no_production_config_added() -> int:
    changed_files = set(git_diff_name_only("--cached")) | set(git_diff_name_only())
    violations: list[str] = []

    for path in changed_files:
        parts = {part.lower() for part in Path(path).parts}
        if parts & FORBIDDEN_NEW_PATH_PARTS:
            violations.append(path)

    if violations:
        return fail(
            "Production/secret-scoped paths are out of scope for this contract: "
            + ", ".join(sorted(violations))
        )
    return 0


def validate_no_obvious_secrets() -> int:
    violations: list[str] = []
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_CONTENT_PATTERNS:
            if pattern in text:
                violations.append(f"{rel_path}: {pattern}")
    if violations:
        return fail("Forbidden secret-like content found: " + ", ".join(violations))
    return 0


def main() -> int:
    checks = (
        validate_required_files,
        validate_required_text,
        validate_docs_are_bilingual,
        validate_no_production_config_added,
        validate_no_obvious_secrets,
    )
    for check in checks:
        result = check()
        if result != 0:
            return result

    print("Cloud-360 repository contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
