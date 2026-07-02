# C5-LIFT-PMS Proof Obligations

Status: working target after exact diagnostics on 2026-07-01.

## Statement

For every all-length-5 K-component row `Q=(q0,...,q4)`, let

```text
s_i = Tw_C(q_i),
tau = 5m/N,
eta = N^2/25 - m,
A = {i : s_i > tau},
d(Q) = sum_{i notin A} (tau - s_i),
row_sum(Q)=sum_i s_i.
```

Target:

```text
row_sum(Q) + d(Q) <= N + (2/3) eta.      (C5-LIFT-PMS)
```

Equivalently:

```text
sum_i max(s_i,tau) <= N + (2/3) eta.
```

This implies C5-RS and hence the equal-length L=5 rowwise GERSH branch.
It keeps the correct threshold `tau=5m/N`; it is not the exact-false shifted
`HL` statement at threshold `N/5`.

## Algebraic Split

### Active-All-Five

If `A={0,1,2,3,4}`, then `d(Q)=0`, so C5-LIFT-PMS becomes

```text
row_sum(Q) <= N + (2/3) eta.             (PMS-5 row stability)
```

This is the sparse atom equality:

```text
N=10, m=3, eta=1,
s=[2,34/15,32/15,34/15,2],
row_sum=32/3=N+(2/3)eta.
```

Proof route: use the existing seven-cut/PMS-5 algebra or replace it by a
shorter row-sum stability proof. This branch is tight.

### Active-Proper

If `A` is a proper subset, the needed inequality is

```text
(row_sum(Q)-N) + d(Q) <= (2/3) eta.      (inactive absorption)
```

Here `d(Q)` is exactly the price of lifting inactive coordinates up to `tau`.
The exact diagnostics show this branch has positive slack in the current
battery; the closest local cases are active-4 rows, not the sparse atom.

A proof cannot use only the self-geodesic floor
`p_f(q_i)>=1/|cyc[f]|`; that floor kills the abstract one-spike vector but is
too weak by itself. It must be paired with shortest-geodesic/max-cut structure,
probably a layer-cake or side-door argument at the inactive coordinates.


## C5-Hom Tightness Split

Claude's 2026-07-01T14:29:16Z gate split C5-RS slack by C5-hom status on census `N<=11`:

```text
C5-HOM rows:     442932, min C5-RS slack = 0.
non-C5-HOM rows: 369157, min C5-RS slack = 1, overloaded rows = 0.
```

Interpretation:

1. The sharp/tight branch is C5-HOM. This is the natural domain for the seven-cut / weighted C5-model proof.
2. The non-C5-HOM branch is non-tight in exact census, but a fixed crude slack floor is not established; Claude scale stress on MycGrotzsch showed slack can shrink below the census floor. This branch still needs a real bound or a C5-superstructure reduction.
3. A proof of C5-LIFT-PMS may therefore split into:

```text
C5-HOM:     prove sharp row_sum+d <= N+(2/3)eta by weighted pentagonal stability.
non-C5-HOM: prove C5-RS/C5-LIFT by a genuine non-C5-hom argument, or reduce it to a C5-superstructure upper bound; do not rely on a constant slack floor.
```

The C5-HOM restriction must not be applied before proving that the considered row/component is in the tight branch; Grotzsch/Mycielskian remain guardrails against assuming C5-hom or constant slack for all length-5 components.

## Necessary Guardrails

1. Do not shift from `tau=5m/N` to `N/5`. Claude exact-falsified
   `sum_i(s_i-N/5)_+ <= eta`.
2. Do not assume every all-length-5 component has a C5 homomorphism; Grotzsch
   refutes this. C5-hom may only be used after proving an overload/C5-model
   bridge.
3. Do not claim seven-cut/PMS-5 implies C5-RS by sum control alone. Distribution
   matters; the abstract vector `s=(32/3,0,0,0,0)` shows the formal implication
   is false without row-regularity.

## Exact Evidence So Far

Local script:

```text
python problems/23/writeup/_codex_c5rs_inspect.py --min-n 8 --max-n 10
python problems/23/writeup/_codex_c5rs_inspect.py --skip-named --min-n 11 --max-n 11
python problems/23/writeup/_codex_c5rs_inspect.py --skip-census
```

Results:

```text
N=8..10 + named: rows=80320, lift_fails=0, min_lift_margin=0.
N=11 census: rows=1045374, lift_fails=0, min_lift_margin=14/25.
Named-only: rows=1436, lift_fails=0, min_lift_margin=19577/17325.
```

Pending: Claude full battery gate, including blowups/glued chains and stress
instances beyond the local script.


