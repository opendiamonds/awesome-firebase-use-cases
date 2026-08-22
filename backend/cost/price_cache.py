"""Postgres pricing_cache access (C1 查價持久層，TTL 24h).

cost_service 估價流程：
  1. ``get_cached_hourly(cloud, sku, region)`` — 命中則直接用
  2. miss → ``pricing_client.fetch_hourly``（AWS SDK Query API → Bulk API）
  3. hit → ``write_cache`` 寫入本表，供後續同元件／同區域重用
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from models import PricingCache

TTL = timedelta(hours=24)


def get_cached_hourly(
    db: Session, cloud: str, sku: str, region: str, now: Optional[datetime] = None
) -> Optional[Decimal]:
    now = now or datetime.now(timezone.utc)
    row = (
        db.query(PricingCache)
        .filter(
            PricingCache.cloud == cloud,
            PricingCache.sku == sku,
            PricingCache.region == region,
        )
        .first()
    )
    if row is None:
        return None
    fetched = row.fetched_at
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    if now - fetched >= TTL:
        return None
    return Decimal(str(row.hourly))


def write_cache(
    db: Session,
    cloud: str,
    sku: str,
    region: str,
    hourly: Decimal,
    fetched_at: datetime,
) -> None:
    row = (
        db.query(PricingCache)
        .filter(
            PricingCache.cloud == cloud,
            PricingCache.sku == sku,
            PricingCache.region == region,
        )
        .first()
    )
    if row is None:
        db.add(
            PricingCache(
                cloud=cloud,
                sku=sku,
                region=region,
                hourly=hourly,
                fetched_at=fetched_at,
            )
        )
    else:
        row.hourly = hourly
        row.fetched_at = fetched_at
    db.flush()
