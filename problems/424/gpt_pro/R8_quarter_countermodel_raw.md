# R8 response: exact negative result for a definition-level quarter proof

GPT-Pro did not prove or disprove the displayed inequality for the actual
least closure `G=<2,3>`. It supplied the following exact countermodel to any
proof based only on closure, `U`-forward invariance, the hard/splitless
taxonomy, and quarter-scale factor descent.

## Countermodel

Let `G'` be the least set containing `2,3,66` and closed under `xy-1` for
distinct values. Define `A'_H,D'` exactly as for `G`. Then

`A'_H(186)=6`, `D'(186)=4`, and `A'_H(46)=0`.

Consequently

`6 > 4+0+1`,

so the quarter inequality fails for `G'`.

The exact prefix is

```text
T = {2,3,5,9,14,17,26,27,33,41,44,50,51,53,65,66,69,77,
     80,81,84,87,98,99,101,105,122,125,129,131,134,137,149,
     152,153,158,159,161,164,167,173}.
```

Every product `xy-1<=186` with `x<y` in this set has `x` among `2,3,5,9`:

```text
x=2: y=3,5,9,14,17,26,27,33,41,44,50,51,53,65,66,69,77,
         80,81,84,87
x=3: y=5,9,14,17,26,27,33,41,44,50,51,53
x=5: y=9,14,17,26,27,33
x=9: y=14,17
```

Their outputs, together with the three seeds, are exactly `T`; once `x>=14`
the next distinct value is at least `17` and `14*17-1>186`. Thus induction
on the output proves `G' intersect [2,186]=T` exactly.

## Six hard roots

The relevant reducible even roots through `186` are

```text
r    r+1   allowed factorizations
54    55   5*11
74    75   5*15
84    85   5*17
114  115   5*23
144  145   5*29
164  165   5*33, 11*15
174  175   5*35
186  187   11*17
```

The roots `84` and `164` belong to `T`; the other six do not. Their chain
values through the cutoff are

`54,107; 74,147; 114; 144; 174; 186`,

none of which lies in `T`. Hence `A'_H(186)=6`. There is no hard root below
`54`, so `A'_H(floor(186/4))=A'_H(46)=0`.

## Four structural deaths

The even `U`-roots of all values in `T` are

```text
{2,6,14,18,20,26,32,38,44,50,66,80,84,98,122,134,152,158,164}.
```

The roots outside `T` are `6,18,20,32,38`. Exactly four are structural
splitless:

```text
6+1=7, 18+1=19, 20+1=3*7, 38+1=3*13.
```

The remaining root `32` is reducible because `33=3*11`. The four structural
roots enter `G'` by

```text
U^3(6)=41, U^2(18)=69, U^2(20)=77, U^2(38)=149.
```

The root list is exhaustive, so `D'(186)=4`.

## Why the true closure is tight

For the actual `G=<2,3>`, the prefix is `T` with `66` removed. No other
element disappears: the only new output below `187` using `66` is `131`,
and independently `131=3*44-1`, `44=5*9-1`.

Now `66` is a structural splitless hole because `67` is prime, while
`U(66)=131 in G`. Thus it supplies exactly the fifth structural death:

`D_G(186)={6,18,20,38,66}`,

and the observed equality is `6=5+0+1`. Declaring `66` an initial seed
deletes exactly this history-dependent event while retaining the six hard
roots.

Therefore the `+1` cannot be justified from closure, residues, taxonomy,
and quarter-scale factor descent alone. It is sensitive to the number and
history of initially occupied `U`-chains.

## Strongest local lemma

If hard `r` has an allowed factorization `r+1=ab`, `2<=a<b`, then

`5<=a<b<=floor(r/4)`.

Indeed `r+1` is odd. The factor `a` cannot equal `3`, because then `b` is an
allowed distinct cofactor and gives a usable seed-3 reduction. Thus `a>=5`
and `b=(r+1)/a<=r/4` for every hard `r>=54`.

This does not yield a factor-ancestral injection. In the actual closure,

`74+1=5*15`, with `15=U(8)`, and
`144+1=5*29`, with `29=U^2(8)`.

Both factorizations are unique. The factor `5=U^2(2)` lies on the initial
seed chain, while the splitless chain rooted at `8` has no generated value
through `186`: `8,15,29,57,113` are all absent. Thus both hard roots expose
the same only locally available source chain, and factor-ancestral Hall
already fails.

## Exact remaining gap

The original inequality for `G` remains neither proved nor refuted. A proof
must use global derivation-history amortization, may charge hard roots to
unrelated splitless-entry events, and must prove that each derived chain such
as the root-`66` chain can be used with total multiplicity at most one.
