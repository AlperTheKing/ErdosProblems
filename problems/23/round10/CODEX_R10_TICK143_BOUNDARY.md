# Exact audit of the proposed non-C5-colourable support gap

Claude TICK-143 correctly splits weightings according to whether their support
is C5-colourable.  The C5-colourable side is settled by embedding the support
in a complete C5 blow-up and applying the exact blow-up formula.

The claimed fixed gap on the other side is false.  In `Gamma_11`, let

```text
S = {0,1,2,4,5,6,8,9},
C = {0,1,4,5,8}.
```

The induced graph on `S` is not homomorphic to C5, while `C` induces a C5.
For every integer `M >= 1`, assign weight `M` on `C`, weight `1` on `S-C`,
and weight `0` elsewhere.  Every cut cost is a polynomial

```text
A M^2 + B M + C0.
```

Exact enumeration of all 2048 labelled cuts gives `A in {1,3,5}`.  Among the
cuts with `A=1,B=0`, the least constant term is `C0=1`, attained by 32 cuts.
All cuts with `A=1,B>0` and all cuts with `A>=3` cost at least `M^2+1`.
Therefore

```text
bip(Gamma_11[a(M)]) = M^2+1,
sum a(M) = 5M+3,
25*bip/(sum a)^2 = 25(M^2+1)/(5M+3)^2 -> 1.
```

The values remain below the conjectured ceiling, but approach it arbitrarily
closely from a non-C5-colourable full-support region.  Hence that region has
no uniform positive margin.  This kills only the advertised non-sharpness;
the support split itself remains valid but does not close the frontier.

Replay:

```text
python problems/23/round10/CODEX_R10_TICK143_BOUNDARY.py
```
