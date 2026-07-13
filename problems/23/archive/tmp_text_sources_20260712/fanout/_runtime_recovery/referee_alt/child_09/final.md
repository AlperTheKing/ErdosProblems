## Conditional component-contraction theorem

Let the row-choice atoms split as \(F=F_C\sqcup F_E\), with legal-choice spaces \(\Omega,\Omega_C,\Omega_E\). Assume:

1. **Legal lift/descend:** Restriction
   \[
   \mathrm{res}:\Omega\to\Omega_C\times\Omega_E
   \]
   is bijective, with inverse `glue`. For canonical rows, this must preserve endpoints, simplicity, four-blue-edge length, shortestness, and row-database membership.

2. **Stable scope:** Changing rows in one factor cannot merge, split, activate, or deactivate components in the other. Selected support, internal-blue components, and active vertices split componentwise.

3. **Score separability:**
   \[
   \operatorname{score}(\operatorname{glue}(x,e))=s_C(x)+s_E(e).
   \]
   Thus collision multiplicities, diagonal terms, HitNeed, reservations, and owners have no cross-component contribution.

4. **Hall separability:** The scoped demand-slot graph is
   \[
   H(\operatorname{glue}(x,e))=H_C(x)\sqcup H_E(e).
   \]
   In particular, a Hall shore inside \(C\) acquires no exterior neighbours.

**Theorem.** If
\[
\omega_*=\operatorname{glue}(x_*,e_*)
\]
is a global score minimizer, then \(x_*\) globally minimizes \(s_C\). After contracting the exterior to its fixed state \(e_*\), define
\[
\overline s(x)=s_C(x)+s_E(e_*).
\]
Then \(x_*\) minimizes \(\overline s\), and every Hall witness contained in \(C\) descends with exactly the same demand, reach, and deficiency.

For every contracted competitor \(x\),
\[
\operatorname{score}(\operatorname{glue}(x,e_*))
-\operatorname{score}(\omega_*)
=s_C(x)-s_C(x_*).
\]

**Proof.** If \(s_C(x)<s_C(x_*)\), legal lifting produces \(\operatorname{glue}(x,e_*)\). Score separability makes it cheaper than \(\omega_*\), contradicting global minimality. Hall preservation follows from disjoint-union incidence. No Hamming-one or local-descent assumption is used.

A weaker sufficient version only requires lifts with exterior state \(e_*\), the displayed score identity, and preservation of the particular failing Hall shore.

## Exact fixture

The exact `Fraction` computation used two independent components:

- \(A\): states `a0,a1`, scores \(2,3\).
- At `a0`, demands \(\{d1,d2\}\) both reach only \(\{s1\}\), giving Hall gap \(2-1=1\).
- \(B\): states `b0,b1`, scores \(5,7\).

The four global scores were exactly:

```text
(a0,b0) = 7
(a0,b1) = 9
(a1,b0) = 8
(a1,b1) = 10
```

Thus `(a0,b0)` is the unique global minimizer. Contracting \(B\) at `b0` gives scores \(7,8\), with the same gap-one Hall witness.

Reproduction command:

```powershell
@'
from fractions import Fraction as F
from itertools import product
A={'a0':(F(2),{'d1':{'s1'},'d2':{'s1'}}),
   'a1':(F(3),{'d1':{'s1'},'d2':{'s2'}})}
B={'b0':F(5),'b1':F(7)}
scores={(a,b):A[a][0]+B[b] for a,b in product(A,B)}
assert scores=={('a0','b0'):F(7),('a0','b1'):F(9),
                ('a1','b0'):F(8),('a1','b1'):F(10)}
assert len({'s1'}) < 2
assert {a:A[a][0]+B['b0'] for a in A} == {'a0':F(7),'a1':F(8)}
print(scores)
'@ | python -
```

## Isolated proof gap

This theorem does **not yet apply** to R29.

The 2,943-vertex construction makes the missing hypothesis explicit: simultaneous selector trades may split the 2,775-vertex active component and deactivate its hubs. Hence:

- legal row choices are not known to factor with the exterior fixed;
- component activity is not stable under joint trades;
- scoped score can change nonlocally through activation and diagonal collisions;
- outside-component attachment transfers can create cross-component Hall neighbours.

The required new result is a **sealed-component lemma**: every legal joint trade must admit a componentwise replacement with the same exterior boundary signature, and that signature must determine activity, Hall incidence, and every score cross-term.

R25–R29 do not prove this lemma. Direct vertex contraction is also illegal: it may shorten a length-4 row, identify row vertices, create a diagonal collision, or change shortest-path membership.

## Source hashes

```text
AGENTS.md
102B44A4744C638BA84381D8CFB70F412916D6C0B892253678453E86007A6D7E

coordination/CODEX_ONBOARDING.md
E3012793ACCDE4E8F8FA3ED3E514A794A7D006A07E4BDC23E4239D14C9D61AD0

coordination/CLAUDE_TO_CODEX.md
B533191BAF54A2E3D53CE05E1F46269B78E6EEDBA90F08CB9B80B7FEAB6E9126

WALL_ATTACK_R25_GPTPRO56.md
50DEB44485A439DC5810AC22FEF972C792CEAC46674A13C3B62789C76F88DC23

WALL_ATTACK_R26_GPTPRO56.md
80069DDFA9EC0F87098772F914E8B043F431D1AA5E3E7E6B43E51DD96E7AB05E

WALL_ATTACK_R27_GPTPRO56.md
45986DFD341AB818D41122957C6B6BBD050907C4E585FF6C9E58CF8C7B010991

WALL_ATTACK_R28_GPTPRO56.md
819D6A3BB2DA534BEB7AC86F8B50E9AB936942893671BCA12C61E027069E42B9

WALL_ATTACK_R29_GPTPRO56.md
FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04
```

Artifact creation under the recovery directory failed through the mandated patch mechanism, so no file artifact or artifact hash is claimed.