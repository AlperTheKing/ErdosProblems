# C107: seed-sensitive upper-quarter correction

## Verdict

The generalized statement is **false under the literal hypothesis of an
arbitrary nonempty finite allowed seed set**.  Its exact smallest-cutoff
falsifier is

\[
                         S=\{2\},\qquad X=74.             \tag{1}
\]

For this system

\[
 A_H^S(74)=2,\qquad D^S(74)=0,\qquad
 A_H^S(\lfloor74/4\rfloor)=0,\qquad k(S)=1,              \tag{2}
\]

so the proposed inequality reads `2 <= 1`.

The natural repaired statement must at least assume

\[
                              \{2,3\}\subseteq S.         \tag{3}
\]

Under (3), no counterexample was found.  The correction is sharp for both
`S={2,3}` and `S={2,3,66}`.  However, the repaired statement contains the
original open upper-quarter gate as its `S={2,3}` specialization, so no
proof is claimed.  Moreover, a direct induction which charges one unit for
each newly occupied seed chain is exactly false: adjoining the single seed
`668` lowers the uncorrected quarter margin by two at `X=8012`.

Thus C107 returns the requested exact smallest falsifier to the theorem as
literally quantified, and a precise obstruction to the obvious Euler proof
of the repaired theorem.

## 1. Definitions

Put

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
 \qquad U(n)=2n-1.
\]

For finite `S subset A`, let `G_S` be the least subset of `A` containing
`S` and closed under

\[
                    a,b\in G_S,\quad a<b
                    \quad\Longrightarrow\quad ab-1\in G_S.       \tag{4}
\]

Every integer `s>=2` lies on a unique literal `U`-chain with even root

\[
 \rho(s)=1+\operatorname{oddpart}(s-1).
\]

Equivalently, repeatedly replace an odd `s` by `(s+1)/2` until it is even.
Define

\[
                  k(S)=|\{\rho(s):s\in S\}|.             \tag{5}
\]

In particular,

\[
 \rho(2)=\rho(3)=2,
 \qquad k(\{2,3\})=1,
 \qquad k(\{2,3,66\})=2.                                \tag{6}
\]

This is the correct treatment of the exceptional seed `3`: the formal
factorization `3+1=2*2` is forbidden because the operands must be distinct,
but `2` and `3` occupy the same literal chain and contribute one initial
chain component, not two.

Call an even allowed root `r` **structural splitless** if `r+1` has no
factorization

\[
                    r+1=ab,\qquad2\le a<b,quad a,b\in\mathcal A.  \tag{7}
\]

Call it **hard** if at least one pair (7) exists but there is no usable
seed-3 pair: either `3` does not divide `r+1`, or `(r+1)/3` is forbidden,
or `(r+1)/3=3` violates distinctness.

For either root type define

\[
 \tau_S(r)=\min\{U^j(r):j\ge0,\ U^j(r)\in G_S\},
\]

with value infinity when the set is empty.  Then

\[
 A_H^S(X)=|\{r:r\text{ hard},\ r\le X<\tau_S(r)\}|,      \tag{8}
\]

and

\[
 D^S(X)=|\{r:r\text{ splitless},\ r\notin G_S,
                       \tau_S(r)\le X\}|.               \tag{9}
\]

The tested generalized inequality is

\[
 \boxed{
 A_H^S(X)\le D^S(X)+A_H^S(\lfloor X/4\rfloor)+k(S).}
                                                               \tag{SQ}
\]

## 2. Exact smallest falsifier to the literal theorem

Take `S={2}`.  Because closure requires two distinct operands, no operation
can be applied, and therefore

\[
                              G_{\{2\}}=\{2\}.            \tag{10}
\]

Direct divisor enumeration through `74` gives exactly two hard roots:

```text
54 + 1 = 5*11,
74 + 1 = 5*15.
```

There is no hard root below `54`.  Neither hard chain meets (10), so both
roots are persistent at `74`.  No structural splitless chain enters (10),
and there is no hard root through `floor(74/4)=18`.  Finally `rho(2)=2`, so
`k(S)=1`.  This proves (2) and falsifies `(SQ)`.

It is the smallest possible failure cutoff among nonempty seed sets.  For
`X<54` there is no hard root.  For `54<=X<74` there is at most one hard
root, while every nonempty seed set has `k(S)>=1` and the two bank terms are
nonnegative.  Hence no such system can fail before `74`.

If the empty seed set is admitted, the still earlier trivial falsifier is
`S=empty`, `X=54`: then `A_H=1` and all three terms on the right vanish.

Therefore the inclusion (3), rather than mere finiteness and allowedness of
the seed set, is load-bearing.

## 3. Repaired gate under `{2,3} subset S`

Exact computation found no failure after imposing (3).

### 3.1 Broad finite seed census

`C107_seed_sensitive_scan.py` checked every cutoff through `5000` for
`8715` systems.  The portfolio includes:

* every one-seed extension with seed at most `5000`;
* every extension by at most three allowed seeds at most `40`;
* targeted combinations on the early hard and structural chains; and
* deterministic random general and odd-only extensions of size at most 12.

There were zero failures of `(SQ)`.  The exact correction audit found:

```text
correction                         failures
k(S)                                      0
k(S)-1                                   24
number of even seed roots                 0
number of seed values minus one            0
```

The first failure of `k(S)-1` is the actual base system at `X=186`, where
the required correction is one.  The tested surrogate `|S|-1` happens to
agree with the sharp correction on `{2,3}`, but it is not chain-invariant:
adding a redundant seed such as `5` on the already occupied root-2 chain
raises `|S|-1` while leaving `k(S)` unchanged.  The raw seed count `|S|` is
already nonsharp on `{2,3}`.  The even-seed count is only a surviving finite
refinement, not a theorem.

### 3.2 Exhaustive one-extra-chain sweep

`C107_single_seed_sweep.cpp` independently checked all `66665` systems

\[
                       S=\{2,3,s\},\qquad s\le100000,
\]

for every cutoff through `100000`, using exact integer arithmetic and 64
OpenMP workers.  There were no failures.  The only non-base tight system was

\[
                             S=\{2,3,66\},               \tag{11}
\]

which needs correction two first at `X=186`.  Seeds on the original chain

\[
                    3,5,9,17,33,65,129,\ldots
\]

leave `k=1` and reproduce the base equality.

An earlier version of the same exact kernel checked all `666665` one-seed
systems through `10^6`; it likewise found no `(SQ)` failure.  This is finite
falsification evidence only; the reproducible load-bearing artifact reported
here is the current `100000` run.

### 3.3 Independent verifier

`C107_seed_sensitive_verify.py` does not use the C++ pair generator.  It
reconstructs every admissible pair by trial divisors, checks all `6665`
one-seed systems and every cutoff through `10000`, reproduces all tight rows,
and independently verifies (1)-(2) and the R8 labels.  Normal and `python -O`
runs are byte-identical.

## 4. Exact failure of one-chain Euler induction

Let

\[
 F_S(X)=D^S(X)+A_H^S(\lfloor X/4\rfloor)-A_H^S(X).       \tag{12}
\]

The tempting perturbation lemma is

\[
 F_{S\cup\{s\}}(X)\ge F_S(X)-1                         \tag{PL}
\]

when `rho(s)` is a new occupied chain.  Together with the base `+1` gate,
`(PL)` would prove `(SQ)` by adding the seed chains one at a time.

`(PL)` is false.  Its first exact failure in the exhaustive one-seed sweep
through `10000` is

\[
                  S=\{2,3\},\qquad s=668,\qquad X=8012. \tag{13}
\]

The independent trial-divisor replay gives

```text
                         A_H(X)   D(X)   A_H(floor(X/4))   F
base {2,3}                  309    301          83          75
seeded {2,3,668}            309    300          82          73
```

Thus `F` falls by two.  The two lost units are explicitly

```text
lost healed splitless root:       668
lost quarter-persistent hard root: 1002
lost full-scale hard roots:       none
```

Seeding `668` both suppresses its own splitless-entry event and causes root
`1002` to heal before the quarter cutoff.  The full-scale hard count is
unchanged.  This is precisely the two-unit interaction which a componentwise
Euler correction misses.

The corrected inequality still has large reserve at this cutoff:

\[
 F_{\{2,3,668\}}(8012)+k(\{2,3,668\})=73+2>0.
\]

Hence (13) falsifies the proof mechanism, not `(SQ)`.

## 5. Multi-seed adversarial search

`C107_combo_search.cpp` used the 76 roots with the strongest exact one-seed
effects, exhaustively evaluated their pair layer, and then retained a
500-state exact beam through eight extra seed roots at every cutoff through
`100000`.  It found no failure.  The best corrected slack by depth was

```text
extra roots       1  2  3  4  5  6  7  8
minimum slack     0  1  2  3  4  5  6  7
```

This search is exact on every evaluated seed system but is not exhaustive
over all systems beyond the pair layer.

## 6. What is and is not established

**Proved.** The all-nonempty-seed formulation of `(SQ)` is false, with the
globally smallest failure cutoff given by (1).  The hypotheses
`{2,3} subset S` and the identification `rho(2)=rho(3)` are necessary for
the intended statement.  The perturbation lemma `(PL)` is false by (13).

**Exact finite evidence.** Under `{2,3} subset S`, `(SQ)` has no failure in
the stated broad, one-chain, and multi-chain censuses.  The constants `+1`
and `+2` are sharp for `{2,3}` and `{2,3,66}` respectively.

**Not proved or falsified.** The repaired all-`X` statement under (3).  Its
`S={2,3}` specialization is exactly the C92 upper-quarter gate, which by
C95 already implies `A_H(X)=o(X)` and resolves Problem 424.  C107 does not
turn that theorem-strength specialization into an elementary Euler lemma.

## 7. Reproduction

```powershell
python problems/424/compute/wave5/C107_seed_sensitive_scan.py `
  --limit 5000 --exhaustive-max 40 --single-max 5000 `
  --random-count 1000 `
  --output problems/424/compute/wave5/C107_seed_sensitive_scan_5000_final.json

g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion -Wshadow `
  -fopenmp -march=native `
  -o problems/424/compute/wave5/C107_single_seed_sweep.exe `
  problems/424/compute/wave5/C107_single_seed_sweep.cpp

problems/424/compute/wave5/C107_single_seed_sweep.exe 100000 64 `
  problems/424/compute/wave5/C107_single_seed_sweep_100000_final.json

python problems/424/compute/wave5/C107_seed_sensitive_verify.py `
  --claim problems/424/compute/wave5/C107_single_seed_sweep_10000_final.json `
  --output problems/424/compute/wave5/C107_seed_sensitive_verify_10000.json

python -O problems/424/compute/wave5/C107_seed_sensitive_verify.py `
  --claim problems/424/compute/wave5/C107_single_seed_sweep_10000_final.json `
  --output problems/424/compute/wave5/C107_seed_sensitive_verify_10000_O.json

g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wconversion -Wshadow `
  -fopenmp -march=native `
  -o problems/424/compute/wave5/C107_combo_search.exe `
  problems/424/compute/wave5/C107_combo_search.cpp

problems/424/compute/wave5/C107_combo_search.exe 100000 64 8 500 `
  problems/424/compute/wave5/C107_combo_search_100000.json
```

SHA-256 values for the principal artifacts at report time:

```text
1AEA8AC684916BF56BBA92E3949624FAB7582B99DFAC5FB34CE4710903D39613
  C107_single_seed_sweep.cpp
86E006AF8B8292DCB3305260FA67910DC9662A7FDAFF3CFD9D3C6D4CC67101E6
  C107_single_seed_sweep_100000_final.json
DEF7453EFFD980688A22E0E457DAEED00E7F2141297091F0CA14B73A9441414E
  C107_seed_sensitive_scan.py
7DA76B84C2E11914CB00B07BC187CD2193BEA57411B4CAD8826C6334B15CD9E8
  C107_seed_sensitive_scan_5000_final.json
2727FF2D735FACF03D528B04CA37BE37A82434F87AF42750218E703236F93ECA
  C107_seed_sensitive_verify.py
D02B963CE79D741A4C3238AFC0BB3737F03C466B5F5D111A637B37D3B8907219
  C107_seed_sensitive_verify_10000.json
861343C4C25782174ADE406CB5C280486A918EB5171B26BC16C716954945FA11
  C107_combo_search.cpp
314247F9EC02B04BD86D937C38AAE4C06FA72635B4B7BF9FB537AA84A73B8E9B
  C107_combo_search_100000.json
```
