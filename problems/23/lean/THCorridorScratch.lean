import Mathlib

/-!
Scratch formalization for the row-side TH-Corridor wrapper.

SUPERSEDED WARNING, 2026-07-01:
The intended `AtMostOneMiss` target of this scratch file is false on the hard
`h_blowup(3)` all-max side.  Keep this file only as archived plumbing for
walk/chain/minimal-corridor ideas.  The active row-side target is residual
Hall, formalized in `ResidualHallScratch.lean` and documented in
`RESIDUAL_HALL_CORNER_ATOM.md`.

This file does not prove the geometric TH-long / TH-rare discharges.  It
machine-checks the logical wrapper accepted in
`NO_TWO_HOLE_RESIDUAL_CORRIDOR.md`:

* a shortest two-hole corridor is represented by endpoints missed by a row and
  internal exits witnessed by that row;
* if every such corridor has either a long-lambda certificate or a rare-exchange
  certificate, and both certificate types contradict the scoped minimality
  assumptions, then no such corridor exists;
* if every pair of distinct missed exits yields such a corridor, then the row
  misses at most one exit in its residual component.
-/

namespace Erdos23
namespace THCorridor

open SimpleGraph

/-- The exit co-witness graph induced by a row-exit witness relation. -/
def coWitnessGraph {Row Exit : Type*} (Wit : Row → Exit → Prop) :
    SimpleGraph Exit where
  Adj e e' := e ≠ e' ∧ ∃ r, Wit r e ∧ Wit r e'
  symm := by
    intro e e' h
    rcases h with ⟨hne, r, he, he'⟩
    exact ⟨hne.symm, r, he', he⟩
  loopless := by
    intro e h
    exact h.1 rfl

/--
An alternating witness chain between exits: each step moves from one exit to a
distinct exit through a row witnessing both.

This is the abstract projection of connectivity in the residual bipartite
row-exit component.
-/
inductive WitnessChain {Row Exit : Type*} (Wit : Row → Exit → Prop) :
    Exit → Exit → Type _ where
  | refl (e : Exit) : WitnessChain Wit e e
  | step {e0 e1 ek : Exit} (r : Row)
      (hne : e0 ≠ e1) (h0 : Wit r e0) (h1 : Wit r e1)
      (tail : WitnessChain Wit e1 ek) : WitnessChain Wit e0 ek

/--
A loose alternating witness chain allows a row to witness the same exit twice.
This is the shape produced most directly by an incidence-component walk before
deleting stationary exit steps.
-/
inductive LooseWitnessChain {Row Exit : Type*} (Wit : Row → Exit → Prop) :
    Exit → Exit → Type _ where
  | refl (e : Exit) : LooseWitnessChain Wit e e
  | step {e0 e1 ek : Exit} (r : Row)
      (h0 : Wit r e0) (h1 : Wit r e1)
      (tail : LooseWitnessChain Wit e1 ek) : LooseWitnessChain Wit e0 ek

/-- A witness chain projects to a walk in the exit co-witness graph. -/
def WitnessChain.toWalk {Row Exit : Type*} {Wit : Row → Exit → Prop}
    {e0 ek : Exit} :
    WitnessChain Wit e0 ek → (coWitnessGraph Wit).Walk e0 ek
  | WitnessChain.refl _ => SimpleGraph.Walk.nil
  | WitnessChain.step r hne h0 h1 tail =>
      SimpleGraph.Walk.cons ⟨hne, r, h0, h1⟩ (WitnessChain.toWalk tail)

/-- A loose witness chain projects to a J-walk after deleting stationary steps. -/
noncomputable def LooseWitnessChain.toWalk
    {Row Exit : Type*} {Wit : Row → Exit → Prop}
    {e0 ek : Exit} :
    LooseWitnessChain Wit e0 ek → (coWitnessGraph Wit).Walk e0 ek
  | LooseWitnessChain.refl _ => SimpleGraph.Walk.nil
  | @LooseWitnessChain.step _ _ _ a b _ r h0 h1 tail => by
      let tailWalk := LooseWitnessChain.toWalk tail
      classical
      by_cases h : a = b
      · exact h.symm ▸ tailWalk
      · exact SimpleGraph.Walk.cons ⟨h, r, h0, h1⟩
          tailWalk

/--
If two exits are connected by an alternating witness chain, then there exists
a co-witness-graph walk between them.
-/
theorem exists_walk_of_witnessChain {Row Exit : Type*} {Wit : Row → Exit → Prop}
    {e0 ek : Exit} (chain : WitnessChain Wit e0 ek) :
    ∃ p : (coWitnessGraph Wit).Walk e0 ek, p = WitnessChain.toWalk chain :=
  ⟨WitnessChain.toWalk chain, rfl⟩

/-- A loose witness chain also supplies a co-witness-graph walk. -/
theorem exists_walk_of_looseWitnessChain
    {Row Exit : Type*} {Wit : Row → Exit → Prop}
    {e0 ek : Exit} (chain : LooseWitnessChain Wit e0 ek) :
    ∃ p : (coWitnessGraph Wit).Walk e0 ek,
      p = LooseWitnessChain.toWalk chain :=
  ⟨LooseWitnessChain.toWalk chain, rfl⟩

/--
Every walk in the exit co-witness graph expands to an alternating witness
chain.  This is the pure bridge from residual-component connectivity in `J`
to the chain object used by the corridor construction.
-/
noncomputable def WitnessChain.ofWalk {Row Exit : Type*} {Wit : Row → Exit → Prop}
    {e0 ek : Exit} :
    (coWitnessGraph Wit).Walk e0 ek → WitnessChain Wit e0 ek
  | SimpleGraph.Walk.nil => WitnessChain.refl _
  | SimpleGraph.Walk.cons h tail =>
      WitnessChain.step h.2.choose h.1
        h.2.choose_spec.1 h.2.choose_spec.2
        (WitnessChain.ofWalk tail)

/-- A co-witness-graph walk therefore supplies an alternating witness chain. -/
theorem exists_witnessChain_of_walk {Row Exit : Type*} {Wit : Row → Exit → Prop}
    {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek) :
    ∃ chain : WitnessChain Wit e0 ek, chain = WitnessChain.ofWalk p :=
  ⟨WitnessChain.ofWalk p, rfl⟩

/--
Abstract form of a shortest two-hole residual corridor for a fixed reference
row `f`.  The endpoints are missed by `f`; every internal exit of the corridor
is witnessed by `f`.

The fact that the corridor is shortest/minimal is not repeated here: it is the
application hypothesis used to *construct* this shape, and is already captured
in the kernel lemmas of `S2CoreScratch.lean`.
-/
def TwoHoleCorridor {Row Exit : Type*} (Wit Miss : Row → Exit → Prop)
    (f : Row) {e0 ek : Exit}
    (p : (coWitnessGraph Wit).Walk e0 ek) : Prop :=
  Miss f e0 ∧
  Miss f ek ∧
  ∀ i : ℕ, 0 < i → i < p.length → Wit f (p.getVert i)

/-- A row misses at most one exit. -/
def AtMostOneMiss {Row Exit : Type*} (Miss : Row → Exit → Prop)
    (f : Row) : Prop :=
  ∀ e e' : Exit, Miss f e → Miss f e' → e = e'

/--
If the endpoints of a co-witness corridor are chosen with minimum walk length
among all distinct missed-exit pairs for `f`, then every internal exit is not
missed.  When `not missed` implies `witnessed`, this is exactly a
`TwoHoleCorridor`.

This is the row-side `hexists` kernel: two distinct missed exits in one
residual component give a walk in `J`; choosing a shortest/minimal missed pair
turns that walk into the corridor shape consumed by the TH-Corridor wrapper.
-/
theorem twoHoleCorridor_of_minimal_missed_walk
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {f : Row} {e0 ek : Exit} {p : (coWitnessGraph Wit).Walk e0 ek}
    (he0 : Miss f e0) (hek : Miss f ek) (hne : e0 ≠ ek)
    (hmin :
      ∀ {x y : Exit}, Miss f x → Miss f y → x ≠ y →
        ∀ q : (coWitnessGraph Wit).Walk x y, p.length ≤ q.length)
    (hnotMiss_wit : ∀ e : Exit, ¬ Miss f e → Wit f e) :
    TwoHoleCorridor Wit Miss f p := by
  refine ⟨he0, hek, ?_⟩
  intro i hi0 hil
  apply hnotMiss_wit
  intro hmiss
  by_cases hne0 : e0 ≠ p.getVert i
  · have hle := hmin he0 hmiss hne0 (p.take i)
    have htake : (p.take i).length = i := by
      rw [SimpleGraph.Walk.take_length]
      exact Nat.min_eq_left (le_of_lt hil)
    rw [htake] at hle
    omega
  · push_neg at hne0
    have h_eq : p.getVert i = e0 := hne0.symm
    have hne_end : p.getVert i ≠ ek := by
      intro hend
      exact hne (h_eq.symm.trans hend)
    have hle := hmin hmiss hek hne_end (p.drop i)
    rw [SimpleGraph.Walk.drop_length] at hle
    omega

/--
Chain-facing version of `twoHoleCorridor_of_minimal_missed_walk`.

Once residual-component connectivity supplies an alternating witness chain,
this theorem composes `WitnessChain.toWalk` with the minimal missed-pair kernel
to produce the corridor shape consumed by the TH-Corridor wrapper.
-/
theorem twoHoleCorridor_of_minimal_witnessChain
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {f : Row} {e0 ek : Exit} (chain : WitnessChain Wit e0 ek)
    (he0 : Miss f e0) (hek : Miss f ek) (hne : e0 ≠ ek)
    (hmin :
      ∀ {x y : Exit}, Miss f x → Miss f y → x ≠ y →
        ∀ q : (coWitnessGraph Wit).Walk x y,
          (WitnessChain.toWalk chain).length ≤ q.length)
    (hnotMiss_wit : ∀ e : Exit, ¬ Miss f e → Wit f e) :
    TwoHoleCorridor Wit Miss f (WitnessChain.toWalk chain) :=
  twoHoleCorridor_of_minimal_missed_walk he0 hek hne hmin hnotMiss_wit

/--
Walk-facing version of the minimal missed-pair kernel.

Residual-component connectivity naturally produces a co-witness-graph walk;
choosing one with minimum length among all distinct missed pairs makes it a
`TwoHoleCorridor`.
-/
theorem twoHoleCorridor_of_minimal_connected_walk
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {f : Row} {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek)
    (he0 : Miss f e0) (hek : Miss f ek) (hne : e0 ≠ ek)
    (hmin :
      ∀ {x y : Exit}, Miss f x → Miss f y → x ≠ y →
        ∀ q : (coWitnessGraph Wit).Walk x y, p.length ≤ q.length)
    (hnotMiss_wit : ∀ e : Exit, ¬ Miss f e → Wit f e) :
    TwoHoleCorridor Wit Miss f p :=
  twoHoleCorridor_of_minimal_missed_walk he0 hek hne hmin hnotMiss_wit

/-- A nonempty family of walks contains one with minimum length. -/
theorem exists_shortest_walk_of_nonempty
    {V : Type*} (G : SimpleGraph V) {a b : V}
    (hwalk : Nonempty (G.Walk a b)) :
    ∃ p : G.Walk a b, ∀ q : G.Walk a b, p.length ≤ q.length := by
  classical
  let P : ℕ → Prop := fun n => ∃ p : G.Walk a b, p.length = n
  have hP : ∃ n, P n := by
    rcases hwalk with ⟨p⟩
    exact ⟨p.length, p, rfl⟩
  rcases Nat.find_spec hP with ⟨p, hp⟩
  refine ⟨p, ?_⟩
  intro q
  rw [hp]
  exact Nat.find_min' hP ⟨q, rfl⟩

/--
If every two-hole corridor has either a long-lambda certificate or a
minimum-lambda rare-exchange certificate, and each certificate is impossible in
the scoped minimal setting, then no two-hole corridor exists.
-/
theorem no_corridor_of_dichotomy
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (hdich :
      ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
      ¬ TwoHoleCorridor Wit Miss f p := by
  intro e0 ek f p hcorr
  rcases hdich f p hcorr with hlong | hrare
  · exact hnoLong f p hcorr hlong
  · exact hnoRare f p hcorr hrare

/--
Endpoint-tier splitter for the TH-Corridor dichotomy.

This isolates the two remaining geometric obligations:

* if at least one endpoint is high/long tier, the corridor supplies a
  `LongCert`;
* if both endpoints are minimum tier, the corridor supplies a `RareCert`.

The theorem is pure plumbing; it does not define or prove the tier predicate.
-/
theorem dichotomy_of_endpoint_split
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (IsLong : Exit → Prop)
    (hlong :
      ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          IsLong e0 ∨ IsLong ek → LongCert f p)
    (hrare :
      ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          ¬ IsLong e0 → ¬ IsLong ek → RareCert f p) :
    ∀ {e0 ek : Exit} (f : Row) (p : (coWitnessGraph Wit).Walk e0 ek),
      TwoHoleCorridor Wit Miss f p →
        LongCert f p ∨ RareCert f p := by
  classical
  intro e0 ek f p hcorr
  by_cases h0 : IsLong e0
  · exact Or.inl (hlong f p hcorr (Or.inl h0))
  · by_cases hk : IsLong ek
    · exact Or.inl (hlong f p hcorr (Or.inr hk))
    · exact Or.inr (hrare f p hcorr h0 hk)

/--
The component-local single-miss conclusion follows once every pair of distinct
missed exits produces a two-hole corridor and all two-hole corridors are
excluded.
-/
theorem atMostOneMiss_of_corridor_existence
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    (f : Row)
    (hexists :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        ∃ p : (coWitnessGraph Wit).Walk e e',
          TwoHoleCorridor Wit Miss f p)
    (hno :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        ¬ TwoHoleCorridor Wit Miss f p) :
    AtMostOneMiss Miss f := by
  intro e e' he he'
  by_contra hne'
  have hne : e ≠ e' := by
    intro h
    exact hne' h
  rcases hexists e e' he he' hne with ⟨p, hp⟩
  exact hno p hp

/--
One-shot wrapper: corridor construction plus TH-long/TH-rare dichotomy and the
two impossibility lemmas imply the row misses at most one residual exit.
-/
theorem atMostOneMiss_of_thCorridor_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row)
    (hexists :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        ∃ p : (coWitnessGraph Wit).Walk e e',
          TwoHoleCorridor Wit Miss f p)
    (hdich :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  apply atMostOneMiss_of_corridor_existence f hexists
  intro e0 ek p hcorr
  rcases hdich p hcorr with hlong | hrare
  · exact hnoLong p hcorr hlong
  · exact hnoRare p hcorr hrare

/--
Chain-facing one-shot wrapper.

This packages the residual-component input in its most concrete form: every
distinct missed pair has an explicit co-witness chain whose projected walk is
minimal among all missed-pair walks.  The rest is the already-kernelized
TH-Corridor target.
-/
theorem atMostOneMiss_of_minimal_missed_chain_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row)
    (hchain :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        ∃ chain : WitnessChain Wit e e',
          (∀ {x y : Exit}, Miss f x → Miss f y → x ≠ y →
            ∀ q : (coWitnessGraph Wit).Walk x y,
              (WitnessChain.toWalk chain).length ≤ q.length) ∧
          (∀ z : Exit, ¬ Miss f z → Wit f z))
    (hdich :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  apply atMostOneMiss_of_thCorridor_target f
  · intro e e' he he' hne
    rcases hchain e e' he he' hne with ⟨chain, hmin, hnotMiss_wit⟩
    refine ⟨WitnessChain.toWalk chain, ?_⟩
    exact twoHoleCorridor_of_minimal_witnessChain
      chain he he' hne hmin hnotMiss_wit
  · exact hdich
  · exact hnoLong
  · exact hnoRare

/--
Walk-facing one-shot wrapper.

This is the direct form of the residual-component statement in the proof
notes: every distinct missed pair has a minimal co-witness-graph walk, and the
TH-long/TH-rare dichotomy excludes the resulting corridor.
-/
theorem atMostOneMiss_of_minimal_missed_walk_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row)
    (hwalk :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        ∃ p : (coWitnessGraph Wit).Walk e e',
          (∀ {x y : Exit}, Miss f x → Miss f y → x ≠ y →
            ∀ q : (coWitnessGraph Wit).Walk x y, p.length ≤ q.length) ∧
          (∀ z : Exit, ¬ Miss f z → Wit f z))
    (hdich :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  apply atMostOneMiss_of_thCorridor_target f
  · intro e e' he he' hne
    rcases hwalk e e' he he' hne with ⟨p, hmin, hnotMiss_wit⟩
    exact ⟨p, twoHoleCorridor_of_minimal_connected_walk
      p he he' hne hmin hnotMiss_wit⟩
  · exact hdich
  · exact hnoLong
  · exact hnoRare

/--
Connected-pair one-shot wrapper.

This is the closest abstract form to the residual-component argument: if a row
has two missed exits, connectivity supplies at least one J-walk between every
distinct missed pair.  Choose a globally shortest such missed-pair walk by
well-ordering of `Nat`; the minimal-pair kernel turns it into a
`TwoHoleCorridor`, and the TH target excludes it.
-/
theorem atMostOneMiss_of_connected_missed_pairs_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row)
    (hconnected :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        Nonempty ((coWitnessGraph Wit).Walk e e'))
    (hnotMiss_wit : ∀ z : Exit, ¬ Miss f z → Wit f z)
    (hdich :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  classical
  intro e e' he he'
  by_contra hne'
  have hne : e ≠ e' := by
    intro h
    exact hne' h
  rcases hconnected e e' he he' hne with ⟨p0⟩
  let HasMissedWalkLength : ℕ → Prop := fun n =>
    ∃ x y : Exit, Miss f x ∧ Miss f y ∧ x ≠ y ∧
      ∃ p : (coWitnessGraph Wit).Walk x y, p.length = n
  have hnonempty : ∃ n, HasMissedWalkLength n := by
    exact ⟨p0.length, e, e', he, he', hne, p0, rfl⟩
  let n := Nat.find hnonempty
  have hn : HasMissedWalkLength n := Nat.find_spec hnonempty
  rcases hn with ⟨x, y, hx, hy, hxy, p, hp_len⟩
  have hmin :
      ∀ {a b : Exit}, Miss f a → Miss f b → a ≠ b →
        ∀ q : (coWitnessGraph Wit).Walk a b, p.length ≤ q.length := by
    intro a b ha hb hab q
    have hq : HasMissedWalkLength q.length :=
      ⟨a, b, ha, hb, hab, q, rfl⟩
    have hle : n ≤ q.length := Nat.find_min' hnonempty hq
    simpa [hp_len] using hle
  have hcorr : TwoHoleCorridor Wit Miss f p :=
    twoHoleCorridor_of_minimal_connected_walk
      p hx hy hxy hmin hnotMiss_wit
  rcases hdich p hcorr with hlong | hrare
  · exact hnoLong p hcorr hlong
  · exact hnoRare p hcorr hrare

/--
Connected-pair wrapper with the endpoint-tier split exposed directly.

This is the proof-facing shape of `hdich`: high-tier endpoints discharge by
the Long geometry, while two minimum-tier endpoints discharge by the Rare
geometry.
-/
theorem atMostOneMiss_of_endpoint_split_connected_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row) (IsLong : Exit → Prop)
    (hconnected :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        Nonempty ((coWitnessGraph Wit).Walk e e'))
    (hnotMiss_wit : ∀ z : Exit, ¬ Miss f z → Wit f z)
    (hlong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          IsLong e0 ∨ IsLong ek → LongCert f p)
    (hrare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          ¬ IsLong e0 → ¬ IsLong ek → RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  apply atMostOneMiss_of_connected_missed_pairs_target f hconnected hnotMiss_wit
  · intro e0 ek p hcorr
    classical
    by_cases h0 : IsLong e0
    · exact Or.inl (hlong p hcorr (Or.inl h0))
    · by_cases hk : IsLong ek
      · exact Or.inl (hlong p hcorr (Or.inr hk))
      · exact Or.inr (hrare p hcorr h0 hk)
  · exact hnoLong
  · exact hnoRare

/--
Chain-connected version of `atMostOneMiss_of_connected_missed_pairs_target`.
The residual component may supply genuine alternating witness chains instead
of J-walks.
-/
theorem atMostOneMiss_of_witnessChain_connected_missed_pairs_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row)
    (hchain :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        Nonempty (WitnessChain Wit e e'))
    (hnotMiss_wit : ∀ z : Exit, ¬ Miss f z → Wit f z)
    (hdich :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  apply atMostOneMiss_of_connected_missed_pairs_target f
  · intro e e' he he' hne
    rcases hchain e e' he he' hne with ⟨chain⟩
    exact ⟨WitnessChain.toWalk chain⟩
  · exact hnotMiss_wit
  · exact hdich
  · exact hnoLong
  · exact hnoRare

/--
Loose-chain-connected version.  This is the closest Lean surface to a raw
residual incidence-component walk: stationary exit steps are deleted by
`LooseWitnessChain.toWalk`.
-/
theorem atMostOneMiss_of_looseWitnessChain_connected_missed_pairs_target
    {Row Exit : Type*} {Wit Miss : Row → Exit → Prop}
    {LongCert RareCert :
      ∀ {e0 ek : Exit}, Row → (coWitnessGraph Wit).Walk e0 ek → Prop}
    (f : Row)
    (hchain :
      ∀ e e' : Exit, Miss f e → Miss f e' → e ≠ e' →
        Nonempty (LooseWitnessChain Wit e e'))
    (hnotMiss_wit : ∀ z : Exit, ¬ Miss f z → Wit f z)
    (hdich :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p →
          LongCert f p ∨ RareCert f p)
    (hnoLong :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ LongCert f p)
    (hnoRare :
      ∀ {e0 ek : Exit} (p : (coWitnessGraph Wit).Walk e0 ek),
        TwoHoleCorridor Wit Miss f p → ¬ RareCert f p) :
    AtMostOneMiss Miss f := by
  apply atMostOneMiss_of_connected_missed_pairs_target f
  · intro e e' he he' hne
    rcases hchain e e' he he' hne with ⟨chain⟩
    exact ⟨LooseWitnessChain.toWalk chain⟩
  · exact hnotMiss_wit
  · exact hdich
  · exact hnoLong
  · exact hnoRare

end THCorridor
end Erdos23
