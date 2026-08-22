#!/usr/bin/env python3
"""Pre-fetch AWS prices into Postgres ``pricing_cache`` (24h TTL)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if not BACKEND.is_dir():
    BACKEND = Path("/app")
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    deploy_env = ROOT / "deploy" / ".env"
    if deploy_env.is_file():
        _load_env_file(deploy_env)
    _load_env_file(BACKEND / ".env")

    if os.environ.get("COST_PRICING_STUB", "").strip() in ("1", "true", "yes"):
        print("COST_PRICING_STUB is set — skip warm (stub mode).", file=sys.stderr)
        return 1

    from cost.config import PRICING_URLS, REGIONS_BY_CLOUD
    from cost.price_cache import get_cached_hourly, write_cache
    from cost.pricing_client import PriceHit, PriceMiss, PriceUnsupported, fetch_hourly
    from database import SessionLocal

    aws_services = tuple(PRICING_URLS.get("default_products", {}).keys())
    gcp_services = tuple(PRICING_URLS.get("default_products_gcp", {}).keys())
    azure_services = tuple(PRICING_URLS.get("default_products_azure", {}).keys())
    aws_regions = list(REGIONS_BY_CLOUD.get("aws", []))
    gcp_regions = list(REGIONS_BY_CLOUD.get("gcp", []))
    azure_regions = list(REGIONS_BY_CLOUD.get("azure", []))
    db = SessionLocal()
    failed = 0
    try:
        now = datetime.now(timezone.utc)
        jobs = [
            ("aws", aws_services, aws_regions),
            ("gcp", gcp_services, gcp_regions),
            ("azure", azure_services, azure_regions),
        ]
        for cloud, services, regions in jobs:
            for region in regions:
                for service in services:
                    print(f"Fetching {cloud}/{service} @ {region} …", flush=True)
                    cached = get_cached_hourly(db, cloud, service, region, now=now)
                    if cached is not None:
                        print(f"  CACHED hourly={cached}")
                        continue
                    result = fetch_hourly(cloud, service, region)
                    if isinstance(result, PriceHit):
                        write_cache(
                            db,
                            cloud,
                            service,
                            region,
                            result.hourly,
                            result.fetched_at,
                        )
                        db.commit()
                        print(
                            f"  OK hourly={result.hourly} source={getattr(result, 'source', 'unknown')}"
                        )
                    elif isinstance(result, PriceMiss):
                        print("  MISS", file=sys.stderr)
                        failed += 1
                    else:
                        print("  UNSUPPORTED", file=sys.stderr)
                        failed += 1
    finally:
        db.close()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
