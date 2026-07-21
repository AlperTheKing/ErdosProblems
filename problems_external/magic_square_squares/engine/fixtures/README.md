# Independent verifier calibration fixtures

No strict positive end-to-end fixture is included. A fixture containing nine
distinct positive integer squares with all eight line sums equal would be a
solution of the open problem itself.

The two positive fixtures are positive witnesses for separate predicates:

- positive_square_domain.txt passes positivity, exact-square, and
  distinctness checks, then is expected to fail with SUM_MISMATCH.
- positive_magic_structure.txt passes positivity, distinctness, and all
  eight equal-sum checks, then is expected to fail with NOT_SQUARE.

The other fixtures exercise distinct strict rejection classes. The executable's
--self-test mode independently exercises parsing, arbitrary-precision exact
square roots, each positive predicate witness, and all rejection classes.
