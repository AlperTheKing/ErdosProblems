Blocked by the filesystem sandbox: all `apply_patch` writes fail, including inside the assigned `lane04_fixtures_small` directory and workspace `tmp`. Therefore I could not produce the required replay artifacts without violating the no-other-write rule.

I did pin the N=175 constructor:

- Extend the canonical N=167 active-circuit fixture.
- Add `x=167, y=168, z=169`.
- Add blue edges `x–0`, `9–y`, `y–z`.
- Add bad edge `x–z`.
- Add a private six-edge blue path from `x` to `z` with internal vertices `170..174`.
- Result: `N=175`, `E=245`, `B=216`, 29 bad edges, max cut 216, and `Γ=725`.

No `REPORT.md`, `result.json`, or manifest was emitted because workspace writes were unavailable.