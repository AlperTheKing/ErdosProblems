/-
Erdős #23 δ=0 — L3: Packet exchange, arithmetic core.
Per LEAN_PACKETEXCHANGE_DESIGN_GPTPRO.md: the theorem is assembled from two
per-orientation counting inequalities (each obtained from an injection into the
ordered pair box plus σ ≥ 0), summed and converted to the rational form
m_R + h/2 ≤ r²/25 + d/2. This module verifies the assembly arithmetic; the
per-orientation injection card computations are the remaining graph-side
obligations (OrientExchangeCert, next module increment).
-/

import Mathlib

namespace Erdos23Delta0
namespace PacketExchange

/-- Orientation of the exchange. -/
inductive POrient
  | pos
  | neg
deriving DecidableEq

/-- Per-orientation counting: the injection into the ordered pair box gives
    25·m_R + 25·h_o + 25·δ_B ≤ r² + 25·d_o + 25·δ_M; max-cut (δ_M ≤ δ_B)
    then drops the boundary terms. All ℕ, r² passed as an opaque count. -/
theorem orient_count (mR h_o blue bad r2 d_o : ℕ)
    (hinj : 25*mR + 25*h_o + 25*blue ≤ r2 + 25*d_o + 25*bad)
    (hsigma : bad ≤ blue) :
    25*mR + 25*h_o ≤ r2 + 25*d_o := by
  omega

/-- Summing the two orientations (h and d split by definition). -/
theorem orient_sum (mR h_pos h_neg d_pos d_neg r2 : ℕ)
    (hpos : 25*mR + 25*h_pos ≤ r2 + 25*d_pos)
    (hneg : 25*mR + 25*h_neg ≤ r2 + 25*d_neg) :
    50*mR + 25*(h_pos + h_neg) ≤ 2*r2 + 25*(d_pos + d_neg) := by
  omega

/-- Division-free ⟹ archived rational form m_R + h/2 ≤ r²/25 + d/2. -/
theorem to_rational (mR h d r : ℚ)
    (h50 : 50*mR + 25*h ≤ 2*r^2 + 25*d) :
    mR + h/2 ≤ r^2/25 + d/2 := by
  linarith

/-- End-to-end ℕ→ℚ: the two orientation inequalities give the packet bound. -/
theorem packet_exchange_of_orient (mR h_pos h_neg d_pos d_neg r : ℕ)
    (hpos : 25*mR + 25*h_pos ≤ r^2 + 25*d_pos)
    (hneg : 25*mR + 25*h_neg ≤ r^2 + 25*d_neg) :
    (mR : ℚ) + (h_pos + h_neg : ℕ)/2 ≤ (r : ℚ)^2/25 + (d_pos + d_neg : ℕ)/2 := by
  have h := orient_sum mR h_pos h_neg d_pos d_neg (r^2) hpos hneg
  have hq : 50*(mR : ℚ) + 25*((h_pos + h_neg : ℕ) : ℚ) ≤
      2*(r : ℚ)^2 + 25*((d_pos + d_neg : ℕ) : ℚ) := by
    exact_mod_cast h
  linarith

end PacketExchange
end Erdos23Delta0
