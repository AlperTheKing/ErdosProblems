# Erdős 1977 primary-source record for Problem 424

## Primary source

Paul Erdős, "Problems and results on combinatorial number theory III," in
Melvyn B. Nathanson (ed.), *Number Theory Day*, Lecture Notes in Mathematics
626, Springer-Verlag, Berlin, 1977, pp. 43-72. The problem is in section 10,
"Some more unconventional problems," on printed p. 71 (PDF page 29, or index
28). The publisher assigns DOI
[10.1007/BFb0063064](https://doi.org/10.1007/BFb0063064). The primary scan is
in the [Erdős archive](https://www.renyi.hu/~p_erdos/1977-27.pdf).

The scan's essential wording is:

> "Form all products of two distinct elements of the sequence, subtract 1 ...
> Does this sequence have positive density?"

The full sentence on p. 71 starts with \(a_1=2,a_2=3\), directs that all such
outputs be appended, and says to repeat the operation indefinitely.

## Exact membership definition

The source-faithful distinct-value closure is

\[
A_0=\{2,3\},\qquad
A_{r+1}=A_r\cup\{xy-1:x,y\in A_r,\ x\ne y\},\qquad
A=\bigcup_{r\geq 0}A_r.
\]

Thus every application of the rule has \(x\ne y\) as integers. Products
\(x^2-1\) are not licensed by two copies or two positions carrying the same
integer. Order and multiplicity do not affect the membership set under this
condition.

For the sprint's stated density convention, define

\[
\underline d(A)=\liminf_{X\to\infty}
  \frac{|A\cap\{1,\ldots,\lfloor X\rfloor\}|}{\lfloor X\rfloor}.
\]

The sprint question is whether \(\underline d(A)>0\). This liminf convention is
not printed in the 1977 problem: Erdős writes only "positive density" and gives
no definition or qualifier in that sentence. There is relevant internal usage
on the immediately preceding printed page 70. For a different sequence, Erdős
writes "density (lower density)" and then distinguishes uncertainty about the
former from an expectation that the latter is zero. Thus this article does not
automatically use unqualified density as a synonym for lower density. The
sprint's liminf formulation is a specified strengthening or interpretation,
not an exact transcription of the 1977 quantifier.

## Lemma: iteration equals the least distinct-value closure

**Lemma.** The set \(A\) above is the unique smallest subset \(S\subseteq
\mathbb Z_{>0}\) such that \(2,3\in S\) and

\[
x,y\in S,\quad x\ne y\quad\Longrightarrow\quad xy-1\in S.
\]

**Proof.** The union \(A\) contains 2 and 3. If \(x,y\in A\) with \(x\ne y\),
then \(x\in A_r\) and \(y\in A_s\) for some \(r,s\). With
\(t=\max(r,s)\), both lie in \(A_t\), so \(xy-1\in A_{t+1}\subseteq A\).
Hence \(A\) has the required closure.

Conversely, let \(S\) contain 2 and 3 and obey that closure for every pair
\(x\ne y\). Inductively, \(A_0\subseteq S\); and \(A_r\subseteq S\) implies
every generator \(xy-1\) used in \(A_{r+1}\) is in \(S\), since its parents
satisfy \(x\ne y\). Hence \(A_r\subseteq S\) for every \(r\), and therefore
\(A\subseteq S\). This proves minimality and uniqueness. \(\square\)

## Exact semantic counterexample: 24

The source says "two distinct elements," not "two distinct indices." Replacing
distinct values by distinct positions in a duplicate-preserving list changes
the generated membership set:

1. Start with the list \([2,3]\). Its two distinct positions append \(5\).
2. On the next complete pass, the positions carrying 2 and 3 append another
   \(5\), so there are now two distinct positions carrying the equal value 5.
3. Pairing those positions would append \(5\cdot5-1=24\). This step has
   distinct indices but violates the source-faithful condition \(x\ne y\).

In the distinct-value set \(A\), \(24\notin A\). First, \(1\notin A\): if 1
entered at a least stage, its distinct positive parents would satisfy \(xy=2\),
so one parent would already have to be 1, a contradiction. If 24 entered, its
distinct positive parents would satisfy \(xy=25\). The only positive factor
pairs are \(1\cdot25\), \(5\cdot5\), and \(25\cdot1\). The first and third are
impossible because \(1\notin A\); the middle is forbidden because \(x=y=5\).
Therefore \(24\notin A\), while the distinct-index/multiplicity interpretation
above inserts 24.

## Attribution and accompanying material

On the same printed page, Erdős attributes this problem to D. Hofstadter. He
says that Hofstadter had recently told him several problems inspired by a
question of Ulam, and presents a small sample; the product-minus-one problem is
the second sample. The surrounding Ulam/Hofstadter material concerns sequences
defined using sums of consecutive earlier terms.

No initial terms, conjectured answer, heuristic, computation, density
definition, or problem-specific proof hint accompanies the product-minus-one
question in the 1977 paper.

## Reproduction and checks

Reproduction commands for PowerShell (PyMuPDF supplies `fitz`):

```powershell
curl.exe -L https://www.renyi.hu/~p_erdos/1977-27.pdf -o C:\tmp\erdos-1977-27.pdf
Get-FileHash C:\tmp\erdos-1977-27.pdf -Algorithm SHA256
python -c "import fitz; d=fitz.open(r'C:\tmp\erdos-1977-27.pdf'); p=d[28]; print(p.get_text('blocks'))"
python -c "import fitz; d=fitz.open(r'C:\tmp\erdos-1977-27.pdf'); p=d[28]; pix=p.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False); pix.save(r'C:\tmp\erdos-1977-p71.png'); print(len(d), p.rect, pix.width, pix.height)"
```

Observed SHA-256:

```text
8FC7F48707AF5C2536E792226C9E14505FC05CD46078E0C6E05A00810F8229EA
```

The rendered statement and attribution were visually checked at printed p. 71.
The statement reads "distinct elements," contains the subtraction by 1 and
indefinite repetition, and asks for positive density. The OCR text was used
only to locate the passage; the rendered scan controlled the transcription.

## Limitations

- The primary source does not formally specify duplicate suppression. The
  membership normalization above uses its explicit requirement that the two
  selected integer elements be distinct; allowing equal values at distinct
  positions creates the exact 24 discrepancy proved above.
- The primary source does not determine which technical notion of positive
  density Erdős intended in this problem. Its nearby explicit distinction
  between density and lower density prevents attributing the liminf formulation
  to the printed statement without an additional interpretive convention.
- This source check proves the closure normalization and the semantic
  obstruction at 24, but no positive lower-density bound for \(A\).
