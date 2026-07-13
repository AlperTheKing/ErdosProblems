Delivered in [child_05_dual](E:\Projects\ErdosProblems\tmp\fanout\common_blue_proof\child_05_dual):

- [REPORT.md](E:\Projects\ErdosProblems\tmp\fanout\common_blue_proof\child_05_dual\REPORT.md)
- [CERTIFICATE_SCHEMA.md](E:\Projects\ErdosProblems\tmp\fanout\common_blue_proof\child_05_dual\CERTIFICATE_SCHEMA.md)
- [check_dual.py](E:\Projects\ErdosProblems\tmp\fanout\common_blue_proof\child_05_dual\check_dual.py)
- [abstract_countermodel.json](E:\Projects\ErdosProblems\tmp\fanout\common_blue_proof\child_05_dual\abstract_countermodel.json)

Main result: every Hall obstruction saturates to complete owner fibers, reducing the target to owner-shore capacity inequalities. Corrected two-edge surplus proves individual arc soundness but cannot imply distinct-source capacity.

Minimal open lemma: `OwnerShoreCapacity`, stated precisely in the report.

Exact checker and independent replay both pass:

```text
demand=2 neighborhood=1 defect=1
dual_objective=1 primal_target=2
strict_farkas=true
```

No floating-point arithmetic, solver dependency, `sorry`, `admit`, or `native_decide`.