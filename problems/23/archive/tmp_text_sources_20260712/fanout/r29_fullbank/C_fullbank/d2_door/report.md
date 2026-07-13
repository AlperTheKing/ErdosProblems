Completed the R29 all-anchor Door audit.

Key result:

- Raw legacy FreeHalf union: `19925` candidates, conditionally `19925` unit capacities.
- Per owner `0,1,2`: `8375` raw candidates each.
- Compiled-admissible Doors: `0` for every owner.
- Compiled-admissible capacity: `0`.

The `19925` raw candidates cannot legally be counted as Doors. The compiled interfaces require instantiated `OwnEdgeDoorSourceData.Checked` and `DoorWallAdapter` bridges. No R29 instantiation exists. Own-edge incidence is supplied at the interface boundary, not graph-derived.

Artifacts:

- [Audit report](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d2_door/report.md)
- [Replay script](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d2_door/replay_door_audit.py)
- [JSON certificate](E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank/C_fullbank/d2_door/door_certificate.json)

Certificate SHA-256: `389d55487add4ce289a81d0ad61eea8c19af68670bbce3d9554dd707165e646b`.