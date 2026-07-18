# arXiv submission metadata — W143 note

- **Primary category:** math.CO
- **MSC:** 05C05 (trees), 05C35 (extremal problems), 05C07 (degree sequences)
- **License:** CC BY 4.0 (as with previous submissions)
- **Title (plain text, one line):**
  Largest induced trees, girth, and the second-smallest degree: a proof of Graffiti.pc's Conjecture 143
- **Abstract (plain text, no custom macros):**

For a finite simple graph G, let t(G) denote the largest number of vertices
inducing a tree in G, let g(G) denote the girth of G, and let d'(G) denote the
second-smallest entry of the degree sequence of G, counted with multiplicity.
Conjecture 143 of the conjecture-making program Graffiti.pc (DeLaViña, Written
on the Wall II, 2005) asserts that every finite connected graph G that is not
a tree satisfies t(G) >= (g(G)+1)/d'(G). We prove the conjecture. The main
step is an elementary global argument showing that a connected graph
containing a cycle and at least two vertices of degree one has an induced tree
on at least g(G)+1 vertices. The bound is sharp for every girth. The proof has
been formalized and machine-checked in Lean 4 against the statement of the
conjecture in the Google DeepMind Formal Conjectures repository. An independent
machine-assisted resolution was announced one day earlier; we make no claim of priority.

- **Ancillary files (anc/):** the three Lean files from the proof branch
  (GraphConjecture143.lean, LargestInducedTree.lean, Degrees.lean), a README
  with the toolchain pin and axiom audit, and two separately written Graph Atlas
  checkers with their complete JSON outputs. The Apache-2.0 license text
  governing the redistributed Lean files is included.
- **Comments field:** "6 pages. Lean 4 formalization and reproducible Graph
  Atlas checks included as ancillary files; see also
  google-deepmind/formal-conjectures."

- **Before submission:** the named author must personally confirm the author
  name and email in the TeX source, review every claim and ancillary file,
  retain the generative-AI disclosure, and verify the priority note for PR
  #4442 against its status on the submission date.
