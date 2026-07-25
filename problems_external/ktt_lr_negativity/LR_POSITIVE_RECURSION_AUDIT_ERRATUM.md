# Erratum for `LR_POSITIVE_RECURSION_AUDIT.md`

The cumulative branching identity in Section 5 is to be read, for each fixed
`gamma`, as

```text
sum_{nu: gamma interlaces nu} c^nu_{lambda,mu}
 = sum_{alpha interlaces lambda, beta interlaces mu} c^gamma_{alpha,beta}.
```

This is the coefficient identity obtained by restricting
`V_lambda tensor V_mu` from `GL_r` to `GL_{r-1}`.  The surrounding conclusion
is unchanged: recovering an individual `c^nu_{lambda,mu}` requires triangular
inversion, and the interlacing index sets depend on the stretch parameter.
