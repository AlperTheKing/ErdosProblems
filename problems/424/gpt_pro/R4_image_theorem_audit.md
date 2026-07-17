# GPT-Pro R4 audit: exact defect identity, not an image-theorem proof

## Verdict

R4 does not prove the requested unconditional image theorem, does not give a
counterexample, and does not prove the weaker one-step preservation theorem.
Its final paragraph explicitly leaves a global ballot assertion open.

It does provide two correct load-bearing facts for the actual least grounded
set `G`:

1. an exact decomposition of the two-scale recurrence defect; and
2. infinitely many positive one-step jumps of that defect.

The first is an identity, not an upper bound. Its positive part is
quantitatively equivalent to the original density conclusion, so R4 has not
reduced the remaining theorem.

## Exact identity

Let `M(X)` count allowed holes, `E(X)` splitless holes, and
`R(X)=M(X)-E(X)`. Put

\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,
 \qquad Z=\left\lfloor\frac{X+1}{3}\right\rfloor,
\]

and

\[
 \Delta(X)=R(X)-M(Y)-M(Z).
\]

Let `K(X)` count hard holes. Define

\[
 T_2(X)=\#\{h\le Y:h\notin G,\ 2h-1\in G\},
\]

\[
 U_3(X)=\#\{h\le Z:h\notin G,\ h\text{ even or }3h-1\in G\}.
\]

Then R4 proves the exact identity

\[
 \Delta(X)=K(X)-T_2(X)-U_3(X).                         \tag{R4.1}
\]

Here `T_2(X)` is the existing healed seed-2 boundary count `Q_G(X)`.
The proof partitions reducible holes into odd holes, usable seed-3 even
holes, and hard holes, then applies the exact seed-2 and seed-3 parent
bijections. The parity, cutoff, and distinct-input conventions are correct.

R4 also proves, assuming the existing theorem `E(X)=o(X)`, that with

\[
 L=\limsup M(X)/X,
 \qquad \eta=\limsup \Delta^+(X)/X,
\]

one has

\[
 \eta\le L\le6\eta.                                   \tag{R4.2}
\]

Thus `M(X)=o(X)` if and only if `Delta^+(X)=o(X)`. This equivalence shows
that controlling the positive defect is theorem-strength; it is not a
strictly weaker bridge.

## Infinite positive jumps

R4 correctly observes that `11` is a hole. For every prime `p>11` with
`p = 2 (mod 3)`, the value

\[
 n_p=11p-1
\]

is a hard hole: `n_p+1=11p` has the unique admissible nontrivial factor
pair `(11,p)`, and the missing factor `11` blocks generation. Since `n_p`
is divisible by `3`, neither floor cutoff `Y` nor `Z` changes from
`n_p-1` to `n_p`, so

\[
 \Delta(n_p)-\Delta(n_p-1)=1.                          \tag{R4.3}
\]

There are infinitely many such primes. These jumps do not make `Delta`
positive by themselves; an accumulated negative balance may absorb them.
They rule out any proof that requires pointwise nonincrease of `Delta`.

## Independent exact replay

`R4_image_theorem_audit.py` independently generated the least grounded set,
classified all holes by exact divisor enumeration, and checked (R4.1) at
every cutoff through `1,000,000`. It also checked every `11p-1` jump in that
range.

Result:

```text
generated                    457599
holes                        209067
splitless                    108651
reducible                    100416
hard                          45583
T2                            67537
U3                           173672
max absolute identity residual    0
max Delta                         0
prime-family jumps checked     4410
```

Thus all tested positive jumps occur while the global defect remains
nonpositive, exactly as R4 warns.

Reproduction:

```powershell
python problems/424/gpt_pro/R4_image_theorem_audit.py `
  --limit 1000000 `
  --output problems/424/gpt_pro/R4_image_theorem_audit_1e6.json
```

SHA-256:

```text
raw answer  A20F2F4A73E8EEDA6F00A9229BC93E336181A0727F87A38FC7DECFE370814A56
checker     118375071C4F1EC0F925876F8A0B291EF1D3B0B752AA4B9DA65C13CA850C6E47
result      6C9B4577EB008B0EF98357ED3D39E74F8CD55CF2D1BEB77573E0ADF4EF0A7A56
```

## Classification

- Requested image theorem: **not proved**.
- Requested counterexample: **not supplied**.
- Weaker preservation theorem: **not proved**.
- Exact defect identity: **proved and replayed**.
- Infinite actual-G positive-jump family: **proved and replayed**.
- New proof frontier: prove a global ballot bound for `Delta`, or the weaker
  additive-one death-rank theorem of C31/C42. A local monotonicity argument
  cannot close it.
