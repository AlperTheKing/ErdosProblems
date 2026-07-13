# P122: live color-excess difference Hall reduction

## Verdict

The live Hall statement is not proved or falsified here.  This note gives an
exact reduction which removes the matching language entirely.  It isolates
the only two ways a color-excess Hall inequality can fail:

1. reciprocal arm pairs inside a color; and
2. reuse of one high-mate difference by several colors.

For every color set `U`, the desired inequality is equivalent to one explicit
reserve-versus-overlap inequality, equation (6) below.  Thus a proof in the
positive-defect literal-hole domain need only control that scalar expression
on every color set.

The two gates are necessary.  The first P110 row has positive defect and a
Hall deficit but no literal hole; its parity lift has a literal hole and the
same Hall deficit but negative defect.  Conversely, an exact scan of every
positive-defect, literal-hole translation of all twenty P110 seeds found no
live Hall deficit.

## 1. Directed arm graphs

Fix a color `u`.  Write `A_u` for the directed arm arcs of `G_u` and put

\[
 r_u=|D_u|,\qquad
 q_u=\#\{\{i,j\}: i\mathbin{\to}j\in A_u,
                         j\mathbin{\to}i\in A_u\}.
\tag{1}
\]

Here `q_u` counts an unordered pair once when both directions occur.  The
following facts use only the fold definitions and integer Sidonicity.

### Lemma P122.1 (simple directed support)

For every color `u`, an ordered pair of vertices supports at most one arc,
the high mates `v_i` of the vertices are distinct, and the map

\[
 \{i,j\}\longmapsto |v_i-v_j|
\tag{2}
\]

is injective on unordered arc supports.  Consequently

\[
                         t_u=r_u+q_u.
\tag{3}
\]

#### Proof

An arc `i -> j` has base low pair `(a_i,c_j)`.  The `(a,c)` projection of
the fold system is injective, so this pair determines at most one base fold
and hence at most one arc.  If two vertices of `G_u` had the same high mate
`v`, then their high pair `(u,v)` and therefore their low pair-sum would be
the same.  Unique unordered sums force the folds to agree.  Thus `i -> v_i`
is injective.

If two unordered arc supports have the same value in (2), uniqueness of
positive differences identifies their unordered high-mate pairs.  The
injectivity just proved then identifies the two vertex pairs.  Hence every
underlying unordered arm edge contributes one member of `D_u`; it contributes
one arc unless it is reciprocal, when it contributes two.  This is (3).
QED.

## 2. The exact Hall identity

For `U` a set of colors, define the difference-overlap count

\[
 M(U)=\sum_{u\in U}r_u-\left|\bigcup_{u\in U}D_u\right|.
\tag{4}
\]

Equivalently, a difference label owned by `k` colors of `U` contributes
`k-1` to `M(U)`.  Since an integer-Sidon difference identifies its unordered
pair of high mates, this is exactly the cross-color high-pair reuse budget.

Put `U_+={u in U:t_u>n_u}` and define the signed local reserve

\[
 L(U)=\sum_{u\in U_+}(n_u-q_u)
       +\sum_{u\in U\setminus U_+}r_u.
\tag{5}
\]

### Theorem P122.2 (reserve-overlap equality)

For every endpoint-normalized integer Sidon fold system and every color set
`U`,

\[
 \left|\bigcup_{u\in U}D_u\right|-\sum_{u\in U}d_u
                         =L(U)-M(U).
\tag{6}
\]

Therefore the proposed Hall inequality is exactly equivalent to

\[
                              M(U)\le L(U)
\tag{7}

for every `U`.

#### Proof

By Lemma P122.1, `t_u=r_u+q_u`.  If `u in U_+`, then

\[
 d_u=t_u-n_u=r_u+q_u-n_u,
 \qquad r_u-d_u=n_u-q_u.
\]

If `u notin U_+`, then `d_u=0` and `r_u-d_u=r_u`.  Summing these two
identities gives

\[
 \sum_{u\in U}r_u-\sum_{u\in U}d_u=L(U).
\]

Subtract (4), which says
`|union D_u|=sum r_u-M(U)`, to obtain (6).  Inequality (7) is now
equivalent to the Hall inequality term by term.  QED.

This is sharper than invoking an augmenting-path algorithm: it reduces every
Hall obstruction to a scalar surplus of shared high-mate differences over
the reserve supplied by local nonreciprocity.

### Corollary P122.3 (minimal failure core)

If `U` is inclusion-minimal with
`sum_{u in U} d_u > |union_{u in U}D_u|`, then every `u in U` satisfies

\[
 d_u>
 \left|D_u\setminus\bigcup_{w\in U\setminus\{u\}}D_w\right|.
\tag{8}
\]

Indeed, subtract the Hall defect of `U\setminus{u}` from that of `U`.
Thus every minimal obstruction is a coupled core: a color cannot survive in
it merely on private difference labels.  Together with (6), this is the
precise live-gate frontier.

## 3. Consequence if the live inequality is proved

Taking all colors in the proposed Hall statement gives

\[
 E=\sum_ud_u\le\left|\bigcup_uD_u\right|
 \le {p\choose2}.
\]

Also `t_u<=n_u+d_u`, so, using the injective low-pair projection,

\[
 T_F\le C_S+E\le {p+1\choose2}+{p\choose2}=p^2.
\tag{9}
\]

Thus the desired implication to `T_F=O(p^2)` is unchanged.  The remaining
mathematical task is exactly to derive (7) from `delta>0` and the literal
hole; neither gate alone controls it.

## 4. Both gates are load-bearing

Let `B` be P110 row 0, stored in
`compute/p110/dimension_falsifiers.json`, with

\[
 (p,h,\delta,C_S,T_F)=(104,9821,6352,579,1104).
\]

It has no literal hole.  Direct exact enumeration gives

\[
 E=598,\quad |\bigcup_uD_u|=595,\quad
 M(\mathcal U)=363,\quad L(\mathcal U)=360.
\]

Hence the full color set already violates (7) by three.  The exact maximum
matching has size `570`, so the capacitated Hall deficit is `28`.

Its parity lift `B'=2B+1`, `h'=2h=19642`, `b=1` has a literal hole and
preserves every arm graph and every difference-label cardinality, but

\[
                         \delta(B',h')=-3469.
\]

It has the same `E=598`, union size `595`, `M=363`, `L=360`, matching `570`,
and deficit `28`.  Thus positive defect without the hole and the hole without
positive defect both falsify the ungated statement.

## 5. Exact live audit

`compute/p122/audit_color_excess_difference_hall.py` gives zero deficits on
all mandatory rows and on its complete width-30 scan: `1,857,024` phase rows,
including `1,037` positive-defect literal-hole triangle rows.

The new exact P110 translation audit tests every positive-defect translation

\[
 B=A+\gamma,\qquad h=h_0+\gamma,\qquad
 0\le\gamma<\delta(A,h_0)
\]

of each of the twenty P110 seeds.  It uses the identity

\[
 \Delta^+(A+\gamma)=\Delta^+(A),\qquad
 (A+\gamma)+(A+\gamma)+b=A+A+2\gamma+b
\]

for an exact bitset literal-hole gate before the matching calculation.
The full run has

```text
positive translations examined: 227279
b=1 literal-hole rows:         47463
b=2 literal-hole rows:         47684
distinct B,h matching calls:   52832
positive-excess matching rows: 8013
maximum color excess:          24
maximum T_F:                   144
Hall deficits:                 0
decision SHA-256:              df7e55fd8d919d3f143fbc226dc4affddbcbaac27349fc4f243f3534c4f61d46
```

The `52,832` matching calls include `25,578` automatic-hole translations
with `gamma>=ceil(width/2)` and `27,254` nonautomatic literal-hole shifts.
The fold and arm definitions do not use `b`, so a translation passing either
phase gate needs one matching calculation.

Reproduce the audit with

```powershell
python -B problems/864/compute/p122/audit_p110_live_color_difference_hall.py
```

This finite audit does not prove (7).  It records that the known P110
obstruction does not survive either the automatic or nonautomatic live gate
under every endpoint-preserving positive-defect translation.

## Claim boundary

P122.1, P122.2, and P122.3 are proved for every endpoint-normalized integer
Sidon fold system.  They do not establish the live reserve-overlap inequality
(7), and therefore do not establish the live Hall lemma or the full P82
conclusion.  A proof must use both live gates to bound high-pair label reuse
against the signed reserve in (5).
