# PHT adversarial gate

## Verdict

No PHT falsifier was found.

The exact finite gate tested 226,354 row tuples in 19 adversarial systems.
It found 903 active-scoped Hall failures and all 903 satisfied

sum_eta S(eta) <= |Omega| (S(omega) - defect).

The earlier complete connected triangle-free census has 705 failures through
orders 10 and 11, all passing PHT. Orders 5 through 9 have no active-scoped
Hall failures.

## Adversarial systems

- Exchange falsifier graph I?[tick]fBO]]?: 144 tuples, 2 Hall failures,
  minimum PHT residual 2,410.
- Submodularity falsifier graph I?[tick]cjVo{?: 256 tuples, 4 failures,
  minimum residual 4,108.
- Prior smallest PHT graph I?[tick]ebRodO: 108 tuples, 1 failure,
  minimum residual 1,804.
- Order-12 inherited-component graph K?ABBBwerwBw: 100,000 tuples,
  416 failures, minimum residual 754,312.
- Reconstructed 89-vertex singleton double-star: scoped score zero and no
  scoped Hall failure, so PHT is vacuous. This confirms the old 528/526
  deficit is unscoped.
- Fifteen nonuniform C5 blow-up types were attempted. Fourteen fit the
  one-million-product cap. Types (2,2,3,2,2) and (2,3,2,3,2) contributed
  192 and 288 Hall failures respectively, with zero PHT failures.
- Uniform (3,3,3,3,3) has product size 27^9 = 7,625,597,484,987 and was
  skipped rather than sampled.

All accepted arithmetic is integer exact. The smallest tested PHT residual
remains 1,804 on I?[tick]ebRodO, corresponding to normalized margin 451/27.

## Reconstructed R29

The later R29 gate artifacts now provide a deterministic 2,943-vertex
reconstruction with canonical instance SHA-256
fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f.
Independent artifacts certify:

- baseline scoped score 30,811;
- maximum Hall defect 28 at shore {0,1,2};
- 676 selector families, each with 680 rows;
- an exact global selector minimum 23,115 at the all-anchor support pattern.

Thus the baseline is not a global minimum regardless of PHT.

The full PHT product has cardinality 680^676. The Fraction gate compressed
all ordered-pair occupancy expectations without enumeration. A completely
unconditional raw/scoping upper bound is 34,666 and is inconclusive against
the PHT threshold 30,783.

A sharper exact bound gives expected score less than 29,585, hence PHT margin
greater than 1,198, conditional on these two structural statements:

1. selector vertices q_L and q_R are never ActiveOwner for any selector
   tuple;
2. anchor active degree is at most 4 plus twice the number of local rows.

The lock-arm portion also uses: a lock-arm owner can be active only when a
local row touches its unique traffic-leaf region. The script verifies each
selector has four local rows, every local row has one D-arm x vertex, and
each traffic-leaf trigger involves exactly 27 or 28 selector families.

Baseline, all-anchor, and eight deterministic uniform-product samples satisfy
the two structural statements. Sample scores range from 24,018 to 24,686,
with zero q_L/q_R activations. This is exact evidence, not a proof over all
680^676 tuples.

## Smallest-falsifier status

No real-graph falsifier exists through the tested order-11 census or the
listed order-12/C5/adversarial fixtures. No abstract surrogate was accepted
as a falsifier because PHT is a statement about the current active-scoped
score and exact Hall defect.

The only unresolved test is the unconditional R29 product. Closing it now
reduces to proving or falsifying the three named component-activation
statements above; the scalar Fraction arithmetic already has margin.

## Proof gaps

- Universal q_L/q_R inactivity is not proved.
- The anchor degree and lock-region trigger bounds are verified on the
  construction and samples but not formalized for every selector tuple.
- The uniform C5(3,3,3,3,3) product exceeds the current exact-enumeration cap.
- PHT itself still lacks a graph-theoretic proof; finite tests cannot replace
  the full-product transport/Hall-capacity lemma.

## Artifact hashes

- pht_adversarial_gate.py:
  50b2cd506850ffba36a531e8d814fe0e38aa27e1931eca8a1bc61e09c986384d
- pht_adversarial.json:
  be502a567d012d2690cfcd2e82bcefe796c156e9e25795310f2e916ffa2ffb22
- pht_n5_n9.json:
  ff1bf376f3b6e92ccfbba752b94d2ab05ebd68be4bf1e78bc210d3ee15c6800f
- r29_pht_bound.py:
  6774554ddae8616f6b6252d316b5eb706c73b90e88d1c696f7348b37bbaa4b5e
- r29_pht_bound.json:
  37cd0baaf472379c087b1f3baea189cde61609a76b9762a104fe47e02e06e1f9
- r29_sample_probe.py:
  cb49b4aa166e04ed9baca449c02141abde27c6190b9579423cdca8c5377795de
- r29_samples.json:
  eb2a75501ac9bce71edfe86306f909f02e971a4713ab0aeb4af86b85cf0624d3
- reconstructed R29 lead script:
  5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6
- reconstructed R29 Hall result:
  13606794cad87e26635c5995171a32572bdf33f9e5d23e00dad427ec032513d9
