# GPT Pro follow-up: p16 z8 dirty `(ZZ,ZD)=(1,20)`, ZZ endpoint pair `(2,2)`

CONTEXT.
We are in the q=14/t=2 cap74 frontier for Erdős #23 / a(30)=36.
The current row is

`(z,s1,s2,d,p,e_R,cap) = (8,0,0,6,16,21,74)`

and the active category is `(ZZ,ZD)=(1,20)`.

There are 8 zero-label vertices `Z` and 6 doubleton vertices `D={8,9,10,11,12,13}`.
For a zero `z`, let `N_D(z)` be its D-row and `m_z=|N_{A∪B}(z)|`.
For a D-column `d`, let `c_d=|N_Z(d)|` and `m_d=|N_{A∪B}(d)|`.

We already use:

1. triangle-freeness;
2. full local nonedge-codegree lower bound 2;
3. A/B root-D visibility: every A/B vertex has at least one D-neighbor;
4. cap equality `M=sum_r m_r=74`;
5. touched-column reroot equality:
   if a tight zero `z` has `d_D(z)=2` and `zd` is an R-edge, then
   `c_d+m_d=6`, hence `c_d<=4`, `m_d=6-c_d`;
6. dirty footprint capacity cut;
7. total-pair reroot cap:
   for a D-pair `{a,b}`, if some tight zero has row exactly `{a,b}`, then
   `K_ab+Q_ab <= 6` and `K_ab+Q_ab != 5`; if some zero row has exactly one
   of `{a,b}`, then `K_ab+Q_ab <= 4`.

COMPLETED.
For the same `(ZZ,ZD)=(1,20)`, zero-D degree profile `(4,4,0,0)`
(four degree-2 zeros and four degree-3 zeros), the dirty ZZ endpoint pair `(3,3)`
is closed.
By symmetry we fixed the dirty edge endpoints to rows

`4:{8,9,10}` and `5:{11,12,13}`.

Then a touched-footprint split closed all footprints:
size 1: 6/6 infeasible;
size 2: 15/15 infeasible;
size 3: 20/20 infeasible;
size 4: 15/15 infeasible;
size 5: 6/6 infeasible;
size 6: infeasible.

CURRENT BLOCKER.
Now attack the ZZ endpoint pair `(2,2)` in the same degree profile `(4,4,0,0)`.
By symmetry and triangle-freeness, fix the dirty ZZ edge endpoints to

`z0:{8,9}` and `z1:{10,11}`.

The broad projection audit times out. The touched footprint must contain
`{8,9,10,11}`, so only four footprints are possible:

`{8,9,10,11}`,
`{8,9,10,11,12}`,
`{8,9,10,11,13}`,
`{8,9,10,11,12,13}`.

The first footprint `{8,9,10,11}` also times out.

QUESTION.
Find the next smallest mathematically safe P-free strengthening for this exact
residual:

- zdeg counts `(4,4,0,0)`;
- dirty ZZ edge endpoints `z0:{8,9}`, `z1:{10,11}`;
- touched footprint `{8,9,10,11}` first, but also suggest cuts reusable for the
  two size-5 and size-6 footprints;
- no fixed A/B template enumeration.

Please give rigorous lemmas and direct CP-SAT encodings. Prefer cuts analogous
to the saturated-column visibility / reroot-excess / aggregate `M<=...` cuts
that closed earlier residuals. If a hand contradiction exists for footprint
`{8,9,10,11}`, prove it. If not, identify the smallest branch variables and the
exact finite certificate structure.

REQUIREMENTS.
Be adversarial. State every dependency. Do not assume cap<74 or lower-q closure
unless explicitly flagged. End with the weakest steps and the first concrete
C++/CP-SAT experiment to run.
