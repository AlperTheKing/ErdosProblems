# Q8 — δ₂-dichotomy / D-lower-bound: GPT Pro ANSWER + Step-2 AUDIT (2026-06-20)

Driven via Chrome (chat c/6a35f70f "Triangle-Free Graph Conjecture", Kapsamlı Pro;
GPT reasoned ~55 min, 9478-char answer). Question: close the low-codegree regime
`δ₂<=⌊5n/8⌋` by lower-bounding the radius-2 surplus `D` (WYZ closes `δ₂>⌊5n/8⌋`).

## GPT VERDICT (honest): NO proof. The δ₂-dichotomy approach CANNOT work — refuted
## rigorously in three independent ways. Best scalar coefficient = 1/17.2 (< BCL 1/23.5).

## What GPT proved (Step-2 audited; key inequalities re-derived/verified)
1. **"small δ₂ ⟹ large D" is FALSE.** Elementary `0 <= Δ_v <= e₂(v)` (since
   `e(H_v)=S_v+e₂(v)`, `MaxCut(H_v)<=e(H_v)`). So a SPARSE ball forces Δ_v SMALL, not
   large — opposite to the proposed intuition; the sparse-ball benefit is in `−T`, not D.
2. **High-δ₂ is CIRCULAR.** If `δ₂(G)>=1`, every nonedge has a common neighbour ⟹
   diameter ≤ 2 ⟹ `H_v=G` for all v. Then `T=Ne−Q`, `D=N(e−β)−Q`, so
   `Q−T+2D = Ne−2Nβ`, and the radius-2 criterion `Q−T+2D>=Ne−2N³/25` reduces
   IDENTICALLY to `β<=N²/25`. (Step-2 verified the algebra.) No new content.
3. **Low-δ₂ ≡ the FULL problem.** Blowup lemma `β(F[k])=k²β(F)` (multilinearity, the
   same fact as BU1/Codex's transfer; Step-2 re-derived). For any tri-free `F` on `5n`,
   `G_k=F[k] ⊔ 5K₁` has `δ₂=0`, `β=k²β(F)`; a low-codegree theorem would give
   `k²β(F)<=(kn+1)²`, which for `β(F)>=n²+1` fails at large `k` — so it implies `β(F)<=n²`
   for ALL `F`. Hence the `δ₂<=⌊N/8⌋` class contains scaled copies of every obstruction.
   Witness with `δ₂=0`, `β=(n-1)²` (or `n²−n` for `(n-1,n,n,n,n)⊔K₁`) yet `D=0`.
- **Net:** δ₂ alone carries insufficient information; both ends of the dichotomy are useless.
- Scalar realignment optimum `c_*=0.058126…=1/17.2039` (eq matches the radius-2 Q7
  answer exactly); one low-codegree pair adds only `O(N)` vs the `Ω(N²)` gap. Clebsch
  blowup (`N=16k`, codeg 2 ⟹ `δ₂=N/8`) is the sharp finite obstruction at the WYZ
  boundary (root `S_v+R_v=25+4=29` via Petersen `α(KG(5,2))=4`).

## ★ NEW VERIFIED TOOL — three-cut bound from a nonedge (PROVED + Step-2 verified)
For a nonedge `uv`, set `C=N(u)∩N(v)`, `A=N(u)∖C`, `B=N(v)∖C`, `R=V∖({u,v}∪C∪A∪B)`,
`t=|C|`, `p=e(A,B)`, `q=e(R)`, `x=e(A,R)`, `y=e(B,R)`. Then
  **`β(G) <= min{ p+q, t+q+x, t+q+y }`.**
Three explicit shores: `A∪B∪C` (mono `=p+q`; A∪C, B∪C independent), `{v}∪A∪R`
(mono `=t+q+x`; the `t` is the `u`–`C` edges inside the complement), and the symmetric
`{u}∪B∪R` (`t+q+y`). **Step-2 INDEPENDENT VERIFICATION: 0 violations over ALL
triangle-free graphs N=6..9 (69 940 nonedge-checks).** A counterexample (`β>=n²+1`) must
have all three `>n²`. Useful minimal-counterexample constraint; gap: `q=e(R)` can hold the
whole hard core (isolated-pair case gives only `β<=e(R)`).

## NEW TOOL — one-root realignment (formula 7)
`M_v=V∖({v}∪N(v))`; for `Y⊆M_v`, shore `N(v)∪Y` has cut `S_v+Σ_{y∈Y}(d(y)−2codeg(v,y))−2e(Y)`.
With `R_v=max_{Y⊆M_v}[Σ(d(y)−2codeg(v,y))−2e(Y)]`, `β(G)<=e−max_v(S_v+R_v)`. Scalar
averaging of this gives the `1/17.2` bound.

## Step-2 AUDIT verdict: SOUND, no overclaim
All load-bearing claims re-derived or computationally verified: `Δ_v<=e₂(v)` (immediate);
diameter-2 reduction `Q−T+2D=Ne−2Nβ` (algebra ✓); blowup `β(F[k])=k²β(F)` and the
low-codeg⟹full reduction (`k²(n²+1)>(kn+1)²` for `k>2n`, ✓); 3-cut bound (4) verified
0/69940. GPT explicitly states it does NOT prove the conjecture. Consistent with Q7.

## Consequence for Step-2 strategy
- The **δ₂-dichotomy line is DEAD** (do not pursue: low-δ₂ ≡ full problem, high-δ₂ circular).
  The radius-2/D-bound scalar route caps at 1/17.2. Update ledger RAD2/WYZ-CODEG accordingly.
- **Genuine next direction (GPT):** a ROBUST AGGREGATE statement — either `Θ(N²)`
  degree-/codegree-deficient nonedges, coherently distributed, generate `Θ(N³)` total
  realignment gain; OR all exceptional pairs localise in a small vertex set whose removal
  leaves a `C5`-homomorphic core, with a sharp extension inequality for the removed
  vertices. This is the honest research frontier (= the medium-density Erdős #23 core).
- The 3-cut bound (4) is a real new minimal-counterexample tool worth keeping.
