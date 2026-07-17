# C83: exact obstruction to local arithmetic feature potentials

## Verdict

There is an exact falsifier at cutoff `X=186` to the following broad static
charging family: the charge may depend on parity/residue, exact obstruction
rank, dyadic scale, admissible factor count, and the complete ranked endpoint
signature of every admissible factorization, but not on the exact root value
or on the chosen blocker cut.

The obstruction is a one-cut rational Hall certificate.  The grounded image
has six unhealed hard roots and six healed nonhard roots, so it satisfies the
desired inequality with equality.  Five healed roots occupy sound singleton
feature classes.  The sixth, `66`, has exactly the same local signature as
the unhealed nonhard root `48`.  Sound feature-symmetric weights therefore
cannot use the class `{48,66}`.  Total sound target capacity is at most `5`,
whereas hard demand is `6`.

Thus this is not a counterexample to the C23 image inequality.  It proves
that the specified symbolic potential family cannot prove that inequality.

## 1. Image shells

Let

\[
 {cal A}_X=\{n\in[2,X]:n\not\equiv1\pmod3\}
\]

and let `P(n)` be the admissible distinct-factor pairs

\[
 n+1=ab,\qquad 2\le a<b,\qquad a,b\in{cal A}_X.
\]

For a forward-closed source `S` containing `2,3`, write `T=F(S)` for its
one-step supported image.  For an allowed even root `r`, put

\[
 W_X(r)=2^j(r-1)+1,
\]

where `j` is maximal subject to `W_X(r)<=X`.  A hard root is unhealed when
`W_X(r) notin T`.  A nonhard root is healed when

\[
 r\notin T,\qquad W_X(r)\in T.
\]

Only grounded holes need be considered: every forward-closed source and
every image contain the least generated set `G`.

## 2. The falsified potential family

For a grounded hole `v`, let `rho(v)` be its exact obstruction rank:

\[
 \rho(v)=0\quad(P(v)=\varnothing),
\]

and otherwise

\[
 \rho(v)=1+\max_{(a,b)\in P(v)}
              \min\{\rho(z):z\in\{a,b\}\setminus G\}.
\]

Put

\[
 d(y,x)=\left\lfloor\log_2(y/x)\right\rfloor.
\]

For an endpoint `z` of a pair supporting `v`, record

\[
 E_v(z)=
 \begin{cases}
  (G,z\bmod6,d(v,z)),&z\in G,\\
  (H,\rho(z),z\bmod6,d(v,z)),&z\notin G.
 \end{cases}
\]

Let `Fact(v)` be the sorted multiset of the sorted pairs
`(E_v(a),E_v(b))` over every `(a,b) in P(v)`.  The full local signature is

\[
 \Phi_X(v)=
 \bigl(\operatorname{type}(v),v\bmod18,\rho(v),d(X,v),
       |P(v)|,\operatorname{Fact}(v)\bigr),             \tag{1}
\]

where the type is `hard`, `splitless`, or `seed3`.

A feature-symmetric static potential consists of nonnegative real weights
`w(A,B)`, one for each hard signature `A` and nonhard signature `B`.  It must
satisfy:

1. **Soundness.** If `w(A,B)>0`, then for every image-realizable `T`, every
   hard `h` of signature `A`, and every nonhard `r` of signature `B`,

   \[
   h\text{ unhealed}\Longrightarrow r\text{ healed}.   \tag{2}
   \]

2. **Unit demand.** Every hard root sends at least one unit:

   \[
   \sum_B |B|w(A,B)\ge1.                               \tag{3}
   \]

3. **Unit target capacity.** Every nonhard root receives at most one unit:

   \[
   \sum_A |A|w(A,B)\le1.                               \tag{4}
   \]

Here `|A|` and `|B|` are the numbers of roots in the feature classes at the
fixed cutoff.  Conditions (2)--(4) imply the desired shell inequality:
activate the row of each unhealed hard root, use (2) to send mass only to
healed roots, and then apply (4).  The family permits arbitrary real weights;
the falsifier is not an integrality artifact.

## 3. Exact falsifier at 186

Exact ascending recursion gives

```text
G intersect [2,186] =
{2,3,5,9,14,17,26,27,33,41,44,50,51,53,65,69,77,80,
 81,84,87,98,99,101,105,122,125,129,131,134,137,149,
 152,153,158,159,161,164,167,173}.
```

This prefix is forward closed and its one-step image through `186` is itself.
Its unhealed hard roots are

\[
 U=\{54,74,114,144,174,186\}.                         \tag{5}
\]

Their chain tops are respectively

```text
107, 147, 114, 144, 174, 186,
```

all outside `G`.  The healed nonhard roots are exactly

\[
 B=\{6,18,20,32,38,66\},                              \tag{6}
\]

with generated chain tops

```text
161, 137, 153, 125, 149, 131.
```

Thus the true shell balance is `|B|-|U|=0`.

All six roots in (5) are unhealed in this single image.  Consequently, if a
nonhard feature class contains even one root outside (6), soundness (2)
forces every weight from every hard class to that target class to be zero.

Under (1), the roots `6,18,20,32,38` lie in five distinct singleton feature
classes.  The apparent sixth class is not sound, because

\[
 \Phi_{186}(48)=\Phi_{186}(66)
   =(\text{splitless},12,0,1,0,\varnothing).           \tag{7}
\]

Indeed, both roots are splitless, are `12 mod 18`, have rank zero, lie in the
same dyadic shell, and have no admissible pair.  But `66` is healed because
its top `131` is generated, while `48` is not healed because its top `95` is
not generated.  The grounded image therefore falsifies (2) for every block
using their shared class.

It follows that all sound target classes have total capacity at most `5`.
Summing (3) over the six hard roots gives required mass at least `6`, while
summing (4) over the five sound singleton classes gives mass at most `5`.
This contradiction is an exact falsifier over the reals.

## 4. Exact synthesis and replay

`C83_feature_potential.py` first encoded source closure and exact one-step
support with Boolean CP-SAT variables.  It used CEGIS to test feature blocks
and exact bipartite flow to synthesize the weights.  At `X=186` it made `89`
implication queries, rejected `76` feature blocks, and returned the class
Hall certificate

```text
hard demand 6 > sound target capacity 5.
```

There are `72` crossing feature blocks.  Exact set-cover minimization reduces
their countercuts to the single grounded source displayed above.  The replay
mode invokes no solver: it refactors every successor, rebuilds `G`, checks
source closure and the exact image, reconstructs all signatures, verifies all
`72` invalid blocks, and checks the `6>5` Hall count.

```powershell
python -O problems/424/compute/wave5/C83_feature_potential.py `
  --cutoff 186 --feature-mode full --workers 64 --time-limit 30 `
  --output problems/424/compute/wave5/C83_feature_potential_full_186.json

python -O problems/424/compute/wave5/C83_feature_potential.py `
  --verify problems/424/compute/wave5/C83_feature_potential_full_186.json `
  --output problems/424/compute/wave5/C83_feature_potential_full_186_verify.json
```

```text
375974131412C9AEE72D8821A867AE15D77C35A06D11BCB3685A587DA605E24C  C83_static_charge.py
423F0900A18EAC88A640D51DCD3D6F0CE43FFBB9D80220126E238F099D59774B  C83_feature_potential.py
5FF737FB89D72BA6993AEF8C390B2725CBEC718952B8C9BA5157D96ED7E05CD5  C83_static_charge_scan_1000.json
FE338D50DB24CFB21F3BA9CB99ECAE3E48495B05CC4C59F1BFCACD7D345AF6D3  C83_feature_potential_full_186.json
4E176B74363720756F4780F8F0E643CD7206BDE2E043DF801D1E6E9BAAD59E7C  C83_feature_potential_full_186_verify.json
```

The falsifier applies to local feature-symmetric, cut-independent potentials
of the form (1)--(4).  It does not rule out a cut-adaptive transport, a rule
that depends on the exact root value, or a potential that explicitly uses the
grounded status of the distant chain top.  Equation (7) identifies why one of
those genuinely nonlocal inputs is necessary.
