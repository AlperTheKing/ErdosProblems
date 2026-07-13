# Proposed OEIS A389182 extension

**Status:** Submitted to OEIS by the user on 2026-07-12; `b389182.txt`
uploaded. The draft is awaiting OEIS editor review.

The exact new terms are

```text
a(70)..a(80)  = 14 (11 terms)
a(81)..a(85)  = 15 (5 terms)
a(86)..a(100) = 16 (15 terms)
```

The C++20 branch-and-bound in `solve_bnb.cpp` returned `proof-complete` at
the six endpoints

```text
F(70)=F(80)=14,
F(81)=F(85)=15,
F(86)=F(100)=16.
```

The intervening values follow without further computation because `F` is
nondecreasing: an admissible subset of `[1,n]` remains admissible in
`[1,n+1]`. Candidate witnesses are rechecked from scratch by the solver.
The solver is independent of `solve_cpsat.py`; both engines agree on the
published range tested locally.

Reproduction:

```powershell
python problems\864\compute\make_oeis_extension.py
powershell -ExecutionPolicy Bypass -File problems\864\compute\run_oeis_endpoints.ps1 -Threads 32
```

Suggested OEIS edit text:

```text
Additional terms a(70)-a(100) from Alper Ferudun, Jul 12 2026. Exact C++
branch-and-bound gives a(70)=a(80)=14, a(81)=a(85)=15, and
a(86)=a(100)=16; monotonicity supplies the intervening terms. The search
uses unordered pairs including diagonals and permits one repeated sum value
with unrestricted multiplicity.
```

Submitted artifacts:

```text
b-file: b389182.txt
SHA-256: E83444A9BD2D070420D013B1D293EDF93B443E4C5627D846342BFC7173B43205
endpoint certificates: oeis_endpoint_certificates.jsonl
```

No further OEIS action is needed unless an editor requests a revision or a
stable public source URL.
