Result: the maxcut expansion yields a sharp identity, but not a terminal-count lower bound.

For a vertex \(v\), set
\[
a(v)=d_B(\{v\})-d_M(\{v\}).
\]
For any distinct \(x,y\),
\[
\sigma(\{x,y\})=a(x)+a(y)-2\varepsilon(xy),
\]
where \(\varepsilon(xy)=1,-1,0\) according as \(xy\) is blue, bad, or absent.

If \(x,y\) are both blue neighbors of owner \(o\), they lie on the same cut side. Triangle-freeness then forces \(xy\notin E\), so the sharp corrected identity is
\[
d_B(\{x,y\})-d_M(\{x,y\})-2=a(x)+a(y)-2.
\]
Thus the corrected terminal condition is exactly \(a(x)+a(y)\ge2\). Maxcut gives only \(a(v)\ge0\) individually.

For an owner shore \(A\), define
\[
C_A(x,y)=\{o\in A: ox,oy\text{ are blue}\}.
\]
The exact distinct corrected-source count, after Free/reservation restrictions, is
\[
\sum_{(x,y,h)}
  1_{\rm Free}\,1_{\rm unreserved}\,
  1_{a(x)+a(y)\ge2}\,1_{C_A(x,y)\ne\varnothing}.
\]
The corresponding owner-arc count replaces the last indicator by \(|C_A(x,y)|\). Hence the exact owner-overlap debit is
\[
\sum_{(x,y,h)}
  1_{\rm Free}\,1_{\rm unreserved}\,1_{a(x)+a(y)\ge2}
  \bigl(|C_A(x,y)|-1\bigr)_+.
\]
Further debits are overlap with the old neighborhood and half-zero reservations. These terms cannot be discarded.

No stronger count inequality follows from the listed production hypotheses: maxcut controls only the nonnegative singleton slacks, while `GammaMinimalConnected` permits a constant `gammaOfCut` and supplies no additional structural inequality. A proof therefore needs a new lemma tying minimal deficient-shore demand/Free exclusions to the distribution of the \(a(v)\), not merely their nonnegativity.

Exact guardrails remain clean:

- Complete N=12 medium/heavy shortest-row census: 18,961,358 tuples; all 8,224 old Hall failures repaired; zero remaining.
- R29: 216 new distinct keys; minimum 28-key repair; every repair key has \((d_B,d_M,\text{adjusted})=(30,27,1)\).
- N=12 result SHA-256: `f822a33ea817afde3e1560a7feb341a2209316b9fd99382c9f031aa33e1c6dff`.
- R29 result SHA-256: `9de9bec94a717da6f4a9fdb50e826dfcd9d8a6e4ed983f8baa16d91771d643e7`.

I could not write lane-local artifacts because the filesystem patch wrapper refused the configured split writable roots; no shared files were edited.