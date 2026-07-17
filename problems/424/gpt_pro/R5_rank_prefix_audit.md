# GPT-Pro R5 audit: exact reformulation, no rank-prefix proof

## Verdict

R5 does not prove the requested additive-one rank-prefix theorem. It also
does not prove the earlier image inequality, the one-step preservation
theorem, or a counterexample satisfying the image hypothesis.

It gives:

1. an exact seed-2 shell/chain identity for arbitrary forward-closed sets;
2. a finite forward-closed set for which `H_T(74)>Q_T(74)`.

The identity is a fixed-set version of the seed-2-chain bookkeeping already
proved in C30. The finite example contains splitless holes and therefore does
not challenge the image or splitless-free gates. It is useful only as a sharp
warning that forward closure by itself is insufficient.

## Exact claims replayed

For

\[
I=\{6,8,11,15,29,54,57,74\},\qquad T_0=\mathcal A\setminus I,
\]

every admissible distinct factorization of `n+1` for `n in I` has an endpoint
in `I`. Hence `T_0` is forward closed.

The independent checker verified, for every cutoff `2 <= X <= 1000`:

- the boundary identity (1);
- the shell identity (2);
- the chain identity (4).

At `X=74` it finds exactly

```text
hard holes: [54, 74]
healed seed-2 parents: [11]
H-Q: 1
```

Thus the finite obstruction is exact. It is not an image obstruction because
`12 in T_0`, while no admissible pair generates `12` (`13` is prime), so no
set `S` can satisfy `T_0=F(S)`.

## Reproduction

```powershell
python problems/424/gpt_pro/R5_shell_identity_audit.py
```

Artifacts:

```text
R5_rank_prefix_raw.md
  4F280A78B6A7DD1E3D1186E6BBD94268606FDCEC7F5A33778B710EB79E174295
R5_shell_identity_audit.py
  5FCDB3D796328B549C74D56DC46094BF6C27382E590691CBCF01253B5A717BC1
R5_shell_identity_audit_1000.json
  73DFAF5144E31F849DE02F59F082996DFB457AC3DC4494D0CA62D81750D221D8
```

## Frontier effect

The response neither proves nor falsifies the real image/rank-prefix bridge.
The surviving frontier remains the global image/rank capacity statement,
with the first-two-exit component gate of C43 as the strongest exact finite
form presently surviving.
