# Optimal 13-Channel Sorting Network — Approach Registry

Selected: 2026-07-18
Deadline: 2026-07-18T21:57:27+03:00
Status: CALIBRATION PASS — target harness blocked pending V2 referee audit

## Novelty and priority gate

- The Bose--Nelson optimal-size problem asks for the minimum number S(n) of
  comparators in an n-channel sorting network.
- Harder proved and formally certified S(11)=35 and S(12)=39:
  <https://arxiv.org/abs/2012.04400>.
- The maintained current table gives 44 <= S(13) <= 45, records the
  2025-04-21 strengthened lower bound, and supplies a 45-comparator network:
  <https://bertdobbelaere.github.io/sorting_networks.html>.
- The strengthened Van Voorhis computation is recorded at
  <https://gist.github.com/bertdobbelaere/0a30f5321965732b59c102fa9e3250bb>.
  It gives F(13)=392.
- Juillé found the 45-comparator upper bound in 1995. The maintained table and
  searches found no 44-comparator network as of 2026-07-18.

## DIRECT ROUTE

### 1. Exact final deliverable

Produce an ordered list C of exactly 44 pairs (i,j) with
0 <= i < j < 13 such that applying each compare-exchange operation in order
sorts every input in {0,1}^13. Deliver the list, two independent exhaustive
verifier results over all 8192 binary inputs, a novelty recheck, and a Lean 4
proof of the finite certificate if feasible.

### 2. Current frontier finite certificate

SN13-44: an explicit 44-comparator sequence whose exhaustive failure count
on {0,1}^13 is exactly zero.

No 45-comparator rediscovery, improved heuristic score, partial input family,
or failed bounded search is a result for this target.

### 3. Explicit logical bridge

The zero--one principle says that a comparator network sorts every totally
ordered input iff it sorts all binary inputs. Therefore an SN13-44
certificate proves S(13) <= 44.

Van Voorhis' two-channel deletion bound gives

S(N) >= S(N-2) + ceil(log2(F(N))).

The published dynamic program gives F(13)=392, so ceil(log2(F(13)))=9.
Harder's certified S(11)=35 then gives S(13) >= 35+9 = 44.
Thus SN13-44 implies the exact theorem S(13)=44.

### 4. Next falsifiable action

Before a target run:

1. independently verify the published 12-channel/40-comparator and
   13-channel/46-comparator fixtures on every binary input;
2. build the public SorterHunter engine and two independent certificate
   verifiers;
3. run 32 independent workers for at most 30 wall-clock minutes: 16 start
   from the published 12/40 fixture and seek a verified 12/39 network, and 16
   start from the published 13/46 fixture and seek a verified 13/45 network;
4. pass calibration only if at least one worker in each cohort reaches the
   stated exact target and both verifiers accept it.

If calibration passes, use at most 64 workers and the remaining deadline to
search only for SN13-44, seeded by multiple published 13/45 networks and
independent prefixes. A GPU implementation may batch exact comparator
evaluation, but no matrix multiplication is involved.

### 5. Exit condition

- If either published fixture fails independent verification, stop.
- If either calibration cohort has zero exact successes in 30 wall-clock
  minutes, mark DEAD: calibration failed and stop all 13-channel work.
- If calibration passes but no independently verified SN13-44 exists by the
  deadline, preserve logs, mark the route DEAD: no certificate by deadline,
  and stop.
- Never extend the run because a 45 network, lower error count, throughput
  record, or bounded no-hit result was obtained. Those do not close S(13).

## Minimal lemma tree

1. FixtureVerify: both published calibration fixtures are exact sorters.
2. Calibration: the engine recovers 12/39 and 13/45 under the fixed gate.
3. SN13-44: the target list sorts all 8192 binary inputs.
4. ZeroOneBridge: SN13-44 sorts arbitrary totally ordered inputs.
5. Lower44: Harder plus Van Voorhis gives S(13) >= 44.
6. ExactS13: SN13-44 and Lower44 give S(13)=44.
