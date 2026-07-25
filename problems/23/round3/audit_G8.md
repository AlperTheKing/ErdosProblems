# AUDIT of round3/G8.md — "the Andrásfai ceiling"

Adversarial audit. Every central computation was re-implemented from scratch
(`audit_G8_*.py`, `audit_G8_*.cpp`): own bitmask graph representation, own
exhaustive maximum-cut over all `2^n` side-vectors, own C5-homomorphism CSP, own
maximum-matching recursion, own isomorphism backtracker, own integer-weight
enumerator (C++, `__int128` where needed). None of the target's scripts was
imported or executed except to diff numeric output files.

**Bottom line.** G8 makes no counterexample claim and none of its structural or
exact-integer claims broke. One exact numeric claim (§8, the value `1/20`) is
REFUTED with an exact falsifier. Three range statements ("for every k ≥ 3",
"for k ≥ 4") are finite verifications stated as general theorems; I *proved* one
of them in general as an audit by-product and the other remains unsupported.
One justification (§6.3) is stated circularly and needs the repair given below.
The whole of §7 terminates in an explicitly unproved lemma, so §7 is a
reformulation-plus-strengthening, not progress.

---

## 1. REFUTED

### R1. §8: "its maximum over the simplex is 1/20"

Verbatim: *"On the uniform C5 measure this is exactly 1/25, but its maximum over
the simplex is 1/20 (two atoms at distance 2/5, mass 1/2 each)."*

The preceding sentence defines the object on the circle graph Γ, so "the
simplex" is the set of probability measures on `R/Z`. On that domain the value
`1/20` is **false**.

**Exact falsifier** (`audit_G8_misc.py`, Fractions):

    two atoms at circular distance 17/50, masses 1/2 and 1/2
    K(17/50) = 1 - 2*(17/50) = 8/25,   B = (1/2)(1/2)(8/25) = 2/25 = 0.08  >  1/20 = 0.05

More: `d = 1001/3000 → B = 499/6000 = 0.08316…`. The exact supremum is **1/12**,
not attained: `K ≤ 1/3` on Γ and Γ is triangle-free, so by Motzkin–Straus
`Σ_{edges} x_u x_v ≤ 1/4`, giving `B ≤ 1/12`; two atoms at distance `1/3 + ε`
give `1/12 − ε/2`.

Where `1/20` actually comes from: it is the maximum of the same form restricted
to measures supported on the **five pentagon points**. Verified exactly by
exhaustive search over the `1/20`-grid on those 5 points: maximum `= 1/20`.

Effect on the report: the *conclusion* of §8 (arithmetic rotation-averaging
cannot certify `1/25`) is unaffected and in fact strengthened — the true gap is
1/12 vs 1/25, not 1/20 vs 1/25. Only the stated constant is wrong, and the
sentence "That reproduces the recorded dead fact for arithmetic averaging" is a
coincidence of the restricted domain, not a reproduction.

---

## 2. CONFIRMED (independent reproduction)

| # | claim | my reproduction |
|---|---|---|
| C1 | §0 And(k) = circulant on Z_{3k−1}, conn {i ≡ 1 mod 3}: k-regular, triangle-free, odd girth 5, α = k, for k = 2..7 | `audit_G8_core.py` — all four invariants match |
| C2 | §0 bip(And(k)) = 1, 2, 4, 6, 9, 12 = ⌊k²/4⌋ for k = 2..7 (n = 5,8,11,14,17,20; \|E\| = 5,12,22,35,51,70) | exhaustive maxcut over all 2^n side-vectors: maxcut = 4,10,18,29,42,58 → identical |
| C3 | §0 psi(uniform) = 1/25, 1/32, 4/121, 3/98, 9/289, 3/100 | exact Fractions, identical |
| C4 | §1 And(k) ≅ K_{(3k−1)/k} via v ↦ kv mod (3k−1) | verified k = 2..7, all pairs |
| C5 | §1 A(k) nondecreasing | CONFIRMED, and improved — see N1 below (Bondy–Hell is not needed) |
| C6 | §1 And(k) ↛ C5 for k ≥ 3 | direct exhaustive CSP: And(3), And(4), And(5) all have no hom to C5; α = k verified k ≤ 7 so χ_f = (3k−1)/k > 5/2 is sound |
| C7 | §2 Γ triangle-free; And(k) = Γ ∩ {3k−1 equally spaced points} | trivial and correct (three arcs > 1/3 cannot sum to 1; d > 1/3 ⟺ \|i−j\| ≥ k) |
| C8 | §3 support reduction psi(H,x) = psi(H[supp x], x\|supp) | correct as stated |
| C9 | §3 every **proper** induced subgraph of And(3) → C5; only obstruction is And(3) itself | own CSP over all 256 subsets, cross-checked against brute force over all 5^\|W\| colourings — **0 CSP/brute mismatches**, exactly 1 obstruction (the full vertex set). ⟹ the §3 THEOREM (psi(And(3),x) ≤ 1/25 off full support) holds |
| C10 | §3 And(k)[W] → C5 ⟺ W has no induced Wagner, k = 3,4,5 | own Wagner-isomorphism backtracker: 1 / 11 / 63 induced Wagner copies; **0 mismatches** over 256 / 2048 / 16384 subsets |
| C11 | §5 M(q): 25·M(q) ≤ q² with equality exactly at 5\|q | independent C++ (graph built in the K_{p/k} form, **no symmetry reduction at all for k = 3, q ≤ 30**): every M(q) equals the target's, And(3) q ≤ 50, And(4) q ≤ 22, And(5) q ≤ 20. 0 mismatches, 0 violations |
| C12 | §5 extremal weightings, e.g. And(3) q = 50 → a = (10,0,0,0,10,10,10,10), M = 100 | my argmax at q = 50 is (10,0,10,0,10,10,0,10) — a rotation/relabel of the same C5 blow-up, same M = 100 |
| C13 | §6.1 the atom certificate scheme is valid, and on C5 it returns the sharp certificate (5 single-edge cuts, A = {i}, B = {i+1}, w = 1/5) | verified exactly by hand and in code: mono ⊆ A×B for each atom, both marginals exactly 1/5, Σw = 1. The chain min ≤ geometric mean ≤ (weighted AM–GM)² is correct. The claim that geometric averaging escapes the recorded arithmetic 1/20 obstruction is correct |
| C14 | §6.2 matching lemma `c(S) ≥ ν(mono S)²` | proof is correct as written (x = e_a + e_b, then Cauchy–Schwarz on the matching) |
| C15 | §6.2 min over cuts of ν(mono S) = k−1; no cut has a star mono set for k ≥ 3 | own matching recursion: k = 2,3,4,5 → 1,2,3,4 (report), **extended by me to k = 6 → 5 and k = 7 → 6** (`audit_G8_nu.cpp`). Star count = 0 for k ≥ 3 |
| C16 | §6.2 table (25(k−1)² > (3k−1)² ⟺ k > 2; C5 exactly on the boundary) | arithmetic correct |
| C17 | §6.2 "all 3496 atoms" | my independent atom count for And(3) is exactly **3496** (unrestricted). Note `G8_certlp.py`'s default `max_mono = 6` gives 3408, so the report's run must have used a larger cap; the number quoted is the right one |
| C18 | §6.3 blocking lemma: And(4) has 33 induced C5s, intersection of active cut sets = ∅; And(5) 98, = ∅ | reproduced exactly; **extended by me to And(6) (238 induced C5s, ∅) and And(7) (504, ∅)**, and then *proved for all k ≥ 4* — see N2 |
| C19 | §7 the five surviving cuts q1..q5 | I obtained the **same five**, from a different maximiser family (the 8 induced-C5 uniform points rather than the report's 16 blow-up maximisers), and verified each is the mono-set of a genuine cut of And(3) — e.g. q1 ↔ side vector 01011010, q5 ↔ 01010101 |
| C20 | §7 the (m,c) identity q1q2q3q4q5 = (m0m1m2m3)²·P(c)·S/64 | verified **symbolically** in sympy (the report checked 400 random rational points only) — `sp.simplify(prod − rhs) == 0` |
| C21 | §7 max_x q1q2q3q4q5 = 25^{−5}; max_x min_j q_j = 1/25 | independent SLSQP in the original a-coordinates (not the reduced form): ratio to target = 1.0000000000 in both cases |
| C22 | §7 exact integer check 25·min_j q_j(a) ≤ q², equality exactly at 5\|q | reproduced by full enumeration to **q ≤ 34** (report: q ≤ 32), 0 violations. **New:** I also ran the *product* form 5^10·q1q2q3q4q5 ≤ q^10 exactly on the same grid (`__int128`) — 0 violations, equality exactly at 5\|q. The report never checked the terminal lemma itself on the integer grid |
| C23 | §7 the three failed AM–GM attacks | exact: P·Σ(1−c_i²) at c_i = √(1/5) is **13824/3125 = 4.42368 > 4** ✓; antipodal folding 1/1048576 vs 1.024e−7 = **9.3132×** lossy ✓ |
| C24 | §4 arc cuts attain the full cut minimum on K_{5/2}, K_{8/3}, K_{11/4}, K_{14/5} | 0 failures on my own 120/120/120/30 exact-rational trials, **plus** 0 failures on *all* uniform-support points (26/247/2036/16369) and on 62200 integer C5-support points of K_{8/3}. Also: this claim is **not load-bearing** — min over arcs ≥ psi always, so arc-only optimisation can never understate max psi |

---

## 3. UNSUPPORTED (may be true; the report does not establish it)

**U1. §6.2 "BLOCKED for every k ≥ 3".** The only k-dependent ingredient,
`min_S ν(mono(S)) = k−1`, is verified by exhaustive cut enumeration for
k = 2,3,4,5 in the report (k ≤ 7 after my run). There is no proof for general k.
What is needed is only `ν > n/5 = (3k−1)/5`; the cheap bounds
(`|mono| ≥ ⌊k²/4⌋`, `ν ≥ |mono|/(2Δ)`) give only `ν ≳ k/8` and do not suffice.
**Missing: a proof of `min_S ν(mono(S)) > (3k−1)/5` for all k.**

**U2. §6.3 / final-summary "BLOCKED for k ≥ 4".** Verified in the report at
k = 4, 5 only. *Now proved in general* — see N2. Until N2 is accepted, the report
as written is a finite verification presented as a general statement.

**U3. §0 "the maximiser is always a C5 blow-up supported on a proper subset".**
Numerical observation. It also presupposes `max psi(And(k)) = 1/25`, which for
k ≥ 3 is precisely the open question. §4's wording ("Every maximiser *found* is a
C5 blow-up") is the honest form; the §0 sentence is not.

**U4. §4 "A(k) = 0.0400000000 for k = 3,4,5,6 and for M = 5,…,29".** Floating
point, SLSQP, local optimisation. Not an acceptance path (the report says
"guiding only"), but the agent's final summary lists it under **EXACT VALUES**,
which is a mislabel. Two further caveats: (i) `G8_circle.py` minimises over
**arc cuts only**, so what it computes is `max_x min_arc(x) ≥ max_x psi(x)` — a
different quantity, safe in direction but not A(k); (ii) my own optimiser returns
0.0399999990 / 0.0400000000 / 0.0399999979 for k = 3,4,5, i.e. values *below*
1/25, which by accepted fact 3 are impossible as maxima — a live demonstration
that these digits carry no information.

**U5. §2 "sup_k A(k) is the finite-configuration version of max_μ psi(Γ,μ)".**
The direction that matters (a proof on Γ covers every And(k)) is correct, since
each And(k) is an induced sub-configuration. The converse identification is
asserted with no density argument, and Γ's edge relation `d > 1/3` is *open*, so
limits can lose edges. Not used anywhere, but it is stated under "PROVED".

**U6. §7 TERMINAL LEMMA.** Explicitly flagged unproved by the report; my
independent evidence (symbolic identity, exact integer grid q ≤ 34 for the
product form, independent numeric max ratio 1.0000000000) found no falsifier.
Status unchanged: open.

---

## 4. NEW — proved during the audit (both strengthen G8)

**N1. The Andrásfai chain is an INDUCED chain, by the identity map.**
Writing And(k) and And(k+1) as circulants with connection set `{c ≡ 1 mod 3}`,
the identity map on `{0,1,…,3k−2}` is an induced embedding And(k) → And(k+1).

*Proof.* For `0 ≤ i < j ≤ 3k−2` put `t = j − i ∈ [1, 3k−2]`. In And(k) (mod
`3k−1`) the residue of `t` is `t`, so `i ~ j ⟺ t ≡ 1 (mod 3)`. In And(k+1) (mod
`3k+2`) the residue of `t` is again `t` because `t < 3k+2`, and the connection set
is `{1,4,…,3k+1}`, so again `i ~ j ⟺ t ≡ 1 (mod 3)`. The two conditions
coincide, and both connection sets are symmetric (`3k−1−c ≡ 1` and
`3k+2−c ≡ 1 mod 3` whenever `c ≡ 1 mod 3`). ∎
Verified k = 2..29 in `audit_G8_chain.py`; in particular **And(4) = And(k)[{0,…,10}]
for every k ≥ 4**.

Consequence: the monotonicity of `A(k)` (§1 Consequence 1) follows directly from
**accepted fact 3** (induced-subgraph monotonicity). The quoted Bondy–Hell
theorem `K_{p/q} → K_{p'/q'} iff p/q ≤ p'/q'` is correctly applied
(`gcd(3k−1,k) = 1`, `p ≥ 2q`) but is not needed.

**N2. The §6.3 block holds for EVERY k ≥ 4, not just k = 4, 5.**

*Proof.* Let `W = {0,…,10}`, so `And(k)[W] ≅ And(4)` for every `k ≥ 4` (N1).
Every induced C5 of `And(k)[W]` is an induced C5 of `And(k)`, and a cut `S` of
`And(k)` restricts to a cut `S ∩ W` of `And(k)[W]` with the same monochromatic
edges inside `W`. If some cut `S` of `And(k)` had exactly one monochromatic edge
in every induced C5 of `And(k)`, then `S ∩ W` would have exactly one
monochromatic edge in every one of the 33 induced C5s of `And(4)` — and the
exhaustive computation shows there is no such cut of And(4). ∎

So the verbatim blocking lemma of §6.3 upgrades from "verified at k = 4, 5" to a
theorem for all k ≥ 4: *no fixed distribution over cuts of And(k), arithmetic or
geometric, can certify `max psi(And(k)) ≤ 1/25` for any k ≥ 4.*

---

## 5. Argument defects (conclusions survive, justifications do not)

**D1. §6.3's stated justification is circular; repair below.**
Verbatim: *"Every induced C5 of And(k), uniformly weighted, is a maximiser
(accepted fact 3)."* Accepted fact 3 gives `max psi(And(k)) ≥ 1/25`, **not** that
`x*` is a maximiser — calling `x*` a maximiser presupposes `max psi = 1/25`,
which for k ≥ 3 is exactly the open question. The conclusion survives with a
repaired argument that never mentions maximisers:

> Suppose `psi(x) ≤ min_j q_{S_j}(x) ≤ Π_j q_{S_j}(x)^{w_j} ≤ 1/25` for all x.
> Let `x*` be uniform on an induced C5. By support reduction
> `psi(x*) = psi(C5, uniform) = 1/25` **exactly**, so `q_{S_j}(x*) ≥ psi(x*) = 1/25`
> for every j. A weighted geometric mean of numbers each ≥ 1/25 that is ≤ 1/25
> forces all of them to equal 1/25. Hence every `S_j` in `supp(w)` has exactly one
> monochromatic edge in every induced C5. Contradiction with the empty
> intersection.

The same repair covers the arithmetic case (`Σ_j w_j q_{S_j}(x*) ≥ 1/25` with
equality iff all `q_{S_j}(x*) = 1/25`).

**D2. §7 is a strengthening, not an equivalent reformulation.**
`Π_j q_j ≤ (Σa)^10/5^10` implies `max psi(And(3)) ≤ 1/25` but is not implied by
it (`min ≤ geometric mean` runs one way only). The report's word
"Equivalently" refers to the change of coordinates, which is fine, but the route
replaces the target by a strictly stronger inequality. That is a legitimate
tactic; it is not a reduction. **The terminal lemma is NOT of conjecture
strength** (it is one degree-10 inequality about one 8-vertex graph), so §7 is
not blocked by circularity — but with the lemma unproved, §7 delivers no theorem.

**D3. Value of the §7 route if closed.** Proving `max psi(And(3)) ≤ 1/25` would
give `bip(G) ≤ N²/25` for every G with `G → And(3)`, a strictly larger class than
`G → C5`. That is real but small; the report does not state it, and it does not
by itself move the `0.16N < δ ≤ 0.375N` band.

---

## 6. Failure-mode checklist (all items answered)

| failure mode | verdict |
|---|---|
| floating point on an acceptance path | **No** on the acceptance paths (all of §0, §3, §5, §6.2, §6.3, §7's integer checks are exact integers/Fractions). **Yes** in the final summary, which lists the float "Numeric ceiling A(k) = 0.0400000000" under **EXACT VALUES** — mislabel, see U4 |
| max cut confused with a local/greedy cut | **No.** Every cut minimum in the target and in my reimplementation is over all `2^{n−1}` cuts. I audited `G8_intsearch.cpp`'s two early-exit prunes (`if (s >= best) break` and the `cutoff` return) and both are sound for a max-min objective; my no-pruning, no-symmetry re-run returns identical M(q) |
| psi < 1/25 reported as a MAXIMUM for an odd-girth-5 graph | **Not present.** All reported maxima are exactly 1/25. The values 1/32, 4/121, 3/98, 9/289, 3/100 are correctly labelled `psi(uniform)`, not maxima, and §0 explicitly notes uniform is never the maximiser |
| integer enumeration silently excluding zero weights | **No.** `G8_intsearch.cpp` loops `t = 0..hi`; my independent full enumeration also starts at 0, and every extremal `a` found has zeros |
| triangle-freeness assumed but unused / false | **No.** And(k) verified triangle-free k ≤ 7; Γ's triangle-freeness proof is correct and is used |
| N odd / not divisible by 5 / disconnected / unbalanced blow-ups | **Covered.** The integer sweeps run every q, not only 5\|q, over all weight vectors including zeros, so unbalanced blow-ups and every residue of q mod 5 are inside. n = 3k−1 is odd for k even and even for k odd; both occur. And(k) is connected; no isolated vertices arise (zero weights are handled by support reduction, which is proved) |
| constant weakened to 1/25 + ε, hidden "N large" | **Not present.** Every acceptance inequality is `25·X ≤ q²` in integers |
| circularity / step of conjecture strength | **§6.3 as written, yes** (see D1) — repaired above, conclusion stands. §7's terminal lemma is strictly weaker than the conjecture, so §7 is not blocked |
| finite verification presented as a general argument | **Yes, twice:** §6.2 "for every k ≥ 3" (verified k ≤ 5) and §6.3 "for k ≥ 4" (verified k = 4,5). See U1 (still open) and N2 (now proved) |
| quoted literature whose hypotheses do not match | **No.** Bondy–Hell needs `gcd(p,q) = 1` and `p ≥ 2q`: here `gcd(3k−1,k) = 1` and `3k−1 ≥ 2k` ✓ (and N1 makes it unnecessary). `χ_f = n/α` needs vertex-transitivity: And(k) is a circulant ✓, and `α = k` is verified for k ≤ 7 |
| missing reproduction artifacts | **Minor.** `G8_wagner5.cpp/.exe` and `G8_w5quick.py` are cited for the §7 numbers but leave no output file on disk (unlike `G8_int_*.txt`). I reproduced both independently. Also `G8_certlp.py` contains a dead branch (`... if False else (None, None)`), harmless |

---

## 7. Files written by this audit

    E:\Projects\ErdosProblems\problems\23\round3\audit_G8.md            (this file)
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_core.py       invariants, exhaustive maxcut, bip table
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_hom.py        C5-CSP + brute force cross-check, Wagner iso
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_cuts.py       min nu(mono), induced-C5 active-cut intersection
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_terminal.py   symbolic (m,c) identity, terminal-lemma search
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_misc.py       rotation kernel (R1), arc cuts, C5 certificate
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_ext.py        hom chain, 6.3 test at k = 6,7, atom count
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_ext2.py       induced chain, arc cuts at structured points
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_chain.py      N1/N2: identity induced embedding, k = 2..29
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_num.py        numeric ceiling, fact-3 protocol
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_int.cpp/.exe  independent M(q), no-symmetry option
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_w5.cpp/.exe   5-cut min AND product forms, __int128
    E:\Projects\ErdosProblems\problems\23\round3\audit_G8_nu.cpp/.exe   min nu(mono) for k = 6,7
    data: audit_G8_int_k3.txt (no symmetry, q<=30), audit_G8_int_k3sym.txt (q<=50),
          audit_G8_int_k4.txt (q<=22), audit_G8_int_k5.txt (q<=20),
          audit_G8_w5.txt (q<=30), audit_G8_w5_34.txt (q<=34)
