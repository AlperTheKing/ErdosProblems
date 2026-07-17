# C35: the killed-chain local-limit estimate is false

## Verdict

The load-bearing estimate (LL) in C29 is false. There is an explicit equal-count
affine relation already recorded in C29,

\[
  552223 \equiv 232552,
  \qquad L_{552223}(t)=L_{232552}(t)=600t+218.
\]

Repeating three independently chosen copies of this relation per unit `k`,
and appending one fixed filler word, produces a fiber of size at least
\(8^k\) at the target count vector \((15k,10k,6k)\). Since

\[
  8\left(\frac{30}{31}\right)^{31}
  =2.894918718637622\ldots>1,
\]

this family violates (LL) exponentially. Thus the C29 maximum-multiplicity
route cannot prove the offset mass gate.

All statements below are exact. The verifier exhaustively reconstructs all
members of the family for \(1\le k\le6\), checks their words are distinct,
and checks their maps and count vectors.

## 1. Exact conditioned path law

Use C29's notation

\[
 S=\frac{31}{30},\qquad \phi(d)=d+\frac{28}{59},
\]

and, on every available inverse edge \(d\to d'\),

\[
 K(d,d')=S^{-1}\frac{\phi(d')}{\phi(d)}.
\]

Let \(\gamma=(d=d_0,d_1,\ldots,d_n=0)\) be a valid path with a
specified label word. Its probability is exactly

\[
 \Pr_d(\gamma)
 =\prod_{j=0}^{n-1}S^{-1}\frac{\phi(d_{j+1})}{\phi(d_j)}
 =S^{-n}\frac{\phi(0)}{\phi(d)}.                 \tag{1}
\]

Consequently, conditional on

\[
 X_n=0,\qquad (N_2(n),N_3(n),N_5(n))=(a,b,c),
\]

the path law is uniform on the \(R_{a,b,c}(d)\) valid inverse paths.
There is no additional chain-dependent weight available to suppress a large
fiber. In particular,

\[
 \Pr_d(X_n=0,N(n)=(a,b,c))
 =R_{a,b,c}(d)S^{-n}\frac{\phi(0)}{\phi(d)}.       \tag{2}
\]

Thus (LL) is equivalent, after cancelling the positive endpoint factor, to

\[
 R_{15k,10k,6k}(d)\le C_0\frac{S^{31k}}{\sqrt{k}}
 \quad\hbox{uniformly in }d.                       \tag{3}
\]

## 2. Equal-map collision block

Words are written outermost letter first, as in C29. For
\(L_m(t)=mt+q_m\), with \((q_2,q_3,q_5)=(0,1,3)\), direct composition gives

\[
 \begin{aligned}
 u&=552223,& L_u(t)&=600t+218,\\
 v&=232552,& L_v(t)&=600t+218.
 \end{aligned}                                      \tag{4}
\]

Both words have count vector

\[
 (\#2,\#3,\#5)=(3,1,2).                              \tag{5}
\]

This is not merely an endpoint collision: the two full affine maps are
identical, so the identity persists under arbitrary left and right
composition.

## 3. Infinite target-count fiber

Fix \(k\ge1\). Choose independently one of \(u,v\) in each of \(3k\)
consecutive six-letter blocks, then append the fixed filler

\[
 w_k=2^{6k}3^{7k}.
\]

Every resulting word has count vector

\[
 3k(3,1,2)+(6k,7k,0)=(15k,10k,6k).                    \tag{6}
\]

The block code is fixed-length and \(u\ne v\), so its \(2^{3k}=8^k\)
choice strings are distinct. Equation (4) shows that every block sequence
has affine map \(H^{3k}\), where \(H(t)=600t+218\). Therefore all the words
have one common full affine map

\[
 H^{3k}\circ L_{w_k}.
\]

In particular, for its endpoint \(d_k=(H^{3k}\circ L_{w_k})(0)\),

\[
 R_{15k,10k,6k}(d_k)\ge8^k.                            \tag{7}
\]

For completeness,

\[
 L_{w_k}(0)=2^{6k-1}(3^{7k}-1)
\]

and hence

\[
 d_k=600^{3k}2^{6k-1}(3^{7k}-1)
     +218\frac{600^{3k}-1}{599}.                       \tag{8}
\]

The quotient is integral because \(600\equiv1\pmod{599}\). The common slope
is exactly

\[
 600^{3k}2^{6k}3^{7k}=2^{15k}3^{10k}5^{6k}.            \tag{9}
\]

Reversing every forward word gives a valid inverse path from \(d_k\) to
zero, so (7) counts paths in the killed chain appearing in (LL), not formal
words outside its state space.

## 4. Exponential contradiction to (LL)

Equations (2) and (7) give

\[
 \Pr_{d_k}(X_{31k}=0,N(31k)=(15k,10k,6k))
 \ge8^kS^{-31k}\frac{\phi(0)}{\phi(d_k)}.              \tag{10}
\]

If (LL) held with an absolute constant \(C_0\), cancellation of the positive
factor \(\phi(0)/\phi(d_k)\) would imply

\[
 \sqrt{k}\left(8S^{-31}\right)^k\le C_0.              \tag{11}
\]

But the base is exactly

\[
 \rho=8S^{-31}
 =\frac{8\,30^{31}}{31^{31}}
 =\frac{49413871702715760000000000000000000000000000000}
        {17069174130723235958610643029059314756044734431}
 >1.                                                     \tag{12}
\]

Therefore the left side of (11) tends to infinity. No absolute \(C_0\)
exists, proving that (LL) is false.

## 5. Consequence and sharper remaining frontier

The failure is specific to a uniform maximum-fiber estimate. It does not
falsify the desired support lower bound: the constructed fiber has only
\(8^k\) words, exponentially negligible compared with the full multinomial
word mass.

A viable replacement must ignore or quotient exact equal-map collision
blocks. One precise sufficient statement is a typical-fiber estimate: find
endpoint sets \(E_k\) such that

\[
 \sum_{d\in E_k}R_{v_k}(d)=o(W_{v_k})
\]

and

\[
 \max_{d\notin E_k}R_{v_k}(d)
 \ll \frac{S^{31k}}{\sqrt{k}}.
\]

That statement would still imply the C29 support target after discarding
\(o(W_{v_k})\) word mass, while (7) would merely place \(d_k\) in \(E_k\).
No proof of this replacement is claimed here.

## 6. Exact verification

Artifacts:

- `problems/424/compute/wave3/C35_killed_chain_local_limit/verify_ll_falsifier.py`
- `problems/424/compute/wave3/C35_killed_chain_local_limit/result.json`

Reproduction:

```powershell
python problems/424/compute/wave3/C35_killed_chain_local_limit/verify_ll_falsifier.py `
  --max-enumerated-k 6 `
  --output problems/424/compute/wave3/C35_killed_chain_local_limit/result.json
```

The run checks \(8+64+512+4096+32768+262144=299592\) distinct words. The independent replay passed through `k=5`; the primary verifier passed
through `k=6`. Pinned SHA-256 values are

```text
verify_ll_falsifier.py  fa01f279c1efb4d42857c7550a5cca52e6dcb57410609f03df84290d28299ef9
result.json             a3694c4b2aa14ee3ec04236ca6cb023c7a69c4b3d1e8694683c9ba2748a71e84
```



