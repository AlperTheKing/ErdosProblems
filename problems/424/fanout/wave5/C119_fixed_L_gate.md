# C119: fixed-L Gate T via atomic coprime swaps

## Direct route

1. **Exact final deliverable.** For the `(3,2,1)` ray (`Q=360`), prove
   explicit integers `L,K0` and rational `eta>0` such that
   `M_K(L) <= (1-eta)N_K` for every `K>=K0`, or construct a rigorous
   infinite counterfamily. A permitted route exit is one exact finite
   counterexample that falsifies a concrete load-bearing lemma below.
2. **Current frontier.** For two distinct representations `(i,u,v)` and
   `(j,u',v')` of one product, put `g=gcd(u,u')`, `a=u/g`, and `b=u'/g`.
   Call the pair *atomic* when each of `a,b` has at most one distinct prime
   divisor. Test the two-part atomic-ownership claim:

   - (AO1) every collision pair is atomic;
   - (AO2) every labelled edge has at most two atomic collision partners.
3. **Logical bridge.** By C106, collision partners are exactly coprime
   swaps. Under (AO1), all `r_K(uv)-1` partners of an edge are atomic; (AO2)
   then gives `r_K(uv)<=3` for every edge. Hence Gate T holds with the
   explicit values `L=3`, `eta=1`, and `K0=2`.
4. **Next falsifiable action.** Independently enumerate the exact
   `(3,2,1)` blocks for `K=2,3,4`; verify every fibre and compute the atomic
   degree of every edge before attempting either lemma.
5. **Exit condition.** Prove (AO1)-(AO2), produce an infinite Gate-T
   falsifier, or stop this route at the first replayable collision pair
   falsifying (AO1) or edge falsifying (AO2). Do not replace it by a growing
   multiplicity cutoff.

## Prerequisite audit

- C102's density bridge is valid: Gate A together with fixed-cutoff Gate T
  produces a positive lower-density subset, and the final inputs are
  separated modulo three.
- C106's normal form `(u,u',v,v')=(ga,gb,bc,ac)` is bijective and its swap
  degree is exactly `r_K(uv)-1`.
- R9's divisor injection and exponential dispersion do not control a fixed
  cutoff.
- C111's divisor-moment inequality and its audited optimization remove edge
  mass only above
  `exp((((log 2)(log 6))+epsilon)K/log K)`. They leave exactly the regime
  targeted here.

## Verdict

The fixed-`L` Gate T is neither proved nor refuted. The concrete atomic
prime-ownership route above is exactly false already at `K=3`.

There is a product with exactly two labelled representations for which both
coprime swap quotients contain two distinct primes:

\[
 \boxed{
  2131353\cdot8825
  =2144475\cdot8771
  =18809190225.}
                                                               \tag{1}
\]

Indeed,

\[
\begin{aligned}
 2131353&=243\cdot8771,&8771&=7^2\cdot179,\\
 2144475&=243\cdot8825,&8825&=5^2\cdot353.
\end{aligned}                                                 \tag{2}
\]

Thus the C106 normal form for the pair is

\[
 (g,a,b,c)=(243,8771,8825,1).                                \tag{3}
\]

Both `omega(a)` and `omega(b)` equal two, so the pair is not atomic. Since
the full fibre has multiplicity two, there is no third representation through
which (1) could be decomposed into atomic swaps. This falsifies (AO1) and
kills the stated route before any asymptotic or growing-cutoff estimate.

## Standalone membership certificate

Both representations in (1) use channel `i=2` of `I_3={1,2}`. Starting at
offset zero and applying `d -> m*d+(m-2)`, the following words (in application
order) give the four offsets:

| factor | layer | word | offset |
|---|---:|---|---:|
| `2131353` | 2 | `2,3,2,5,3,2,2,3,2,3,5,2` | `28876` |
| `8825` | 1 | `2,2,5,3,2,3` | `61` |
| `2144475` | 2 | `2,3,5,2,3,2,3,2,5,2,2,3` | `35437` |
| `8771` | 1 | `2,2,3,3,2,5` | `43` |

Each layer-two word has six `2`s, four `3`s, and two `5`s; each layer-one
word has three `2`s, two `3`s, and one `5`. Hence the offsets belong to
`D_2,D_1` respectively. With `Q=360`, all four corresponding values

\[
 h=8Q^k+d+1
\]

are `2 (mod 3)`, the selected residue in both layers. Therefore the left
values are `u=2h-1` and the right values are `v=3h-1`, giving exactly the
four factors in (1). They are valid labelled edges in `U_2 x V_1`.

The independent replay checks every possible left divisor from both channels
`i=1,2` and finds exactly the two displayed representations of the product.
Thus the assertion that the fibre has multiplicity two is part of the finite
certificate, not an inference from the factorization alone.

## Exact bounded-degree test

The complete `K<=4` results are:

| `K` | edges | support | collision pairs | atomic | non-atomic | bilateral non-atomic | max atomic degree |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1,296 | 1,296 | 0 | 0 | 0 | 0 | 0 |
| 3 | 560,088 | 559,577 | 511 | 288 | 223 | 57 | 1 |
| 4 | 60,512,841 | 60,496,906 | 15,939 | 1,831 | 14,108 | 6,535 | 1 |

For `K=4`, the full multiplicity histogram is
`1:60480975, 2:15927, 3:4`, independently reproducing C111. The bounded
atomic-degree claim (AO2) passes these layers with the stronger observed
bound one, but this cannot rescue the route because most collision pairs at
`K=3,4` are not atomic. No extrapolation from that finite degree is made.

## Verification

`C119_atomic_swap_audit.cpp` rebuilds `D_1,D_2` from the exact union
recursion, forms and sorts all `61,074,225` labelled edges for `K=2,3,4`,
replays every repeated product, factors every reduced swap pair, and emits
the first one-sided and bilateral failures of (AO1). Two 32-worker runs are
byte-identical.

`C119_atomic_swap_verify.py` uses ordinary Python sets and integers. It
independently reconstructs the full `K=2,3` product histograms, searches all
channels for every representation of (1), verifies (2)-(3), and finds the
four displayed words. Normal and `python -O` outputs are byte-identical.

SHA-256:

```text
168670B54A3B656848BD6177C19EA77B7FBAEC0E10ACD79A331FF9957B43D6C2  C119_atomic_swap_audit.cpp
40D4893C6A79CC3BBB267360693A30F86D9AA9C1424D2A10240E879BFEA6D534  C119_atomic_swap_audit.json
FD5AE9F0FCC627B315184847E954613EE1E59EE55F946C38A7B13AD688629831  C119_atomic_swap_verify.py
39D89D4BB525DD035053A53ADAA7B5BE45BD3393D485E9669E09AB7F0EEAFAD8  C119_atomic_swap_verify.json
```

Reproduction:

```powershell
g++ -std=c++20 -O3 -march=native -fopenmp -Wall -Wextra -Wconversion -Wshadow `
  problems/424/compute/wave5/C119_atomic_swap_audit.cpp `
  -o problems/424/compute/wave5/C119_atomic_swap_audit.exe

problems/424/compute/wave5/C119_atomic_swap_audit.exe `
  problems/424/compute/wave5/C119_atomic_swap_audit.json 32

python problems/424/compute/wave5/C119_atomic_swap_verify.py `
  --audit problems/424/compute/wave5/C119_atomic_swap_audit.json `
  --output problems/424/compute/wave5/C119_atomic_swap_verify.json
```

## Boundary

The counterexample refutes the load-bearing atomic reduction, not Gate T.
It supplies neither a fixed `L` nor an infinite high-multiplicity family.
Per the exit condition, the prime-ownership branch stops here; replacing
atomic swaps by successively larger composite swap classes would create an
unbounded hierarchy with no bridge to a fixed cutoff.
