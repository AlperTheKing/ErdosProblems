# Support-sensitive centered codegree identity: exact audit

## Verdict

The identity is correct, but its inequality and proposed \(4/3\) frontier are
algebraically identical to Lemma 2 and equations (10)--(17), (24)--(25) of
\`fanout/wave1/P02_k23_interval.md\`.

For a finite \(X\), put

\[
\nu_A(d)=\#\{a\in A:a+d\in A\},\qquad
Z_X=\sum_d\rho_X(d)(\nu_A(d)-1).
\]

P02 writes \(\nu_A(d)=1_\Delta(d)+1_D(d)\). Since
\(\sum_d\rho_X(d)=\binom{|X|}{2}\),

\[
Z_X=Q_\Delta(X)+Q_D(X)-\binom{|X|}{2}.
\]

Consequently GPT-Pro's energy formula

\[
\sum_yD_X(y)^2=m h+h(h-1)+2Z_X
\]

is exactly P02 equation (13),

\[
\sum_yD_X(y)^2=mh+2Q_\Delta(X)+2Q_D(X).
\]

Replacing \(X\) by \(-X\) identifies GPT-Pro's \(|A-X|\) with P02's
\(|A+X|\). Its displayed centered identity is the exact variance remainder
in the Cauchy--Schwarz step used in P02 (14). The interval support formula
is P02 (17), and the centered duplicate formula is P02 (18) after writing
the reflected core in radius coordinates.

Thus the proposed mesoscopic condition

\[
\frac{M_H(A)}N\left(1+\frac{2Z_H(A)}{H^2}\right)
\le \frac43+o(1)
\]

is not a new reduction: it is P02's existing open support--duplicate
tradeoff.

## Exact verification

\`compute/verify_gpt_support_identity.py\` checked the identity for 16,128
pairs \((A,X)\), with \(A\subseteq[1,8]\), nonempty
\(X\subseteq[-2,3]\), using \`Fraction\` throughout.

For

\[
A=\{1,2,8,10,13,23,27,43,47,57,60,62,68,69\},\quad H=16,
\]

the claimed values all pass:

\[
m=14,\quad M_H=84,\quad Z_H=120,\quad
\sum_yD_H(y)^2=704,
\]

\[
M_H\left(1+\frac{m-1}{H}+\frac{2Z_H}{H^2}\right)=231,
\]

and the exact variance remainder is \(231-14^2=35\).

## New ask sent

GPT-Pro was asked for one genuinely stronger, exact-testable structural
inequality coupling \(M_H\) and \(Z_H\), or an adaptive mesoscopic choice of
\(H\), sharp on the Erdos--Freud family. The prompt explicitly excludes
restating P02 or treating the variance remainder as independent data.
