# P37b: translate blocks and the continuum endpoint-shadow obstruction

## Verdict

This note proves an exact finite translate-block lemma and an exact rational
continuum obstruction. The lemma retains equal-three-sum partitions; the
continuum profile shows that the P13 occupation law together with all P24
endpoint-shadow inequalities still permits every span coefficient
(2+g<3), (0<g<1). Hence those inequalities alone cannot prove the
coefficient (3) required in the fully reflected lane.

## 1. Exact translate-block lemma

Let (E={e_1<cdots<e_q=M}) be a positive integer Sidon set, with
diagonal pair sums included, and suppose (Ecap3E=arnothing), where
repeated triple summands are allowed. Put

[
 S={a+b:a,bin E, ale b},qquad
 T={a+b+c:a,b,cin E, a+b+cle M}.
]

For each (sin S), define the low translate block

[
 C_s={e+s:ein E, e+sle M}subseteq T.
]

Then:

1. any two distinct blocks (C_s,C_{s'}) meet in at most one point;
2. if (r(t)=|{sin S:tin C_s}|), then the supports of distinct
   unordered triple representations of a fixed (tin T) are disjoint;
3. consequently
   [
   sum_{sin S}|C_s|
   =sum_{ein E}|{sin S:sle M-e}|
   =sum_{tin T}r(t),
   qquad r(t)le q-1.
   ]

### Proof

If two distinct blocks had two common points, then

[
 e+s=f+s',qquad e'+s=f'+s'
]

with two distinct endpoint pairs. Subtraction gives
(e-f=e'-f'), hence (e+f'=e'+f). Difference uniqueness for a Sidon
set forces the endpoint pairs to coincide, contradicting that the two
common points were distinct. Thus block intersections have size at most one.

If two triple representations of the same (t) share an element, cancel
that element. The remaining unordered pair sums are equal, so Sidonicity
makes the two remaining pairs identical. Hence the triple representations
were identical. Distinct representations therefore have disjoint supports.

A representation with three distinct entries contributes three blocks at
(t), one with each entry singled out; a representation with repeated
entries contributes the number of distinct entries in its support. Hence
(r(t)) is the sum of the support sizes of the distinct triple
representations of (t). These supports are disjoint, so (r(t)le q).
Equality would use every element of (E), including (M), in a positive
triple summing to (tle M), which is impossible. Therefore (r(t)le q-1).
The displayed incidence identity is double counting.

The bound is sharp for (E={1,7,19,23}): (r(21)=3=q-1).

## 2. Continuum profile

Fix a rational (g) with (0<g<1), and put (u=1-g). Consider the
normalized one-point density on

[
 [g/2,1+g/2].
]

Its positive-difference density and shifted pair-sum density are

[
 d(t)=(1-t)_+,mathbf 1_{0le tle1},
]

[
 s_g(t)=
 egin{cases}
 (t-g)/2,&gle tle g+1,\
 (g+2-t)/2,&g+1le tle g+2,\
 0,&	ext{otherwise}.
 end{cases}
]

A direct interval check gives

[
 0le d(t)+s_g(t)le1
]

for every real (t). Thus the complete P13 coupled occupation law holds
at span coefficient (2+g<3).

The normalized low triple shadow is the interval

[
 [3g/2,1+g/2],
]

of length (u). For normalized endpoints (0le x<yle1), let
(delta=y-x). The continuum versions of the P24 source, shadow
autocorrelation, and hole capacity are

[
 eta_g(x,y)=rac{(u-y)_+^2}{4},qquad
 	au_g(delta)=(u-delta)_+,qquad
 h_g(delta)=1+rac g2-delta.
]

They satisfy

[
 eta_g(x,y)le	au_g(delta)le h_g(delta)
]

for every (x<y). Indeed, if (yge u), the first term is zero. If
(y<u), then (0<u-yle1) and
((u-y)^2/4le u-yle u-y+x=u-delta).
The second inequality follows from (u=1-gle1+g/2).

The global normalized capacities are

[
 	ext{source edges}=rac{u^4}{48},qquad
 	ext{translate incidences}=rac{u^3}{12},
]

[
 	ext{represented shadow edges}=rac{u^2}{2}-rac{u^3}{6},
 qquad
 	ext{all shadow edges}=rac{u^2}{2},
]

[
 	ext{represented hole edges}=rac13+rac g4,
]

and satisfy the same ordering as the finite P24 inequalities.

This is a continuum feasibility obstruction, not an integer
counterconstruction. It proves that a completion needs a unit-lattice
phase/carry theorem or a new restriction on equal-three-sum partitions.

## 3. Exact verification

The verifier

    problems/864/compute/p37/audit_reflected_3e.py

uses integers and Fractions only. It checks:

- 2,861 exhaustive signed rulers and 2,746 low-shadow targets;
- 123,840 rational endpoint inequalities;
- the independent P24 audit of 93,494 interval slices;
- the sharp finite example above;
- valid finite records through q=14, without optimality claims.

The certificate is

    problems/864/compute/p37/audit_results.json