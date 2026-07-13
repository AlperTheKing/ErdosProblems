import Erdos23Delta0.Gamma.CheckedMicroReservationLedger

open Erdos23Delta0.Gamma.CheckedMicroReservationLedger

#check PhysicalHalfKey.ofFreeHalf
#check Data.PhysicalHalfExclusive
#check Data.BaseKeyComponentCoherent
#check GraphExistenceHypothesis

#print axioms PhysicalHalfKey.ofFreeHalf_injective
#print axioms Data.check_eq_true_iff
#print axioms Data.sound_of_check_eq_true
#print axioms Data.source_eq_of_key_eq
#print axioms Data.source_component_eq_of_same_base
#print axioms Data.term_eq_of_source_eq
#print axioms Data.newSpend_le_residualCapQ
#print axioms Data.residualCapQ_nonneg
#print axioms Data.baseComponentOf_source
#print axioms sound_of_graph_existence
