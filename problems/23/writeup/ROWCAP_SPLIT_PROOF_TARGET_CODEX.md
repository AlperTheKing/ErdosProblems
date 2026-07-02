# Row-Cap Split Proof Target

Status: exact-supported, not proved.  This note records the current cleanest
route from rowwise GERSH to component CV.

## Definitions

Fix a connected-B gamma-minimum maximum cut.  Let `M` be the bad edges, and
let `cyc[f]` be the set of shortest B-geodesic rows for `f`.

For a K-component `C`, define the unit load

```text
Tw_C(v) = sum_{g in M_C} #{Q in cyc[g] : v in Q} / |cyc[g]|.
```

Let

```text
eta = N^2/25 - |M|,
A = N + eta.
```

The rowwise GERSH target is

```text
sum_{v in Q} Tw_C(v) <= A
```

for every bad edge `f in M_C` and every row `Q in cyc[f]`.

## Implication Chain

The exact algebra in `CV_PERCOMP_SPECTRAL.md` gives:

```text
ROWWISE-GERSH
  => GERSH
  => (N+eta)D - O_C is PSD for every K-component
  => component CV: sum_{v in C} T(v)^2 <= (N+eta) * Gamma_C
```

The live split proves ROWWISE-GERSH by row length:

```text
LONG-SURPLUS:
if |Q| > 5, then
    sum_{v in Q} Tw_C(v)
    <= N + eta/2 - (|Q|^2-25)/50.
```

```text
PMS-5:
if |Q| = 5, then
    sum_{v in Q} Tw_C(v) <= N + (2/3) eta.
```

Since `1/2 <= 1` and `2/3 <= 1`, these imply rowwise GERSH.

## Exact Gates

### NON5-HALF

```text
python problems/23/writeup/_codex_rowcap_non5_half_gate.py \
  --fast --min-n 7 --max-n 11 --two-lane-max 30 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
L>5 rows checked = 19832
NON5-HALF violations = 0
LONG-SURPLUS violations = 0
min margin = 12/25 at C7[1]
min LONG-SURPLUS margin = 0 at C7[1]
```

The first pure odd-cycle margins are:

```text
C7[1]:  12/25
C9[1]:  28/25
C11 row: 48/25
```

For a pure odd cycle of length `L`, the NON5-HALF margin is

```text
L + (L^2/25 - 1)/2 - L = L^2/50 - 1/2.
```

Equivalently, `LONG-SURPLUS` is tight on pure odd cycles:

```text
N + eta/2 - rowvalue - (L^2-25)/50 = 0.
```

Direct stress avoiding expensive `gmins` calls on large known-cut families:

```text
python problems/23/writeup/_codex_rowcap_non5_half_direct_stress.py
```

Result:

```text
L>5 rows checked = 127540
NON5-HALF violations = 0
LONG-SURPLUS violations = 0
min NON5-HALF margin = 12/25 at direct-C7[1]
min LONG-SURPLUS margin = 0 at direct-C7[1]
LONG-SURPLUS equality at pure C7[1], C9[1], C11[1], C13[1]
two-lane checked through L=100
```

### Row-Overload Classifier

```text
python problems/23/writeup/_codex_rowcap_overload_classify.py \
  --fast --min-n 7 --max-n 11 --two-lane-max 30 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
rows checked = 1148058
rows with rowvalue > N = 131
max (rowvalue-N)/eta = 2/3 at I?BD@g]Qo
census N=11 adds 0 over-N rows
```

The non-5 over-N rows are sparse diagnostics with large deficit reserve.  The
worst observed row-cap ratio remains the N=10 pentagonal PMS equality atom.

### Dead Coarse Shortcut

The trivial overlap estimate

```text
sum_{v in Q} Tw_C(v)
  <= sum_{g in M_C} min(|Q|, ell(g))
```

is too coarse to prove NON5-HALF:

```text
python problems/23/writeup/_codex_rowcap_coarse_budget_gate.py \
  --fast --min-n 7 --max-n 10 --two-lane-max 30 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
non-5 violations = 5654
first = C7[2]
min margin = -834/25 at C7[3]
```

Thus NON5-HALF needs genuine geodesic anti-concentration, not only the bound
`|Q cap P| <= min(|Q|,|P|)`.

## PMS-5 Reuse

The older OC-PMS target states, in the global length-5 case,

```text
75*(I(P)-N) <= 2*(N^2 - 25|M|).
```

Since `eta=(N^2-25|M|)/25`, this is exactly

```text
I(P) <= N + (2/3)eta.
```

So OC-PMS is precisely the required `PMS-5` coefficient.  It is stronger than
plain rowwise GERSH in the only coefficient-tight length-5 branch.

## Open Proof Lemmas

1. Prove `LONG-SURPLUS`.

   Desired structural statement:

   ```text
   odd row length > 5
     => row unit-overlap excess above N consumes half of the global deficit
        eta, with an additional pure odd-cycle surplus (L^2-25)/50.
   ```

   The exact equality cases `C7[1]`, `C9[1]`, and the `C11` row suggest the
   proof should expose the surplus `(L^2-25)/50` from odd length itself.
   Dense complete odd-cycle blow-ups are harmless because geodesic mass
   anti-concentrates; sparse long corridors are harmless because `eta` is large.

   Equivalent scalar form for a long row `Q` of length `L`, writing

   ```text
   R_Q := sum_{v in Q} Tw_C(v),
   m := |M|,
   eta := N^2/25-m:
   ```

   `LONG-SURPLUS`

   ```text
   R_Q <= N + eta/2 - (L^2-25)/50
   ```

   is equivalent to

   ```text
   N^2 + 50N + 25 - L^2 - 25m - 50R_Q >= 0.
   ```

   The near-tight sparse lane diagnostic `klane-L14k4` has

   ```text
   N=75, m=16, L=15, eta=209, R_Q=172,
   margin = 7/2.
   Tw_C on Q = [4,7,10,12,14,15,16,16,16,15,14,12,10,7,4].
   ```

   In this case the closed-neighbourhood Hall max cut is the global set
   `U=V`; the Hall excess is `R_Q-N=97`, while the bank is `201/2`.
   So the difficult sparse regime is already the total scalar
   `LONG-SURPLUS`, not a smaller Hall-deficient shadow.

2. Prove `PMS-5`.

   This is the existing OC-PMS / pentagonal matrix stability target.  The
   current smallest algebraic subtarget is the seven-cut weighted equality-atom
   implication recorded in `OC_PMS_PROOF_TARGET.md`.

3. Audit the collapse needed to apply PMS-5.

   OC-PMS currently gates length-5 overload rows in the `R(P)=sum T` sense.
   For rowwise GERSH, the relevant overload is unit-overlap `I(P)>N`.  The
   gates suggest the same pentagonal equality atom is the only coefficient
   threat, but the proof must explicitly bridge unit-overlap length-5 rows to
   the PMS-5 hypotheses or prove PMS-5 directly for every length-5 row.

## Live Hall Transport Candidate for LONG-SURPLUS

The row-only cage Hall transport is false.  With uniform capacity `A/N` and
eligibility only inside the row `P`, the exact gate

```text
python problems/23/writeup/_codex_deficit_cage_gate.py \
  --stop-first --min-n 7 --max-n 9 --two-lane-max 20 \
  --blowup-t 3 --blowup-nmax 20 --max-cuts 4
```

fails at `two-lane-L8`:

```text
N=27, m=4, A=1304/25, cap_unit=1304/675
f=(0,6), Q=(0,1,2,3,4,5,6)
U=(0,1,2,3,4,5,6,7,8)
lhs=24, rhs=1304/75, excess=496/75.
```

The current live transport candidate enlarges each demand row to its closed
blue neighbourhood.  For a fixed long row `Q`, each row `P in cyc[g]` carries
mass

```text
|P cap Q| / |cyc[g]|
```

and may use unit capacity on

```text
E(P)=P union N_B(P).
```

The universal bank is

```text
eta/2 - (|Q|^2-25)/50.
```

The Hall target is

```text
max_X demand(X)-|union_{P in X} E(P)|
    <= eta/2 - (|Q|^2-25)/50.
```

This implies `LONG-SURPLUS` because summing all row demands gives
`sum_{v in Q} Tw_C(v)`, while the vertex capacities contribute at most `N`.

Exact gate:

```text
python problems/23/writeup/_codex_row_union_hall_gate.py \
  --eligibility bclosed1 --direct-only --two-lane-max 100 --stop-first
```

Result:

```text
rows=284, violations=0, min_margin=0 at C7[1].
max_excess=348 at klane-L20k6.
max_bank_ratio=194/201 at klane-L14k4.
```

Thus the deficit bank is essential on sparse lane examples; the proof cannot
be only a closed-neighbourhood coverage statement.

Targeted no-census hard-family gate:

```text
python problems/23/writeup/_codex_row_union_hall_gate.py \
  --eligibility bclosed1 --skip-census --two-lane-max 100 \
  --max-cuts 3 --stop-first
```

Result:

```text
rows=287, violations=0, min_margin=0 at C7[1].
```

The negative control

```text
python problems/23/writeup/_codex_row_union_hall_gate.py \
  --eligibility row --direct-only --two-lane-max 8 --stop-first
```

fails first at `two-lane-L8` with margin `-29/10`; its min-cut witness is now
printed by the gate.  Thus the blue-neighbourhood enlargement is doing real
work, not merely restating the row-only false transport.

### Banked UPO Position-Flow Sublemma

For unique-geodesic long rows, the closed-neighbourhood Hall candidate has a
smaller position-flow shadow.

Let `Q=(x_0,...,x_{L-1})` be a unique row in component `C`, and define

```text
d_i := Tw_C(x_i)-1.
```

Let the blue components of `V\Q` have attachment spans on `Q`; a component
with span meeting a position set `I` contributes capacity equal to its vertex
count.  The old UPO Hall condition was

```text
sum_{i in I} d_i <= cap(I),
```

which would imply the false ceiling `R_Q<=N`.  The corrected banked condition is

```text
sum_{i in I} d_i <= cap(I) + eta/2 - (L^2-25)/50.
```

For `I={0,...,L-1}` this is exactly `LONG-SURPLUS` for a unique row.

Exact gate:

```text
python problems/23/writeup/_codex_banked_upo_gate.py \
  --direct-only --two-lane-max 100 --stop-first
```

Result, interval position sets:

```text
rows=284, violations=0, min_margin=0 at C7[1].
```

Bounded all-subsets sanity:

```text
python problems/23/writeup/_codex_banked_upo_gate.py \
  --direct-only --two-lane-max 14 --all-subsets \
  --max-row-len 15 --stop-first
```

Result:

```text
rows=100, violations=0, min_margin=0 at C7[1].
```

This is a cleaner proof target for unique long rows than full row-atom Hall:
prove a banked span-capacity Hall statement for off-row blue components.

Additional exact gates:

```text
python problems/23/writeup/_codex_banked_upo_gate.py \
  --min-n 7 --max-n 10 --max-cuts 4 --stop-first
```

Result, interval position sets on census plus the direct families already
included in the gate:

```text
census N=7: rows=152, viol+=0
census N=8: rows=156, viol+=0
census N=9: rows=184, viol+=0
census N=10: rows=280, viol+=0
violations=0, min_margin=0 at C7[1]
```

Named/direct interval stress:

```text
python problems/23/writeup/_codex_banked_upo_gate.py \
  --skip-census --two-lane-max 30 --max-cuts 3 --stop-first
```

Result:

```text
rows=147, violations=0, min_margin=0 at C7[1]
```

All-subsets census sanity for rows of length at most `15`:

```text
python problems/23/writeup/_codex_banked_upo_gate.py \
  --min-n 7 --max-n 10 --max-cuts 4 --all-subsets \
  --max-row-len 15 --stop-first
```

Result:

```text
census N=7: rows=112, viol+=0
census N=8: rows=116, viol+=0
census N=9: rows=144, viol+=0
census N=10: rows=240, viol+=0
violations=0, min_margin=0 at C7[1]
```

Proof obligation in its smallest form:

```text
For every unique long row Q and every position interval I,
    demand(I)-cap(I) <= eta/2 - (L^2-25)/50.
```

Equivalently, any interval whose overload exceeds off-row component capacity
forces enough global bad-edge deficit to pay the excess and the odd-length
surplus `(L^2-25)/50`.  The previous unbanked UPO descent proves the same
statement with zero right-hand side only in regimes where the corrected ceiling
does not need the deficit bank; sparse lane examples show the bank is essential.

A diagnostic over direct two-lane/k-lane/odd-cycle rows, named cases, and
census `N<=9` with two gamma-min cuts per graph found:

```text
bad edges checked = 1836
unique-geodesic edges = 560
multi-geodesic edges = 1276
negative bank(Q) cases = 0
old-ceiling ROWSUM>N cases = 270
multi-geodesic old-ceiling ROWSUM>N cases = 0
first old-ceiling violation = two-lane-L8, unique row length 9,
    ROWSUM=28 > N=27, corrected A=1304/25.
```

Thus the corrected bank is not cosmetic for unique rows: the old `ROWSUM<=N`
fails already on unique long rows, while the multi-geodesic rows in this
battery did not create old-ceiling violations.

### Banked-UPO Contradiction Template

Assume a unique row `Q=(x_0,...,x_{L-1})` has a banked interval failure:

```text
E(I):=sum_{i in I} d_i - cap(I) > bank(Q)
```

for some interval `I`, with

```text
bank(Q)=eta/2-(L^2-25)/50.
```

The old unbanked interval-Hall descent only needs `E(I)>0`, but it can be
blocked in a gamma-min cut precisely by the global deficit bank.  The corrected
proof target is therefore:

```text
Any interval failure with excess E(I) forces
    eta/2 >= E(I) + (L^2-25)/50.
```

Equivalently, if the excess is larger than the bank, the same singleton/interval
descent mechanism used in the old UPO proof must strictly lower Gamma.  The
odd-row surplus `(L^2-25)/50` is the irreducible cost of having a long unique
row instead of a pentagonal row; the remaining `eta/2` is the global bad-edge
deficit available to absorb sparse-lane overload.

Bank-usage profiling on direct lanes/odd cycles plus connected-B max-cut census
through `N=10`:

```text
intervals checked = 353051
max excess = 348 at klane-L20k6, full interval
max bank ratio = 194/201 at klane-L14k4, full interval
min margin = 0 at C7[1]
```

So the hard sparse examples nearly use the whole bank, but the worst set is
the full interval `I=[0,L-1]`; the small-interval geometry is not the apparent
obstruction there.  This suggests a proof split:

```text
near-extremal eta small:
    old unbanked UPO / singleton-descent geometry should force excess <= 0
    or very small;

sparse eta large:
    global deficit bank eta/2 pays the full-interval pileup, with the
    odd-length correction (L^2-25)/50 accounting for pure odd-cycle equality.
```

The sparse half cannot be proved by local span capacity alone: the `klane`
examples use almost all of the global bank.  Any successful proof must include
a scalar deficit-pileup inequality in addition to the interval/span geometry.
