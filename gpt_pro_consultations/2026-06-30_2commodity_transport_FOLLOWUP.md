# GPT-Pro follow-up 2026-06-30 — corrected 2-commodity transport; prove per-component volume PREFIX

## Question sent

Follow-up to your level-transport answer. I implemented your step-10 exactly (rational max-flow) and tested it
on my full battery (~190k triangle-free max-cut configs, all gamma-min cuts, incl iterated Mycielskians to N=23
and glued multi-component graphs). RESULT: your literal 3-arc construction is INFEASIBLE on 42/103 of a
curated set once ALL max-cuts are tested -- first failure a glued graph C5|C7 joined by a single bridge edge.
The min-cut diagnosis is exactly what you predicted: a CUT EDGE covered by NO geodesic (the bridge) generates
pressure debt 5N but has no same-geodesic source to pay it.

THE FIX (feasible on ALL 189,497 configs, 0 infeasible): a TWO-COMMODITY causal transport.
  - VOLUME sinks (the alpha_j<0 over-load atoms) are paid ONLY within the SAME K-COMPONENT (= the
    geodesic-connected component: union-find where each bad-edge geodesic path is a clique). Causal i<=j.
  - PRESSURE sinks (5N*sigma_j*Delta_j) are paid by ANY causal source (non-local). The bridge forces this.
So the proof now SPLITS into two independent Hall conditions, both of which I have exact-verified hold on the
whole battery:
  (A) PER-COMPONENT VOLUME PREFIX: for every K-component c and every threshold tau,
        Phi_c(tau) := integral_0^tau 25*(N + eta - 2s) * |H_s ∩ c| ds  >= 0,    eta = N^2/25 - beta.
      (the volume-only running balance restricted to one component; pressure removed.)
  (B) GLOBAL PRESSURE: the total pressure debt 5N*(TV_cut - TV_bad) is covered by the leftover global bank.
      I separately verified the clean inequality  5*(N^2 - Gamma) >= TV_cut(T) - TV_bad(T)  (Gamma=sum ell^2;
      equality at the C5[t] extremal), so total pressure debt = 5N(TVcut-TVbad) <= 25N(N^2-Gamma).
  Also the DEPOSIT half (s<=N/2) is a clean single-superlevel inequality, both forms exact-verified:
      h*(N^2 - 25|M|) >= N*sigma(H)   and the sharper   h*(N^2 - Gamma) >= N*sigma(H)   on full-low superlevels.

MAIN QUESTION: prove (A), the per-component volume PREFIX Phi_c(tau) >= 0. A single K-component c is generated
by the shortest odd-cycle geodesics (length ell>=5) of the bad edges whose geodesics meet c; its load T|c is
exactly the geodesic-traffic of those cycles. Note Phi_c(infinity) = 25*[(N+eta)*Gamma_c - sum_{v in c} T_v^2]
where Gamma_c = sum_{v in c} T_v. Concretely:
  (i) Is Phi_c(tau)>=0 a consequence of a per-odd-cycle "five-slot" load-distribution fact -- that the load a
      single geodesic odd cycle of length ell>=5 deposits at low levels (s<theta) always exceeds what it
      withdraws at high levels (s>theta), and that this survives superposition of overlapping cycles in c?
  (ii) What is the right per-component invariant: is it sum_{v in c}T_v^2 <= (N+eta)*Gamma_c (the tau=inf
      endpoint), and does the prefix (all tau) follow from a Karamata/majorization argument because within a
      component the load profile is "more spread toward low levels" than the threshold theta=(N+eta)/2?
  (iii) Or is the component itself the wrong unit -- should I instead transport per BAD-EDGE geodesic atom
      (one odd cycle) and prove the single-cycle inequality, then sum?
Please give the cleanest provable form of (A) and the argument, in enough detail to verify on exact examples
(I can test any per-component or per-cycle inequality on the full battery in exact rational arithmetic).
Key facts: ell(f)>=5; sum_v T=Gamma; on each cut edge T varies, on each bad edge T jumps; max-cut gives
delta_M(H_s)<=delta_B(H_s); the global extremal is the balanced C5 blow-up (T==N, one K-component, eta=0).

## Answer (GPT-Pro, 2026-06-30) — 1-line: (A) <=> single per-component second-moment (CV); proven prefix-collapse

CLEAN REDUCTION (rigorous, I re-derived it). Let A := N + eta = N + N^2/25 - beta. For K-component c,
h_c(s):=|H_s cap c|. Then (1/25)*Phi_c(tau) = int_0^tau (A-2s) h_c(s) ds, with derivative (A-2tau)*h_c(tau).
Sign = sign(A-2tau): Phi_c RISES for tau<A/2, FALLS for tau>A/2 -> UNIMODAL, Phi_c(0)=0. Hence
  Phi_c(tau) >= 0 for ALL tau  <=>  Phi_c(infinity) >= 0.
And (1/25)Phi_c(infinity) = A*Gamma_c - sum_{v in c} T_v^2 (Gamma_c=sum_{v in c}T_v). So (A) is EXACTLY
  (CV)   sum_{v in c} T(v)^2  <=  (N + N^2/25 - beta) * sum_{v in c} T(v),   for every K-component c.
NO separate prefix difficulty after (CV). [I verified this equivalence by hand; it is airtight.]

WHY per-cycle is the WRONG unit: (CV) is QUADRATIC in the superposed load T = sum_f (ell_f/|cyc_f|) p_f; the
cross terms 2 sum_{f<g} ell(f)ell(g) <p_f,p_g> are the whole issue. A per-bad-edge-atom proof misses them.

GPT's proof plan for (CV) ("Hot Core Bundle"): the 1-D inequality is sum_i a_i^2 ... <= ... (N+something);
sharp only for the balanced C5 bundle. Proof of the bundle inequality: set a_i = ..., max-cut (P) gives
a relation a_i ~ a_{i+/-1}; sum cyclically; AM-GM; equality requires all a_i equal which for an ODD cycle
forces the balanced C5 blow-up. Then a "Hot Core Bundle Lemma": if a component violates (CV), pick a
density-maximal subset F and COMPRESS to a coherent bundle B; bad edges OUTSIDE the bundle only increase the
global N-budget, reducing (CV) to a GLOBAL SLACK inequality (outside bad edges can't consume more than the
vertex budget). [Bundle-compression details are heuristic; the CLEAN, verifiable deliverable is the reduction
(A)<=>(CV) above + the target (CV).]

## My verification
(A)<=>(CV) reduction PROVEN (unimodality). Gating (CV) Sum_{v in c}T_v^2 <= (N+N^2/25-beta)*Gamma_c per
K-component on the full battery (_cv_gate.py). Remaining proof: (CV) per component [the second-moment, my leg]
+ PRESSURE-SURPLUS-HALL [global, Codex] + deposit h(N^2-Gamma)>=N sigma [Codex]. All four exact-validated.
