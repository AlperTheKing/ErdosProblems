from functools import lru_cache


def qsum(m, e):
    e = min(e, m // 2)
    return (e * (e + 1) + (m - e) * (m - e + 1)) // 2


def baseline(m, e):
    e = min(e, m // 2)
    return [x for i in range(1, e + 1) for x in (i, i)] + list(
        range(e + 1, m - e + 1)
    )


@lru_cache(maxsize=None)
def incidence_profiles(n):
    lambdas = [0] * (n - 1)
    profiles = []
    for width in range(1, n):
        for target in range(1, n):
            lo = max(0, target - width)
            hi = min(target - 1, n - width - 1)
            lambdas[target - 1] += max(0, hi - lo + 1)
        ordered = tuple(sorted(lambdas))
        profiles.append(
            (
                ordered,
                max(ordered),
                width * n - width * (width + 1) // 2,
            )
        )
    return tuple(profiles)


@lru_cache(maxsize=None)
def span_lower(n, e):
    answer = 0
    weights = baseline(n - 1, e)
    base = qsum(n - 1, e)
    for lambdas, cap, selected in incidence_profiles(n):
        weighted = sum(x * y for x, y in zip(lambdas, weights))
        extra = max(0, qsum(selected, e) - weighted)
        answer = max(answer, base + (extra + cap - 1) // cap)
    return answer


bad = []
for delta in (0, 1):
    for p in range(1, 100):
        if p + delta < 2:
            continue
        core = 2 * p + delta
        for residual in range(max(1, 2 * core - 4), 500):
            excess = p * (p + delta - 1)
            extracted = residual + p + 1
            four_target = (
                4 * p * (p + delta)
                + 2 * core * residual
                + 3 * residual * (residual + 1)
            )
            gap4 = 4 * extracted * extracted - four_target
            if gap4 > 0 and gap4 * gap4 >= 144 * extracted**3:
                continue
            lower = max(
                span_lower(core + residual, excess),
                span_lower(extracted, 0),
            )
            if 4 * lower < four_target:
                bad.append((p, delta, residual))

expected = (
    [(1, 1, u) for u in range(2, 27)]
    + [(2, 0, u) for u in range(4, 18)]
    + [(2, 1, u) for u in range(6, 12)]
)
assert sorted(bad) == sorted(expected)
print({"exceptional_parameter_triples": len(bad), "triples": sorted(bad)})
