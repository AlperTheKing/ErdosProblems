# Exact balanced-C5-blow-up face in Gamma_11

## Scope

This is an exact face computation for the registered fixed-c=25,
degree-4, 56-arc certificate. It enumerates every induced support
that is a complete C5 blow-up with five nonempty classes. It does
**not** claim that these plateaus exhaust the full ARCBOUND equality set.

## Exact enumeration

```json
{
  "D22_orbit_size_distribution": {
    "11": 8,
    "22": 2
  },
  "D22_x_AutC5_orbits": 10,
  "class_maps_before_AutC5_quotient": 1320,
  "complete_c5_blowup_supports": 132,
  "orbit_representatives": [
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        1,
        1,
        1
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1
        ],
        [
          5
        ]
      ],
      "support": [
        0,
        1,
        4,
        5,
        8
      ]
    },
    {
      "D22_orbit_size": 22,
      "class_sizes": [
        1,
        1,
        1,
        1,
        2
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1
        ],
        [
          5,
          6
        ]
      ],
      "support": [
        0,
        1,
        4,
        5,
        6,
        8
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        1,
        1,
        3
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1
        ],
        [
          5,
          6,
          7
        ]
      ],
      "support": [
        0,
        1,
        4,
        5,
        6,
        7,
        8
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        1,
        1,
        2
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1
        ],
        [
          5,
          7
        ]
      ],
      "support": [
        0,
        1,
        4,
        5,
        7,
        8
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        1,
        1,
        1
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1
        ],
        [
          6
        ]
      ],
      "support": [
        0,
        1,
        4,
        6,
        8
      ]
    },
    {
      "D22_orbit_size": 22,
      "class_sizes": [
        1,
        1,
        1,
        2,
        1
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1,
          2
        ],
        [
          6
        ]
      ],
      "support": [
        0,
        1,
        2,
        4,
        6,
        8
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        1,
        2,
        2
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          1,
          2
        ],
        [
          6,
          7
        ]
      ],
      "support": [
        0,
        1,
        2,
        4,
        6,
        7,
        8
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        1,
        1,
        1
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8
        ],
        [
          2
        ],
        [
          6
        ]
      ],
      "support": [
        0,
        2,
        4,
        6,
        8
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        2,
        1,
        1
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8,
          9
        ],
        [
          2
        ],
        [
          6
        ]
      ],
      "support": [
        0,
        2,
        4,
        6,
        8,
        9
      ]
    },
    {
      "D22_orbit_size": 11,
      "class_sizes": [
        1,
        1,
        2,
        1,
        2
      ],
      "classes": [
        [
          0
        ],
        [
          4
        ],
        [
          8,
          9
        ],
        [
          2
        ],
        [
          6,
          7
        ]
      ],
      "support": [
        0,
        2,
        4,
        6,
        7,
        8,
        9
      ]
    }
  ],
  "q10_witness": {
    "class_sums": [
      2,
      2,
      2,
      2,
      2
    ],
    "classes": [
      [
        0
      ],
      [
        4
      ],
      [
        8
      ],
      [
        1,
        2
      ],
      [
        6,
        7
      ]
    ],
    "included": true,
    "support": [
      0,
      1,
      2,
      4,
      6,
      7,
      8
    ],
    "weights": [
      2,
      1,
      1,
      0,
      2,
      0,
      1,
      1,
      2,
      0,
      0
    ]
  },
  "support_size_distribution": {
    "5": 33,
    "6": 66,
    "7": 33
  }
}
```

For a nonempty complete blow-up, equal open-neighbourhood classes
are exactly its five blow-up classes. Hence each accepted support has
one class map modulo Aut(C5), and the support enumeration is complete.

## Forced multiplier face

On a class-sum-one plateau, Theorem B gives q_S(x)>=1. The
normalization and SOS identity force
`sum_S nu_S(x)(q_S(x)-1)=0`. If the restriction of q_S-1 is not
the zero polynomial, it is strictly positive at an interior plateau
point; coefficientwise nonnegativity then kills every coefficient of
nu_S whose monomial support lies in that blow-up support.

```text
C5-only forced multiplier orbits = 1147
all blow-up forced multiplier orbits = 2085
increment = 938
```

## Exact parity-block evaluation spans

For parity mask p, write a degree-6 Gram monomial as
`y^p x^gamma`, where `|gamma|=(6-|p|)/2`, hence degree 0..3.
The factor y^p is common and nonzero on an interior plateau whenever
`supp(p)` lies in the support. In every class one pivot variable is
eliminated by `x_pivot=1-sum(other class variables)`. Expanding all
`x^gamma` gives integer coefficient rows whose rational span is
exactly the span of all plateau evaluations (the interior is Zariski
dense in the product of simplices).

```text
C5-only Gram-face rank = 1471
all blow-up Gram-face rank = 6129
increment = 4658
independent integer H nonzeros = 71973
remaining invariant Gram dimension = 2518
```

Every evaluation span is closed under the relevant stabilizer in exact
rational arithmetic. The invariant symmetric-face dimension is computed
by the character formula, and integer Qv=0 equations attain the
resulting codimension modulo the exact prime 2000003.

## Per-block data

```json
[
  {
    "candidate_rows": 286,
    "degree_in_x": 3,
    "evaluation_span_dimension": 132,
    "gram_constraint_rank": 1364,
    "gram_face_dimension": 582,
    "gram_scalars": 1946,
    "order": 286,
    "parity_orbit": 0,
    "parity_weight": 0,
    "stabilizer_order": 22
  },
  {
    "candidate_rows": 121,
    "degree_in_x": 2,
    "evaluation_span_dimension": 34,
    "gram_constraint_rank": 858,
    "gram_face_dimension": 273,
    "gram_scalars": 1131,
    "order": 66,
    "parity_orbit": 1,
    "parity_weight": 2,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 118,
    "degree_in_x": 2,
    "evaluation_span_dimension": 31,
    "gram_constraint_rank": 805,
    "gram_face_dimension": 326,
    "gram_scalars": 1131,
    "order": 66,
    "parity_orbit": 2,
    "parity_weight": 2,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 95,
    "degree_in_x": 2,
    "evaluation_span_dimension": 26,
    "gram_constraint_rank": 710,
    "gram_face_dimension": 421,
    "gram_scalars": 1131,
    "order": 66,
    "parity_orbit": 3,
    "parity_weight": 2,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 19,
    "degree_in_x": 1,
    "evaluation_span_dimension": 6,
    "gram_constraint_rank": 27,
    "gram_face_dimension": 9,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 4,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 135,
    "degree_in_x": 2,
    "evaluation_span_dimension": 34,
    "gram_constraint_rank": 858,
    "gram_face_dimension": 273,
    "gram_scalars": 1131,
    "order": 66,
    "parity_orbit": 5,
    "parity_weight": 2,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 17,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 45,
    "gram_face_dimension": 21,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 6,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 9,
    "degree_in_x": 1,
    "evaluation_span_dimension": 3,
    "gram_constraint_rank": 16,
    "gram_face_dimension": 20,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 7,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 122,
    "degree_in_x": 2,
    "evaluation_span_dimension": 33,
    "gram_constraint_rank": 840,
    "gram_face_dimension": 291,
    "gram_scalars": 1131,
    "order": 66,
    "parity_orbit": 8,
    "parity_weight": 2,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 17,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 45,
    "gram_face_dimension": 21,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 9,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 16,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 45,
    "gram_face_dimension": 21,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 10,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 11,
    "degree_in_x": 1,
    "evaluation_span_dimension": 4,
    "gram_constraint_rank": 20,
    "gram_face_dimension": 16,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 11,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 18,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 24,
    "gram_face_dimension": 12,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 12,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 13,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 26,
    "degree_in_x": 1,
    "evaluation_span_dimension": 7,
    "gram_constraint_rank": 56,
    "gram_face_dimension": 10,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 14,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 13,
    "degree_in_x": 1,
    "evaluation_span_dimension": 4,
    "gram_constraint_rank": 38,
    "gram_face_dimension": 28,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 15,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 9,
    "degree_in_x": 1,
    "evaluation_span_dimension": 3,
    "gram_constraint_rank": 30,
    "gram_face_dimension": 36,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 16,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 18,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 45,
    "gram_face_dimension": 21,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 17,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 21,
    "degree_in_x": 1,
    "evaluation_span_dimension": 6,
    "gram_constraint_rank": 27,
    "gram_face_dimension": 9,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 18,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 19,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 24,
    "degree_in_x": 1,
    "evaluation_span_dimension": 7,
    "gram_constraint_rank": 30,
    "gram_face_dimension": 6,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 20,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 21,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 22,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 26,
    "degree_in_x": 1,
    "evaluation_span_dimension": 7,
    "gram_constraint_rank": 56,
    "gram_face_dimension": 10,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 23,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 18,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 45,
    "gram_face_dimension": 21,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 24,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 23,
    "degree_in_x": 1,
    "evaluation_span_dimension": 6,
    "gram_constraint_rank": 51,
    "gram_face_dimension": 15,
    "gram_scalars": 66,
    "order": 11,
    "parity_orbit": 25,
    "parity_weight": 4,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 28,
    "degree_in_x": 1,
    "evaluation_span_dimension": 7,
    "gram_constraint_rank": 30,
    "gram_face_dimension": 6,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 26,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 27,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 24,
    "degree_in_x": 1,
    "evaluation_span_dimension": 7,
    "gram_constraint_rank": 30,
    "gram_face_dimension": 6,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 28,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 16,
    "degree_in_x": 1,
    "evaluation_span_dimension": 5,
    "gram_constraint_rank": 24,
    "gram_face_dimension": 12,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 29,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 30,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 31,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 32,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 33,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 34,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 35,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 36,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 37,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 1,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 36,
    "gram_scalars": 36,
    "order": 11,
    "parity_orbit": 38,
    "parity_weight": 4,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 39,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 40,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 41,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 42,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 43,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 44,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 45,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 46,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 47,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 48,
    "parity_weight": 6,
    "stabilizer_order": 1
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 49,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 0,
    "degree_in_x": 0,
    "evaluation_span_dimension": 0,
    "gram_constraint_rank": 0,
    "gram_face_dimension": 1,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 50,
    "parity_weight": 6,
    "stabilizer_order": 2
  },
  {
    "candidate_rows": 1,
    "degree_in_x": 0,
    "evaluation_span_dimension": 1,
    "gram_constraint_rank": 1,
    "gram_face_dimension": 0,
    "gram_scalars": 1,
    "order": 1,
    "parity_orbit": 51,
    "parity_weight": 6,
    "stabilizer_order": 2
  }
]
```
