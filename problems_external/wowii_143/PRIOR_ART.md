# Prior-art audit — WOWII / Graffiti.pc Conjecture 143

**Access date:** 2026-07-17  
**Decision:** **PASS — no prior proof located; this is not proof of absence.**  
**Confidence:** **moderate (0.75) for global priority**, and **high (0.90) that the audited current registers still treat the exact statement as open**.

The lower confidence on global priority is deliberate.  The proof under audit is
short, a very close induced-forest theorem appeared in 2004, and an unpublished
or unindexed observation could exist.  Any public claim should therefore say
“a proof of Conjecture 143, which is still listed as open in the sources below”,
not “the first proof”, until the originators have confirmed priority.

## Target checked

For a finite connected non-tree graph $G$, let $t(G)$ be the maximum order of
an induced tree, $g(G)$ its girth, and $\delta'(G)$ the second-smallest degree,
with multiplicity.  The target is

$$
t(G)\,\delta'(G)\ge g(G)+1,
$$

equivalently $t(G)\ge (g(G)+1)/\delta'(G)$.

## Current official and curated records

### Douglas B. West's Graffiti.pc register

- Page: <https://dwest.web.illinois.edu/regs/graffiti.html>
- The page was retrieved directly on 2026-07-17 (HTTP 200), and a search-index
  copy had been crawled during the preceding week.
- It defines $t(G)$ as the number of vertices in a largest induced tree and
  $\delta'(G)$ as the next-to-last entry in the degree list, equal to the
  minimum degree when more than one vertex has minimum degree.
- It gives the exact record:

  > Conjecture 143: (2005) If G is connected and not a tree, then
  > t(G) >= (g(G)+1)/delta'(G).

- No proof or resolution is attached to Conjecture 143 on that page.  Continued
  inclusion is evidence of current unresolved status, not a guarantee of it.

### DeLaViña's Written on the Wall II resolved list

- Page: <https://cms.dt.uh.edu/faculty/delavinae/research/wowII/resolvedT.htm>
- The live host timed out on 2026-07-17.  The search-index snapshot, crawled
  four months earlier, was therefore checked.  Searches within that indexed
  page for `143`, `maximum order of an induced tree`, and `girth(G)+1` returned
  no Conjecture 143 resolution.  Nearby tree-number records, including 140 and
  147, are present.
- The same resolved list does contain the closely related Conjecture 48:

  $$
  f(G)\ge g(G)+f_G(1)-1,
  $$

  where $f(G)$ is maximum induced-forest order and $f_G(1)$ is the number of
  degree-one vertices.  It attributes this to DeLaViña and Waller (2004).
- Thus the curated list distinguishes the resolved **forest** statement from
  the later **tree** Conjecture 143.  Omission is negative evidence only,
  especially because the live host was unavailable.

### Google DeepMind Formal Conjectures

- Current source:
  <https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean>
- Raw source:
  <https://raw.githubusercontent.com/google-deepmind/formal-conjectures/main/FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean>
- The current file retrieved on 2026-07-17 labels `conjecture143` as
  `@[category research open, AMS 5]` and leaves its proof as `by sorry`.  Its
  inequality is the denominator-free real-valued form

  ```text
  (G.girth : Real) + 1 <=
    largestInducedTreeSize G * secondSmallestDegree G.
  ```

- Most recent commit touching the file:
  [`c252a41054125b5fd9c8356e2137cd9b55337657`](https://github.com/google-deepmind/formal-conjectures/commit/c252a41054125b5fd9c8356e2137cd9b55337657),
  2026-07-16T23:28:26Z, “refactor: split out FormalConjectures.Util to a new
  library (#4433)”.  The open annotation remains in the resulting current file.
- File-introduction commit:
  [`c270a99760869e9736d01be7871d7b8fd248e887`](https://github.com/google-deepmind/formal-conjectures/commit/c270a99760869e9736d01be7871d7b8fd248e887),
  2026-06-08T13:14:19Z, “Add 22 WOWII numbered conjectures (batches 3-9,
  part 1/2) (#3820)”.
- Commit-history endpoint checked:
  <https://api.github.com/repos/google-deepmind/formal-conjectures/commits?path=FormalConjectures%2FWrittenOnTheWallII%2FGraphConjecture143.lean>

The repository's status is strong recent evidence, but it is not an authority
for mathematical priority and can lag the literature.

## Foundational induced-tree paper

P. Erdős, M. Saks, and V. T. Sós, “Maximum Induced Trees in Graphs”,
*Journal of Combinatorial Theory, Series B* 41(1) (1986), 61–79.

- DOI: <https://doi.org/10.1016/0095-8956(86)90028-6>
- Author-hosted full text:
  <https://users.renyi.hu/~sos/1986_Maximum_Induced_Trees_in_Graphs.pdf>

All 19 pages were searched and the relevant results were read.  The paper has
no occurrence of “girth” or “minimum degree”.  Its abstract and main-results
summary concern order and size, radius, independence number, clique number,
and connectivity.  In particular it proves induced-path bounds in terms of
diameter and radius and gives bounds for $t(G)$ in terms of order and cyclomatic
number.  Its final open problems concern $c(n,k)$ and $f(n,p)$, not Conjecture
143 or the two-leaf/girth lemma used here.

**Finding:** the 1986 paper supplies the invariant and background, but no
statement or proof of the target inequality was located, and its listed results
do not subsume the target.

## Closest located antecedent: the induced-forest theorem

E. DeLaViña and B. Waller, “On some conjectures of Graffiti.pc on the maximum
order of induced subgraphs”, *Congressus Numerantium* 166 (2004), 11–32,
proved the bound

$$
f(G)\ge g(G)+f_1(G)-1,
$$

where $f(G)$ is maximum induced-forest order and $f_1(G)$ counts degree-one
vertices.  The exact published attribution and statement are recorded at
pp. 200–201 of:

- A. Hertz, O. Marcotte, and D. Schindl, “On the maximum orders of an induced
  forest, an induced tree, and a stable set”, *Yugoslav Journal of Operations
  Research* 24(2) (2014), 199–215;
- DOI: <https://doi.org/10.2298/YJOR130402037H>;
- institutional full text:
  <https://publications.polymtl.ca/3626/1/2014_Hertz_On_maximum_orders_induced_forest.pdf>.

This is very close but does **not** prove Conjecture 143.  With two leaves it
gives an induced forest on at least $g+1$ vertices; the forest need not be
connected, whereas $t(G)$ requires one induced tree.  Hertz–Marcotte–Schindl,
Theorem 2.3, converts an arbitrary induced forest $F$ only to the bound

$$
t(G)\ge
\left\lceil\frac{|F|-2}{n+1-|F|}\right\rceil+2,
$$

which does not yield $t(G)\ge g+1$ from the 2004 forest inequality.  For
example, the numerical data $g=3$, $f_1=2$, and $n=100$ give only $t\ge3$ via
that conversion, not $t\ge4$.

The full 2004 proceedings article was not found in an openly accessible
primary copy during this audit.  Its bibliographic record and exact theorem
were cross-checked against the official WOWII resolved list and the 2014
peer-reviewed article.  This access limitation is one reason not to make an
unqualified first-proof claim.

## Search log

The following exact or near-exact queries were run in web and scholarly-index
searches.  Results were followed to official pages, primary papers, or
institutional copies where available.

### Exact number and formula

- `"t(G) >= (g(G)+1)/delta'(G)"`
- `"t(G)" "g(G)+1" "delta'(G)" induced tree`
- `"t(G) delta'(G)" "g(G)+1" graph`
- `"Conjecture 143" "maximum induced tree"`
- `"Graffiti.pc" 143 "induced tree"`
- `"Written on the Wall II" 143 tree girth`
- `"Conjecture 143" Graffiti.pc proof`

### Degree terminology

- `"second-smallest degree" "induced tree"`
- `"second smallest degree" induced tree girth`
- `"next-to-last entry" "induced tree" degree list`
- `"next-to-last degree" induced tree`
- `"induced tree" girth "second minimum degree"`

### Two-leaf/girth lemma and synonyms

- `"largest induced tree" girth leaves graph theorem`
- `"maximum induced tree" girth "two leaves"`
- `"two leaves" "largest induced tree" graph`
- `"two pendant vertices" "induced tree" graph girth`
- `"induced tree containing" leaves graph`
- `"induced subtree" girth pendant vertices graph`
- `connected cyclic graph two leaves induced tree girth`

### Foundational and citation-oriented searches

- `"Maximum Induced Trees in Graphs" girth degree leaves`
- `"maximum induced tree" girth minimum degree graph theorem`
- `"largest induced tree" girth graph degree`
- `"On some conjectures of Graffiti.pc on the maximum order of induced subgraphs"`
- `DeLaViña Waller induced forest girth f(G) g(G) f1(G)`
- `"f(G)" "g(G)+f1(G)-1" graph`

The formula searches returned the West register or irrelevant notation.  The
synonym searches returned work on random graphs, restricted graph classes,
terminal-containing induced trees, induced forests, and optimization, but no
proof of the exact inequality or of the two-leaf/girth lemma.  No located
result was silently upgraded from “forest” to “tree”.

## Limitations and final decision

- Negative search results cannot establish absence from all publications,
  theses, proceedings, correspondence, or folklore.
- The live DeLaViña host timed out; its four-month-old indexed snapshot was
  used for the resolved-list check.
- The especially close 2004 forest theorem raises the chance that the tree
  argument was noticed but never indexed or published.
- A direct priority inquiry to Douglas West and Ermelinda DeLaViña remains the
  appropriate final check before journal submission or a “first proof” claim.

**Final novelty-gate decision: PASS — no prior proof located in the sources and
queries above.  This is not proof of absence.**
