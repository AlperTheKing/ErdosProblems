# Layer-cake / port-Hall proof of the unified atom (GPT-Pro, 2026-06-30)

Goal: B_L(P) = 25*M(P) >= 0 for every gamma-min connected-B max cut, bad edge f, shortest blue
L-geodesic P=(x_0..x_{L-1}).  (=> PATH-GAMMA => Erdos #23 beta<=N^2/25.)

## Verified scaffolding (exact Fraction, status)

(1) LAYER-CAKE IDENTITY  [VERIFIED 0 fails on 1.07M+ rows: census N<=11, Grotzsch=Myc(C5),
    Myc(Grotzsch) N=23, C5/C7 lopsided blowups N<=16, glued islands, H?AFBo]]
      B_L(P) - DG(x_0) - DG(x_{L-1}) = sum_{r=0}^{N-1} (2r+1) Z_r(P),
      Z_r = L*(1-m_r) + 25*(L-a_r(P))/(2r+1) - chi_P(r) - delta_P*1_{r<L}.
    m_r=#{bad g: L_g>r}; a_r=sum_{g:L_g>r} a_g(P), a_g=sum_i p_g(x_i) through-frac; delta_P=(S/L)^2-q;
    chi_P(r)=layer profile of the DG closed form at the two endpoints (=0 unless that flip is neutral+conn).
    On the 99.76% of rows with non-neutral endpoints, chi_P=0 and this DIRECTLY decomposes B_L (non-vacuous).

(2) TRUNCATED RESOURCE FORM  [VERIFIED 0 mismatches, _trunc_verify.py]
      Tail_k(P) := sum_{r>=k} (2r+1) Z_r(P)
                 = L*(N^2-k^2-Gamma_k) + 25*(L*(N-k)-A_k(P)) - phi_k(L)*delta_P - E_k(P),
    phi_k(t)=max(t^2-k^2,0); Gamma_k=sum_{g in M} phi_k(L_g); A_k=sum_{g} a_g(P)*max(L_g-k,0);
    E_k=sum_{r>=k}(2r+1)chi_P(r)=DG_k(x_0)+DG_k(x_{L-1}) (truncated endpoint-flip Gamma variation).

(3) TAIL DOMINANCE  Tail_k(P) >= 0 for every k   [VALIDATED 0 fails on the full 1.07M+ battery;
    pointwise Z_r>=0 FAILS, only the tail survives].  Tail_0 => B_L - DG0 - DGL >= 0 => (gamma-min DG>=0)
    => B_L>=0 => atom.

## The proof of (3) (GPT-Pro convex-order port-Hall) -- SKETCH, crux open

PORT-INTERVAL TAIL HALL LEMMA.  For each k let Omega_k(P) = multiset of endpoint-flip port intervals whose
endpoint-flip length > k; len_k(J) = truncated length of interval J above level k.  Then
   sum_{J in Omega_k(P)} len_k(J) <= L*(N^2-k^2-Gamma_k) + 25*(L*(N-k)-A_k(P)) - phi_k(L)*delta_P.
This is exactly Tail_k>=0.

PROOF (convex-order greedy Hall):
- Endpoint port obligations are INTERVALS (Step I).  Triangle-free => no length-3 port collapse => every
  bad-edge reroute has length >=5; a blue geodesic crossing P enters/leaves P in a CONTIGUOUS interval
  (else a shorter blue route or a triangle).
- Two resources match the obligations: (A) bad-edge geodesic layers L_g>k [weighted count L*Gamma_k inside
  L*(N^2-k^2-Gamma_k)]; (B) unused path slots above k [weighted count 25*A_k inside 25*(L*(N-k)-A_k)].
- AM-GM correction phi_k(L)*delta_P is the penalty for nonuniform path loads (already paid by C_L).
- Greedy match from large r downward: works because both sides are nested TAILS => only tail (not pointwise)
  inequalities survive.  Coefficient 25 is forced by odd-girth>=5 (five-slot corridor payment).

CRUX (gamma-minimality, the one step still to make rigorous):
  gamma-minimality is used MORE deeply than DG_0(x)>=0.  A FAILURE of the tail Hall inequality at level k
  would EXTRACT a neutral connected Gamma-DECREASING port switch (a singleton endpoint flip for k=0; a
  parity-completed endpoint-port switch for k>0), contradicting gamma-minimality.  Making "tail Hall failure
  => neutral Gamma-decreasing switch" precise is the remaining mathematical content (Codex's switch-extraction
  leg).  Everything else above is exact-verified.

Files: _layer_gate.py (identity+pointwise+tail), _layer_gate_full.py, _layer_gate_n11.py, _layer_gate_myc23.py,
_trunc_verify.py.  GPT chat: "Spectral Inequality Proof".
