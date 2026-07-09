import Mathlib

namespace Erdos23Delta0
namespace Ell5DistancePrune

/-- If a subgraph `K ≤ H` contains a geodesic whose image has exactly ambient distance
    length, then the `K`-distance equals the `H`-distance. -/
theorem dist_eq_of_le_of_geodesic_sub {V : Type*} (K H : SimpleGraph V) (hle : K <= H)
    (u v : V) (p : K.Walk u v)
    (hlen : (p.mapLe hle).length = H.dist u v) :
    K.dist u v = H.dist u v := by
  have hK_le : K.dist u v <= H.dist u v := by
    have hp : K.dist u v <= p.length := SimpleGraph.dist_le p
    have hmap : (p.mapLe hle).length = p.length := by simp
    omega
  have hH_le : H.dist u v <= K.dist u v := by
    have hconn : K.Reachable u v := p.reachable
    obtain ⟨q, hq⟩ := hconn.exists_walk_length_eq_dist
    have hdist : H.dist u v <= (q.mapLe hle).length := SimpleGraph.dist_le (q.mapLe hle)
    have hmap : (q.mapLe hle).length = q.length := by simp
    omega
  omega


end Ell5DistancePrune
end Erdos23Delta0
