# C81: exact image-realizable blocker falsifier gate

## Verdict

There is no image-realizable blocker-cut counterexample through `X=10000`.
More precisely, for every forward-closed allowed source `S` containing `2,3`
and every `X<=10000`, the exact finite computation proves

\[
H_{F(S)}(X)\le Q_{F(S)}(X).
\]

All `878` hard cutoffs through `10000` were optimized separately and returned
`OPTIMAL`.  This closes the previous C23 simultaneous-run gap of objective
`0` versus upper bound `7` at limit `10000`.  It is only a finite theorem.  It
does not prove the unconditional image lemma or Erdős Problem 424.

The precise remaining falsifier obstruction is:

> Any counterexample must first occur at a hard-shaped even cutoff `X>10000`
> and must be realized by a self-blocking source complement whose unhealed
> hard seed-2 chains outnumber its healed nonhard seed-2 chains.

## 1. Self-blocking complement model

Let `v_n=1` mean that the allowed value `n` is absent from the source `S`.
For every distinct allowed factor pair

\[
ab=n+1,\qquad a<b,
\]

forward closure of `S` is exactly the Boolean clause

\[
\neg v_n\lor v_a\lor v_b.                              \tag{1}
\]

Thus, if `n` is cut from the source, every factor pair of `n` is hit by a
smaller cut vertex.  The seed constraints are `v_2=v_3=0`.

Write `f_n=1` for membership in the image `F(S)`.  For every pair `(a,b)`,
the clause

\[
v_a\lor v_b\lor f_n                                    \tag{2}
\]

forces an unblocked pair to put `n` in the image.  Conversely, `f_n=1`
activates one support selector, and that selector forces `v_a=v_b=0` for its
pair.  Hence the gates encode exactly

\[
f_n\quad\Longleftrightarrow\quad
\bigvee_{ab=n+1}(\neg v_a\land\neg v_b).                \tag{3}
\]

Values with no admissible pair have `f_n=0`, apart from the explicit seeds.
Only Boolean clauses and bounded integer equalities are used; there is no LP
relaxation or floating-point mathematical decision.

### Half-range elimination

At cutoff `X`, no value greater than

\[
Y=\left\lfloor\frac{X+1}{2}\right\rfloor
\]

can be a factor of an output at most `X`.  Such high source values can
therefore be set present without changing `F(S)` through `X`.  Adding them
also cannot violate forward closure through `X`.  The model needs source
variables only through `Y`.

Conversely, any feasible finite assignment extends to an infinite
forward-closed source by taking every allowed value above `X` present.  Thus
the finite model loses no image-realizable blocker cut through its cutoff.

## 2. Boundary-free chain objective

Let `T=F(S)`.  On every seed-2 chain

\[
r,\ 2r-1,\ 4r-3,\ldots
\]

rooted at an allowed even `r`, membership in `T` is upward closed.  Let
`top_X(r)` be the last chain value at most `X`.

For a hard root, the chain contributes

\[
1-f_{\operatorname{top}_X(r)}
\]

to `H_T(X)-Q_T(X)`: an absent root contributes one hard hole, canceled by
one boundary exactly when the chain has healed by its top.  A nonhard root
contributes

\[
f_r-f_{\operatorname{top}_X(r)},
\]

which is `-1` exactly for a healed nonhard chain.  Therefore

\[
H_T(X)-Q_T(X)=
\sum_{r\ \mathrm{hard}}(1-f_{\operatorname{top}_X(r)})
+\sum_{r\ \mathrm{nonhard}}(f_r-f_{\operatorname{top}_X(r)}). \tag{4}
\]

Equation (4) removes every boundary variable and requires image gates only
at roots and chain tops.

The excess can increase only when `X` reaches a hard-shaped even value;
boundary events only decrease it.  Before the first hard event it is
nonpositive.  Optimizing every hard cutoff therefore certifies every cutoff
in the finite range.

## 3. Exact finite gate

The final run used `8` independent processes with `8` CP-SAT workers each,
so the total worker cap was `64`.  Each hard cutoff was a separate integer
optimization problem with a `60` second limit.

| range | hard cutoffs | exact status | maximum image excess |
|---|---:|---:|---:|
| `X<=1000` | 66 | 66/66 `OPTIMAL` | `0` |
| `X<=5000` | 410 | 410/410 `OPTIMAL` | `0` |
| `X<=10000` | 878 | 878/878 `OPTIMAL` | `0` |

The full `X<=10000` run took `39.339` seconds of elapsed time on the recorded
machine.  Its largest per-model solver time was under `0.276` seconds.
C81 independently reproduces C78's last audited optimum `-4` at `X=984`.

The complete equality set is

\[
X\in\{54,74,114,186,204,362\}.                         \tag{5}
\]

Every later hard cutoff through `10000` has strict negative optimum.  Exact
tail maxima are:

| hard-cutoff tail | maximum excess | attaining cutoff(s) |
|---|---:|---|
| `X>=1001` | `-2` | `1014` |
| `X>=2001` | `-3` | `2064` |
| `X>=5001` | `-31` | `6192,6194,6204` |
| `X>=7501` | `-56` | `9564,9570` |

The minimum optimized excess is `-72` at `X=8664`.  The sequence of optimal
margins is not monotone: it first rises from `-1` at `84` to `0` at `114`,
and after reaching `-72` at `8664` it rises to `-56` at `9564`.  Therefore a
monotone-margin extrapolation from this gate is exactly false.

### Last hard cutoff

At `X=9984`, the exact optimum is

\[
H-Q=512-579=-67.
\]

The equivalent shell counts are `388` unhealed hard roots and `455` healed
nonhard roots.  One optimizing source/image has the following exact profile.

| quantity | count |
|---|---:|
| allowed source positions | 6656 |
| source blockers / missing values | 1369 |
| source members | 5287 |
| image members | 3400 |
| image holes | 3256 |
| factorable image holes | 1915 |
| unsupported source members | 1887 |
| blocked factor-pair incidences | 5866 |
| pairs hit once / twice | 3909 / 1957 |
| distinct blockers used | 1369 |

The endpoint model has `3328` source variables, `3386` root/top image gates,
`9298` support selectors, and `7981` self-blocking clauses.  Its serialized
CP-SAT model is `997897` bytes.

## 4. Independent verification

`C81_image_blocker_verify.py` does not call CP-SAT.  It:

1. exhausts all `65536` image-relevant source masks through the first hard
   cutoff `54`, finding exactly `256` forward-closed masks;
2. checks the direct `H-Q` count against the chain-shell formula in `13568`
   cases and matches the brute-force optimum to CP-SAT at `54`;
3. reconstructs all `878` optimizing sources and images, checks source
   closure, recomputes each objective, and checks objective equals bound; and
4. independently recomputes the blocker incidences and structural statistics
   above.

The verifier output reports `878/878 OPTIMAL`, all bounds nonpositive, and
the exact hard-cutoff coverage `54` through `9984`.

## 5. Reproduction

From the repository root:

```powershell
python -O problems/424/compute/wave5/C81_image_blocker_sat.py `
  --scan-stop 10000 --group-size 1 --jobs 8 --workers-per-job 8 `
  --time-limit 60 --linearization-level 0 `
  --output problems/424/compute/wave5/C81_gate_10000.json

python -O problems/424/compute/wave5/C81_image_blocker_verify.py `
  --gate problems/424/compute/wave5/C81_gate_10000.json `
  --exhaustive-limit 54 `
  --output problems/424/compute/wave5/C81_verify_10000.json
```

Core artifacts and SHA-256 hashes:

```text
C1A2B0AA88527EC7CBA01C3FA115D7288E56C6F7F64C7A5E7A07EC70A2ADD9F8  C81_image_blocker_sat.py
D0CD0A1880CE1B68CBB19F5B1CE47346B0FFC77AB5101653B8085AD1CF98AB21  C81_image_blocker_verify.py
976C4834302515FA3945254EB82CA056346269C2040ED335B56E54C549BF5D22  C81_gate_10000.json
244456810F0E58FA4DADDEC6C90D871656CA5803F31BD122204DC29E4FC1C964  C81_verify_10000.json
```

## 6. Scope obstruction

This gate rules out a finite counterexample only.  The exact optimizer can
move to a different source at every cutoff, the optimal margin is
nonmonotone, and no cutoff-uniform matching, dual certificate, or recurrence
is extracted.  A proof still needs a uniform reason that every
image-realizable self-blocking complement has at least as many healed
nonhard chains as unhealed hard chains.  Finite optimality through `10000`
does not supply that reason and is not an asymptotic density argument.
