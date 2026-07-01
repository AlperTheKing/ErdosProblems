# Root-Tail Harvest Switch Lemma Status

The proposed root-tail harvest switch lemma cannot be true as stated.

The lemma implies the harvest inequality

```text
25*rho_o >= 4*(cU_o - a_o)
```

for every minority overloaded vertex.  Equivalently, with the proposed tail
functional,

```text
F_o(0) = 25*rho_o - 4*(cU_o - a_o)
```

would have to be nonnegative on every gamma-minimal connected maximum cut.

This is false on the C5 blow-up guardrail with class sizes

```text
[6,5,6,5,6]
```

and the standard gamma-minimal maximum cut leaving the minimum adjacent product
between classes `0` and `1` bad.

For an overloaded minority vertex `o` in the adjacent size-5 class, the exact
rational evaluation gives:

```text
N = 28
a_o = 2
A = 20
rho_o = 1.9890721568352303...
cU_o = 16.582814271682803...
e_o = cU_o - a_o = 14.582814271682803...
F_o(0) = 25*rho_o - 4*e_o = -8.604453165850455...
```

Thus the lemma's antecedent fires.  If the lemma were true, it would produce a
neutral connected terminal-shadow switch with negative square-length
replacement cost, hence a Gamma-decreasing connected maximum cut.  That
contradicts the gamma-minimality of the standard C5 blow-up cut.

The same family also rules out every fixed positive-coefficient strengthening
of bare Schur absorption; see `SCHUR_C5_BLOWUP_QUOTIENT_GUARDRAIL.md`.

Conclusion: the root-tail harvest switch lemma is a certificate for a false
harvest inequality.  The surviving Schur route must avoid HARVEST and target a
coefficient-free statement such as bare non-majority absorption or full
effective-shunt/PSD domination.
