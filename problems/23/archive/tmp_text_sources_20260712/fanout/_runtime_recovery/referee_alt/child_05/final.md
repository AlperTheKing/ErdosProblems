Verdict: natural active-component contraction does not preserve any of the four requested semantics without extra quotient data.

Exact hand-model falsifiers:

- Legal rows: contract \(C=\{s,a,b,c,t\}\). The legal four-edge row \((s,a,b,c,t)\) becomes \((K)\), which is not a legal four-edge simple replacement row.
- Score: disjoint rows \((a,x_1,x_2,x_3,x_4)\) and \((b,y_1,y_2,y_3,y_4)\) have collision excess \(0\). After contraction both contain \(K\), giving exact excess \(1\).
- Hall neighborhoods: \(N(o_1)=\{a\}\), \(N(o_2)=\{b\}\) has neighborhood size \(2\) and a perfect matching. Contraction produces two copies of \(\{K\}\), neighborhood size \(1\).
- Semantic uniqueness: selectors differing only by the choice \(a\) versus \(b\) are distinct before contraction but identical afterward. Quotient canonicality therefore cannot establish uniqueness of the original minimizer.

Exact verifier result:

```text
PASS legal 5->1; score 0->1; Hall 2->1; distinct lifts collapse
MODEL_SHA256=c3a448acf1c43ba472b4e19e2be5e6c39be65322aac3b24dd26c7079add7db35
```

It used `fractions.Fraction`; no floating-point claims were accepted.

Explicit proof gap: these are small abstract scoped-row models, not certified triangle-free, maximum-cut, Γ-minimal database fixtures. Thus they refute unqualified contraction semantics, while a theorem with the complete R25 hypotheses could survive only by proving these mechanisms impossible. Alternatively, the quotient must retain row traces, vertex capacities, collision diagonals, and lift fibers.

No reconstructible 2,943-vertex builder or certificate matching R29’s claimed SHA was found in the workspace search. The recovery directory rejected file creation through the required patch mechanism, so no artifact file was written; the launcher’s `final.md` is the sole output.