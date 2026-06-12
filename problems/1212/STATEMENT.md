# Erdős #1212 — STATEMENT
Source: [Er80, p.114] (P. Erdős, "Some notes on problems and results in number theory", 1980);
erdosproblems.com/1212 (OPEN; page edited 2026-04-08; 0 comments; no partial solutions claimed).

Let G be the graph whose vertices are the visible lattice points {(x,y) in Z_{>0}^2 : gcd(x,y)=1},
with edges joining two vertices that differ by exactly 1 in exactly one coordinate.

QUESTION: Does there exist an infinite path (going to infinity) in G such that EVERY vertex (x,y)
on the path satisfies BOTH:
  (i) min(x,y) > 1, and
  (ii) at least one of x, y is composite?

Interpretation notes (quantifiers pinned):
- "Path going to infinity" = an infinite walk leaving every finite ball (trimmable to a simple path).
- Start vertex unconstrained; only existence is asked. Answer YES = exhibit/construct; NO = prove none.
- (ii) forbids both-prime vertices (e.g. Stewart's (p_k, p_{k+1}) anchors).
- History: Erdős's original version had only (i); C. Stewart solved it via prime-pair paths
  (p_k,p_{k+1}) -> (p_{k+1},p_{k+2}) (valid when p_{k+2} < 2 p_k, true for k >= 4). The composite
  condition (ii) is Erdős's strengthening posed after that solution.
- Variants mentioned on the page (NOT the target): monotone paths; bounded direction changes.
