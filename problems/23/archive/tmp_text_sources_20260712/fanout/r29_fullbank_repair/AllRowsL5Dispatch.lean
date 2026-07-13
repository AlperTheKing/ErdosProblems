import Erdos23Delta0.Rows.RowPartition

namespace Erdos23Delta0
namespace R29FullBankRepair

open CertGraph
open RowPartitionCore

/-- If every recorded row has length five, every component in every component
table is an all-L5 component.  No connectivity property is needed. -/
theorem componentAllL5_of_allRowsL5
    {rows : RowDB} (D : K2ComponentData rows)
    (hAll : forall i : RowIdx rows, rowEll rows i = 5)
    (comp : Fin D.componentCount) :
    D.ComponentAllL5 comp := by
  intro i _hi
  exact hAll i

theorem isEQODL1Row_of_allRowsL5
    {rows : RowDB} (D : K2ComponentData rows)
    (hAll : forall i : RowIdx rows, rowEll rows i = 5)
    (i : RowIdx rows) :
    D.IsEQODL1Row i := by
  exact componentAllL5_of_allRowsL5 D hAll (D.compOfRow i)

theorem not_isBranchBRow_of_allRowsL5
    {rows : RowDB} (D : K2ComponentData rows)
    (hAll : forall i : RowIdx rows, rowEll rows i = 5)
    (i : RowIdx rows) :
    Not (D.IsBranchBRow i) := by
  exact fun hBranch => hBranch (isEQODL1Row_of_allRowsL5 D hAll i)

end R29FullBankRepair
end Erdos23Delta0

#print axioms Erdos23Delta0.R29FullBankRepair.componentAllL5_of_allRowsL5
#print axioms Erdos23Delta0.R29FullBankRepair.isEQODL1Row_of_allRowsL5
#print axioms Erdos23Delta0.R29FullBankRepair.not_isBranchBRow_of_allRowsL5
