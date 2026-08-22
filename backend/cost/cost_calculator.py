"""Pure cost arithmetic — no I/O (C1 cost-calculator unit)."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Literal, Optional, TypedDict

DAYS_PER_MONTH = 30
HOURS_PER_MONTH_LIST = Decimal("730")

PieCategory = Literal["compute", "database", "network", "other"]
PIE_ORDER: tuple[PieCategory, ...] = ("compute", "database", "network", "other")
TWOPLACES = Decimal("0.01")
PRICED_STATUSES = frozenset({"priced", "manual_override"})


class LineForCalc(TypedDict, total=False):
    status: str
    hourly: Decimal
    hours: int
    category: str


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _require_finite_non_negative(name: str, value: Decimal) -> None:
    if not value.is_finite() or value < 0:
        raise ValueError(f"{name} must be non-negative finite Decimal")


def hourly_from_monthly(monthly: Decimal) -> Decimal:
    _require_finite_non_negative("monthly", monthly)
    return _quantize(monthly / HOURS_PER_MONTH_LIST)


def line_subtotal(hourly: Decimal, hours: int) -> Decimal:
    _require_finite_non_negative("hourly", hourly)
    if not isinstance(hours, int) or hours < 0:
        raise ValueError("hours must be int >= 0")
    if hours == 0:
        return Decimal("0.00")
    return _quantize(hourly * Decimal(hours) * Decimal(DAYS_PER_MONTH))


def _line_exact_subtotal(line: LineForCalc) -> Decimal:
    status = line.get("status")
    hourly = line.get("hourly")
    hours = line.get("hours")
    if status not in PRICED_STATUSES or hourly is None:
        return Decimal("0")
    if hours is None:
        raise ValueError("hours required for priced line")
    if not isinstance(hours, int) or hours < 0:
        raise ValueError("hours must be int >= 0")
    _require_finite_non_negative("hourly", hourly)
    if hours == 0:
        return Decimal("0")
    return hourly * Decimal(hours) * Decimal(DAYS_PER_MONTH)


def total_priced(lines: Iterable[LineForCalc]) -> Decimal:
    exact = sum((_line_exact_subtotal(line) for line in lines), Decimal("0"))
    return _quantize(exact)


def _normalize_category(category: Optional[str]) -> PieCategory:
    if category in PIE_ORDER:
        return category  # type: ignore[return-value]
    return "other"


def pie_buckets(lines: Iterable[LineForCalc]) -> dict[PieCategory, Decimal]:
    exact_buckets: dict[PieCategory, Decimal] = {k: Decimal("0") for k in PIE_ORDER}
    for line in lines:
        if line.get("status") not in PRICED_STATUSES:
            continue
        sub = _line_exact_subtotal(line)
        cat = _normalize_category(line.get("category"))
        exact_buckets[cat] += sub

    total_q = _quantize(sum(exact_buckets.values(), Decimal("0")))
    quantized = {k: _quantize(v) for k, v in exact_buckets.items()}
    diff_cents = int((total_q - sum(quantized.values(), Decimal("0"))) * 100)

    if diff_cents == 0:
        return quantized

    remainders = sorted(
        PIE_ORDER,
        key=lambda k: (
            exact_buckets[k] - quantized[k],
            -PIE_ORDER.index(k),
        ),
        reverse=True,
    )
    idx = 0
    while diff_cents > 0:
        key = remainders[idx % len(remainders)]
        quantized[key] += Decimal("0.01")
        diff_cents -= 1
        idx += 1

    return quantized


def is_overspent(total: Decimal, budget: Optional[Decimal]) -> bool:
    if budget is None:
        return False
    return total > budget
