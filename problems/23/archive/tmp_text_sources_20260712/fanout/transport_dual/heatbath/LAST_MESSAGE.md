I completed the exact analysis, but could not create `REPORT.md`: the required `apply_patch` writer was denied even inside `tmp/fanout/transport_dual/heatbath/`. I did not bypass the mandated file-editing mechanism.

Core result:

\[
\bar\Delta_\mu=\sum_x\mu_x\Delta_x
=\bar C_\mu+\bar H_\mu,\qquad
\mu_x\in\mathbb Q_{\ge0},\quad\sum_x\mu_x=1.
\]

At a global scoped-score minimizer, every legal single- or multi-coordinate alternative satisfies \(\Delta_x\ge0\), hence

\[
\bar\Delta_\mu\ge0.
\]

Together with \(\bar H_\mu\le0\), this yields

\[
\bar C_\mu=\bar\Delta_\mu-\bar H_\mu\ge-\bar H_\mu\ge0,
\]

not strict negative drift. Therefore inclusion-minimal deficiency plus `HitNeedDelta ≤ 0` is insufficient. The missing theorem must directly establish a negative collision upper bound, e.g.

\[
\bar C_\mu\le-\operatorname{def}(A)+(-\bar H_\mu)-\varepsilon
\]

for some \(\varepsilon>0\), or equivalently \(\bar\Delta_\mu<0\). No current Lean reduction supplies this inequality.

Exact `Fraction` tests on `accounting/default.json`, with coordinate menu sizes \(3,5,5\):

- Uniform coordinate heat bath: \(C=-16,\ H=-3,\ \Delta=-19\).
- Uniform over all 13 alternatives: \(C=-16,\ H=-3,\ \Delta=-19\).
- Inverse-menu weights \(1/(3m_i)\): \(\Delta=-19\).

Smallest abstract falsifier: singleton inclusion-minimal shore with demand \(2\), source \(1\), defect \(1\), and one legal alternative \(C=1,H=0,\Delta=1\). It satisfies global nondecrease and \(H\le0\), but falsifies both strict negative drift and \(C\le-\operatorname{def}(A)\).

A separate exact two-coordinate model has singleton deltas \(1,1\) but joint delta \(-3\), showing why one-coordinate heat baths cannot detect all simultaneous descents.

No `sorry`, `native_decide`, floats, LP/Farkas, component embedding, or shared-file edits were used.