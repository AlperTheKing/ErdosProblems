# Non-C5 equality-face witness

For `Gamma_11` and all 56 cyclic-interval cuts, take

```text
a = (2,1,1,0,2,0,1,1,2,0,0).
```

Direct integer evaluation gives:

```text
sum(a) = 10
min_S q_S(a) = 4 = 10^2/25
number of tight arc cuts = 19
arc-value histogram = {4:19, 6:1, 8:10, 12:14, 16:6, 20:6}
```

Thus this weighting is another exact equality point.  It is not one of the
33 unit-weight induced-C5 points used to construct
`CODEX_R10_c5_FACE_data.npz`.

At any exact `c=25` certificate it forces:

- `nu_S(a)=0` for every arc cut with `q_S(a)>4`; because multiplier
  coefficients are nonnegative, every coefficient monomial positive on the
  support of `a` is then zero; and
- every parity-block evaluation vector at `y_i=sqrt(a_i)` lies in the
  corresponding PSD Gram kernel.

Consequently the 1,147 F1 zeros and 1,471 independent F2 rows derived only
from induced C5s are necessary but incomplete.  The sparse C5-face scaffold
must remain build-only until the full exact small-denominator equality set is
enumerated, transported to D22 representatives, and independently gated.
