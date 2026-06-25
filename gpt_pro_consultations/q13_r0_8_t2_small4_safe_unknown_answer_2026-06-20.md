Verdict

Under the definitions and numerical data as written, all four rows are outside the n=30 search space. No additional structural cut or CP-SAT run is needed.

1. Vertex-count contradiction

For nonadjacent roots x,y, the standard rooted sets form the disjoint partition

V(G)={x,y}
∪
˙
C
∪
˙
A
∪
˙
B
∪
˙
R.

Therefore

n=2+∣C∣+∣A∣+∣B∣+∣R∣.

Your parameters give

2+3+6+7+13=31,

not 30.

Hence:

q=13, k=3, ∣A∣=6, ∣B∣=7
	​


cannot occur in a 30-vertex graph.

This argument does not use terminal closure, H14, codegrees, rooted cuts, or any computational assumption.

For n=30,q=13,k=3, the necessary identity is

∣A∣+∣B∣=30−2−3−13=12.

Thus the only possibilities compatible with root minimum degree 8, which gives ∣A∣,∣B∣≥5, are

(5,7),(6,6),(7,5).

Up to swapping the roots, only (5,7) and (6,6) need consideration. The pair (6,7) is impossible.

2. The stated edge cap also independently rejects every row

For both profiles,

U=
r∈R
∑
	​

∣L(r)∣=26.

Indeed, for profile 4971,

2⋅1+2⋅2+2⋅1+3⋅2+4⋅3=26,

and for profile 5164,

2⋅1+3⋅2+2⋅1+2⋅2+4⋅3=26.

Your stated cap is

ROOT_EDGES+U+p+e
R
	​

+M≤111.

But even omitting the nonnegative root-edge contribution, the smallest listed row has

U+p+e
R
	​

+M≥26+25+12+54=117>111.

Therefore, if that inequality and RHS 111 are literal,

all four rows are immediately infeasible.
	​


Since the solver instead ran for 300 seconds and returned UNKNOWN, the implementation plainly does not enforce the cap exactly as stated here. Either:

111 is a residual cap from which some terms have already been removed;

the actual RHS is a different constant;

or the displayed formula is not the implemented formula.

That mismatch should be resolved before using any solver result from these rows.

3. The listed M-ranges expose the likely off-by-one

The number of edges incident with the two nonadjacent roots is

ROOT_EDGES=2∣C∣+∣A∣+∣B∣.

The invalid (6,7) parameters give

2⋅3+6+7=19.

A valid q=13,k=3,n=30 decomposition must instead have ∣A∣+∣B∣=12, hence

ROOT_EDGES=2⋅3+12=18.

Under the usual total edge cap 139, profile U=26 and e
R
	​

=12 would give:

M≤139−18−26−25−12=58

for p=25, and

M≤139−18−26−26−12=57

for p=26.

Your generated upper bounds are instead 57 and 56, exactly one lower. Those are the bounds obtained by charging 19 root edges:

139−19−26−25−12=57,
139−19−26−26−12=56.

So the row ranges are consistent with the generator treating all 6+7 side vertices as genuine vertices, thereby generating a 31-vertex rooted decomposition.

4. Why B=7 cannot harmlessly include a root or dummy

A possible explanation is that the code’s “seven B vertices” include a distinguished root or placeholder. That convention is not compatible with the stated exact-state model unless the extra object is excluded from every ordinary B calculation.

In particular, it must not contribute to:

I
∑
	​

B
I
	​

,M,p=
I∩J=∅
∑
	​

A
I
	​

B
J
	​

,

or B/R, B/B, state-separator, rectangle, and rooted-cut terms.

Treating the B-root as an ordinary empty-state B vertex would be especially wrong: the exact A/B law would declare it adjacent to every A-state, because the empty state is disjoint from every state, whereas the opposite root is nonadjacent to all vertices of A.

Thus there are only two coherent possibilities:

nb=7 means seven ordinary B vertices, in which case the model has 31 vertices.

One object is special, in which case the ordinary B-state count must be 6, and all formulas must exclude the special object.

5. Exact generator checks to add

This should be rejected before constructing CP-SAT variables:

Python
Run
def validate_rooted_row(
    *,
    n: int,
    q: int,
    k: int,
    na: int,
    nb: int,
    cnt: tuple[int, ...],
    p: int,
    e_r: int,
    m_min: int,
    total_edge_cap: int | None = None,
) -> None:
    assert len(cnt) == 8
    assert sum(cnt) == q, (
        f"Label counts sum to {sum(cnt)}, expected q={q}"
    )

    vertex_total = 2 + k + na + nb + q
    assert vertex_total == n, (
        f"Invalid rooted partition: "
        f"2 + k + na + nb + q = {vertex_total}, expected n={n}"
    )

    u = sum(mask.bit_count() * cnt[mask] for mask in range(8))
    root_edges = 2 * k + na + nb

    # Equivalent invariant derived from the vertex partition.
    assert root_edges == n - 2 + k - q

    if total_edge_cap is not None:
        minimum_edges = root_edges + u + p + e_r + m_min
        assert minimum_edges <= total_edge_cap, (
            f"Row already violates edge cap: "
            f"{root_edges}+{u}+{p}+{e_r}+{m_min}"
            f"={minimum_edges}>{total_edge_cap}"
        )

For the current invocation,

n=30, q=13, k=3, na=6, nb=7

the second assertion returns

2 + 3 + 6 + 7 + 13 = 31, expected 30

and constitutes a complete finite certificate closing the four jobs.

Also avoid one ambiguous EDGE_CAP constant. Keep two separately named quantities:

TOTAL_EDGE_CAP
RESIDUAL_M_CAP

and derive the latter in exactly one place:

Python
Run
m_max = (
    TOTAL_EDGE_CAP
    - (2 * k + na + nb)
    - u
    - p
    - e_r
)
6. Correct next search space

The files produced with

--q 13 --k 3 --na 6 --nb 7

should not be used in the n=30 proof certificate.

For these 13-vertex label profiles, the valid reruns are based on:

--na 6 --nb 6

and, if not already handled elsewhere,

--na 5 --nb 7

with the root-swapped (7,5) case identified by symmetry.

There is also a profile symmetry:

4971=(c
2
	​

,c
3
	​

,c
4
	​

,c
5
	​

,c
7
	​

)=(2,2,2,3,4)

is mapped to

5164=(2,3,2,2,4)

by exchanging colours 2↔3, which swaps

S2↔S3,D12↔D13.

Thus in the symmetric (6,6) branch, only one of these two profile families should need independent certification, provided the symmetry canonicalizer also transports the fixed R-mask and all colour-indexed constraints.

Weakest steps

The vertex-count rejection assumes A,B,C,R have their standard rooted meanings exactly as stated. If nb=7 is a private coding convention rather than the cardinality of the ordinary B-side, that convention must be specified and audited separately.

The cap-111 contradiction uses the cap formula literally as written. The solver behavior strongly indicates that the actual code uses a different interpretation.

The corrected M-upper bounds 58 and 57 use the usual total edge cap 139. The partition contradiction itself is independent of any edge-cap value.

Colour symmetry reduces duplicated work only if no external symmetry-breaking constraint distinguishes colours 2 and 3.