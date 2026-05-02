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
    "docs/srs/cloud-360-srs.md",
    "docs/sa/software-architecture.md",
    "docs/sd/software-design.md",
    "docs/architecture/system-architecture.md",
    "docs/user-stories/core-pillars.md",
    "docs/adr/0001-repo-scope.md",
    "docs/adr/0002-agent-routing-layer.md",
    "docs/adr/0003-web-based-experience.md",
    "docs/README.md",
    "docs/adr/0004-mcp-skill-management.md",
    "docs/adr/0005-bilingual-documentation.md",
    "scripts/validate_repo_contract.py",
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
    "docs/srs/cloud-360-srs.md": (
        "AI Multi-Cloud Operations",
        "Cloud Security Posture & Policy Advisory",
        "Mobile Web",
        "MCP servers",
        "Terraform / OpenTofu",
        "MCP & Skill Management",
    ),
    "docs/sa/software-architecture.md": (
        "Software Architecture",
        "Cloud-360 Custom Router",
        "LangGraph",
        "n8n + OpenRouter",
        "NVIDIA Developer / NIM",
        "Anthropic OAuth",
        "OpenAI OAuth",
        "ADK",
        "Human Approval Gate",
    ),
    "docs/sd/software-design.md": (
        "Software Design",
        "Single repo / modular folders",
        "FastAPI",
        "Nuxt",
        "AgentRouteRequest",
        "AgentRouteDecision",
        "LLMProvider",
        "Runtime Selection Rule",
    ),
    "docs/architecture/system-architecture.md": (
        "Agent Routing Layer",
        "Cloud Operation Integration Layer",
        "draw.io",
        "Security Policy Advisor Agent",
        "MCP / Skill Registry",
    ),
    "docs/user-stories/core-pillars.md": (
        "Architecture Design",
        "Cost Estimation & FinOps",
        "Cloud Security Posture",
        "Mobile Web",
        "MCP & Skill Management",
    ),
    "docs/adr/0001-repo-scope.md": (
        "Spec-Driven Development",
        "feature/cloud_architecture",
        "read-only",
    ),
    "docs/adr/0002-agent-routing-layer.md": (
        "Routing Agent",
        "Security Policy Advisor Agent",
        "human approval",
    ),
    "docs/adr/0003-web-based-experience.md": (
        "Web-first",
        "Mobile Web",
        "Native iOS app",
        "Native Android app",
    ),
    "docs/adr/0004-mcp-skill-management.md": (
        "MCP and Skill Management",
        "Permission and Risk Classification",
        "Agent Routing Integration",
        "Health Checks",
    ),
    "docs/adr/0005-bilingual-documentation.md": (
        "Bilingual Documentation",
        "## 中文版",
        "## English Version",
    ),
    "docs/README.md": (
        "Cloud-360 Documentation",
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
    violations: list[str] = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
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
