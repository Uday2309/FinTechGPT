from datetime import date
from math import isfinite


def xnpv(rate: float, cashflows: list[tuple[date, float]]) -> float:
    start = cashflows[0][0]
    return sum(cf / ((1 + rate) ** ((d - start).days / 365.0)) for d, cf in cashflows)


def xirr(cashflows: list[tuple[date, float]]) -> float | None:
    cashflows = sorted(cashflows, key=lambda x: x[0])
    if len(cashflows) < 2:
        return None
    if not (any(v < 0 for _, v in cashflows) and any(v > 0 for _, v in cashflows)):
        return None

    low, high = -0.9999, 10.0
    f_low = xnpv(low, cashflows)
    f_high = xnpv(high, cashflows)
    attempts = 0
    while f_low * f_high > 0 and attempts < 8:
        high *= 2
        f_high = xnpv(high, cashflows)
        attempts += 1

    if f_low * f_high > 0:
        return None

    for _ in range(200):
        mid = (low + high) / 2
        f_mid = xnpv(mid, cashflows)
        if abs(f_mid) < 1e-7:
            return mid
        if f_low * f_mid <= 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid

    result = (low + high) / 2
    return result if isfinite(result) else None
