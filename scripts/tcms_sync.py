#!/usr/bin/env python3
"""把 AI-DLC `tcms-test-cases` stage 產出的手動測案同步到 Kiwi TCMS。

輸入是該 stage 的 artifact `manual-test-cases.md`；輸出是 TCMS 上的測試案例。
以案例標題為鍵，可重複執行：已存在的更新、不存在的建立，不會產生重複案例。

    python3 scripts/tcms_sync.py --file <path> --dry-run   # 預覽，不寫入
    python3 scripts/tcms_sync.py --file <path>             # 實際寫入

前置：
    pip install tcms-api
    ~/.tcms.conf：
        [tcms]
        url = https://tcms.danniel.cc/xml-rpc/
        username = <帳號>
        password = <密碼>

格式契約見 `aidlc/spaces/<space>/knowledge/aidlc-quality-agent/test-case-authoring.md`。
本檔的解析器與該文件的「解析規則」一節必須一致；改其一就要改另一個。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PRODUCT_NAME = "Cloud-360"
TAG = "Cloud-360"
DEFAULT_PRIORITY = "P2"

CASE_HEADING = re.compile(r"^##\s+TC:\s*(?P<summary>.+?)\s*$")
META_LINE = re.compile(r"^-\s*(?P<key>plan|priority)\s*:\s*(?P<value>.+?)\s*$")
SECTION_HEADING = re.compile(r"^###\s+")


@dataclass
class Case:
    summary: str
    plan: str | None = None
    priority: str = DEFAULT_PRIORITY
    body_lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(self.body_lines).strip()


def parse(path: Path) -> list[Case]:
    """把 manual-test-cases.md 解析成案例清單。

    格式錯誤一律當場報錯而不是跳過：一個沒被解析到的案例，在 TCMS 上看起來
    就跟「沒寫過」一模一樣，而這正是本工具要防的失敗模式。
    """
    cases: list[Case] = []
    current: Case | None = None
    in_body = False

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        heading = CASE_HEADING.match(raw)
        if heading:
            current = Case(summary=heading.group("summary"))
            cases.append(current)
            in_body = False
            continue

        if current is None:
            continue  # 第一個案例標題之前的內容（檔案標題、前言）不屬於任何案例

        if SECTION_HEADING.match(raw):
            in_body = True

        if not in_body:
            meta = META_LINE.match(raw)
            if meta:
                key, value = meta.group("key"), meta.group("value")
                if key == "plan":
                    current.plan = value
                else:
                    if value not in ("P1", "P2", "P3"):
                        raise SystemExit(
                            f"{path}:{lineno}: priority 必須是 P1／P2／P3，得到 {value!r}"
                        )
                    current.priority = value
                continue
            if raw.strip():
                raise SystemExit(
                    f"{path}:{lineno}: 案例 {current.summary!r} 的標題與第一個 '###' 之間"
                    f"只能有 '- plan:' 與 '- priority:'，得到 {raw.strip()!r}"
                )
            continue

        current.body_lines.append(raw)

    problems = []
    for case in cases:
        if not case.text:
            problems.append(f"  案例 {case.summary!r} 沒有任何內容段落（缺 '###' 小節）")
        if not case.plan:
            problems.append(f"  案例 {case.summary!r} 缺 '- plan:'")
    if problems:
        raise SystemExit(f"{path} 格式有誤：\n" + "\n".join(problems))

    seen: dict[str, int] = {}
    for case in cases:
        seen[case.summary] = seen.get(case.summary, 0) + 1
    duplicates = [s for s, n in seen.items() if n > 1]
    if duplicates:
        raise SystemExit(
            "案例標題重複（標題是同步鍵，重複會讓其中一個覆寫另一個）：\n  "
            + "\n  ".join(duplicates)
        )

    return cases


def connect():
    """建立 TCMS 連線。缺設定檔時明確失敗，不靜默跳過。"""
    conf = Path.home() / ".tcms.conf"
    if not conf.exists():
        raise SystemExit(
            f"找不到 {conf}。同步不會被靜默跳過——請先建立設定檔：\n\n"
            "    umask 077\n"
            "    read -p 'TCMS 帳號: ' U && read -s -p 'TCMS 密碼: ' P && echo && \\\n"
            "    printf '[tcms]\\nurl = https://tcms.danniel.cc/xml-rpc/\\n"
            "username = %s\\npassword = %s\\n' \"$U\" \"$P\" > ~/.tcms.conf && \\\n"
            "    unset U P\n"
        )
    try:
        from tcms_api import TCMS
    except ImportError:
        raise SystemExit("缺少 tcms-api 套件。安裝：pip install tcms-api") from None
    return TCMS().exec


def sync(cases: list[Case], *, dry_run: bool) -> int:
    rpc = connect()
    prefix = "[dry-run] " if dry_run else ""

    products = rpc.Product.filter({"name": PRODUCT_NAME})
    if not products:
        raise SystemExit(f"TCMS 上找不到 Product {PRODUCT_NAME!r}")
    pid = products[0]["id"]

    versions = rpc.Version.filter({"product": pid})
    if not versions:
        raise SystemExit(f"Product {PRODUCT_NAME!r} 沒有任何 Version")
    version = versions[0]

    categories = rpc.Category.filter({"product": pid})
    if not categories:
        raise SystemExit(f"Product {PRODUCT_NAME!r} 沒有任何 Category")
    category = categories[0]

    priorities = {p["value"]: p["id"] for p in rpc.Priority.filter({})}
    statuses = rpc.TestCaseStatus.filter({})
    confirmed = next((s for s in statuses if s.get("is_confirmed")), statuses[0])
    plan_types = rpc.PlanType.filter({})
    plan_type = next(
        (t for t in plan_types if t["name"].lower() in ("function", "functional", "manual")),
        plan_types[0],
    )

    # --- TestPlan：需要哪些就建哪些 ---
    wanted_plans = sorted({c.plan for c in cases if c.plan})
    existing_plans = {p["name"]: p["id"] for p in rpc.TestPlan.filter({"product": pid})}
    plan_ids: dict[str, int | None] = {}
    for name in wanted_plans:
        if name in existing_plans:
            plan_ids[name] = existing_plans[name]
            print(f"{prefix}plan     已存在 {name} (id={existing_plans[name]})")
        elif dry_run:
            plan_ids[name] = None
            print(f"{prefix}plan     將建立 {name}")
        else:
            created = rpc.TestPlan.create(
                {
                    "name": name,
                    "product": pid,
                    "product_version": version["id"],
                    "type": plan_type["id"],
                    "is_active": True,
                }
            )
            plan_ids[name] = created["id"]
            print(f"plan     已建立 {name} (id={created['id']})")

    # --- TestCase ---
    existing_cases = {
        c["summary"]: c for c in rpc.TestCase.filter({"category__product": pid})
    }
    created_n = updated_n = 0

    for case in cases:
        payload = {
            "summary": case.summary,
            "category": category["id"],
            "priority": priorities.get(case.priority, priorities[DEFAULT_PRIORITY]),
            "case_status": confirmed["id"],
            # 手動案例必須是 False，才與 junit plugin 回寫的自動化案例區分得開。
            "is_automated": False,
            "text": case.text,
            "notes": "手動測案，來源為 AI-DLC tcms-test-cases stage 的 manual-test-cases.md。",
        }
        found = existing_cases.get(case.summary)

        if dry_run:
            verb = "將更新" if found else "將建立"
            print(f"{prefix}case     {verb} [{case.priority}] {case.summary[:56]}")
            created_n += 0 if found else 1
            updated_n += 1 if found else 0
            continue

        if found:
            rpc.TestCase.update(found["id"], payload)
            case_id = found["id"]
            updated_n += 1
            print(f"case     已更新 id={case_id} {case.summary[:50]}")
        else:
            case_id = rpc.TestCase.create(payload)["id"]
            created_n += 1
            print(f"case     已建立 id={case_id} {case.summary[:50]}")

        rpc.TestCase.add_tag(case_id, TAG)
        plan_id = plan_ids.get(case.plan or "")
        if plan_id:
            try:
                rpc.TestPlan.add_case(plan_id, case_id)
            except Exception as exc:  # 已在計畫內時 API 會報錯，視為冪等成功
                if "already" not in str(exc).lower():
                    print(f"    ! 加入計畫失敗 case={case_id} plan={plan_id}: {exc}")

    print()
    print(f"{prefix}完成：新增 {created_n} 筆，更新 {updated_n} 筆，共 {len(cases)} 筆")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="manual-test-cases.md 的路徑（tcms-test-cases stage 的 artifact）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只列出將要建立／更新的內容，不連線寫入",
    )
    args = parser.parse_args()

    if not args.file.exists():
        raise SystemExit(f"找不到檔案：{args.file}")

    cases = parse(args.file)
    if not cases:
        raise SystemExit(f"{args.file} 沒有解析到任何案例（案例標題格式為 '## TC: <標題>'）")

    print(f"解析到 {len(cases)} 個案例：")
    for case in cases:
        print(f"  [{case.priority}] {case.summary}")
        print(f"        plan={case.plan}  text={len(case.text)} 字元")
    print()

    return sync(cases, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
