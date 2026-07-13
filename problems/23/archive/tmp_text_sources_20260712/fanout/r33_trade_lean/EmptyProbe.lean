import Erdos23Delta0.Gamma.Pattern5StaticOwnership

namespace EmptyProbe

variable {Obligation SourceBase Comp : Type*} [DecidableEq Obligation]

structure Match where
  matched : Finset Obligation
  assign : {d // d ∈ matched} ↪ (SourceBase × Fin 2)

def empty : Match (Obligation := Obligation) (SourceBase := SourceBase) where
  matched := ∅
  assign :=
    { toFun := fun d => (Finset.notMem_empty d.1 d.2).elim
      inj' := fun d _ => (Finset.notMem_empty d.1 d.2).elim }

end EmptyProbe
