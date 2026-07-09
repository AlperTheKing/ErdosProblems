import Mathlib

namespace Erdos23Delta0
namespace ScratchT6State

open Finset

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V} {u v : V}

theorem no_three_common_edges_len4_same_endpoints
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4)
    (hne : p.edges.toFinset ≠ q.edges.toFinset) :
    (p.edges.toFinset ∩ q.edges.toFinset).card ≠ 3 := by
  intro h3
  cases p with
  | nil => simp at hlp
  | @cons _ a _ hpa p1 =>
    cases p1 with
    | nil => simp at hlp
    | @cons _ b _ hpb p2 =>
      cases p2 with
      | nil => simp at hlp
      | @cons _ c _ hpc p3 =>
        cases p3 with
        | nil => simp at hlp
        | @cons _ d _ hpd p4 =>
          cases p4 with
          | nil =>
            cases q with
            | nil => simp at hlq
            | @cons _ a' _ hqa q1 =>
              cases q1 with
              | nil => simp at hlq
              | @cons _ b' _ hqb q2 =>
                cases q2 with
                | nil => simp at hlq
                | @cons _ c' _ hqc q3 =>
                  cases q3 with
                  | nil => simp at hlq
                  | @cons _ d' _ hqd q4 =>
                    cases q4 with
                    | nil =>
                      simp only [SimpleGraph.Walk.edges_cons, SimpleGraph.Walk.edges_nil,
                        List.toFinset_cons, List.toFinset_nil] at hne h3 hp hq ⊢
                      trace_state
                      fail_if_success grind
                      admit
                    | @cons _ e' _ hqe q5 => simp at hlq
          | @cons _ e _ hpe p5 => simp at hlp

end ScratchT6State
end Erdos23Delta0
