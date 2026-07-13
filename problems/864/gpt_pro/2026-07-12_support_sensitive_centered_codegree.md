# Support-sensitive centered codegree identity

Source: GPT-Pro response relayed by the user on 2026-07-12. Reconstructed
locally from the conversation after the browser copy disappeared.

Let `A` be finite, `m=|A|`, and

    nu_A(d)=#{a in A : a+d in A}.

For a nonempty finite `X subset Z`, put `h=|X|`,

    rho_X(d)=#{{x,x'} subset X : |x-x'|=d},
    Z_X(A)=sum_{d>=1} rho_X(d)(nu_A(d)-1),
    M_X(A)=|A-X|,
    D_X(y)=#{x in X : x+y in A}.

Then the exact identity is

    M_X(A) * (1+(m-1)/h+2Z_X(A)/h^2) - m^2
      = M_X(A)/h^2 * sum_{y in A-X}
          (D_X(y)-mh/M_X(A))^2.                         (1)

Consequently

    m^2 <= M_X(A) * (1+(m-1)/h+2Z_X(A)/h^2).           (2)

Proof. In the bipartite sum graph with left side `X`, right side `A-X`,
and `x~y` iff `x+y in A`, one has `sum_y D_X(y)=mh`. Two distinct
`x,x'` at distance `d` have exactly `nu_A(d)` common neighbors, so

    sum_y binom(D_X(y),2)=binom(h,2)+Z_X(A),
    sum_y D_X(y)^2=mh+h(h-1)+2Z_X(A).

Subtracting the square of the mean gives (1).

If the exceptional sum is `sigma`, write `c=sigma/2` and

    P=A intersect (sigma-A)
      ={c}^delta union {c-u_i,c+u_i : 1<=i<=q}.

Then the duplicated positive differences are the disjoint union

    {u_j-u_i : i<j},
    {u_i+u_j : i<j},
    {u_i : 1<=i<=q} if delta=1.                         (3)

Therefore

    Z_X(A)
      = sum_{i<j}[rho_X(u_j-u_i)+rho_X(u_i+u_j)]
        + delta sum_i rho_X(u_i)
        - sum_{nu_A(d)=0} rho_X(d).                      (4)

For `X_H={0,...,H-1}`,

    rho_XH(d)=H-d (1<=d<H),
    M_H(A)=H+sum_{i=2}^m min(a_i-a_{i-1},H),             (5)

and

    m^2 <= M_H(A)*(1+(m-1)/H+2Z_H(A)/H^2).              (6)

The proposed scalar frontier is to find `H` or a more flexible test set
`X` for which

    (M_X(A)/N)*(1+2Z_X(A)/|X|^2) <= 4/3+o(1).           (7)

For the Erdos-Freud reflected family the factors approach `2/3` and `2`,
respectively, so (7) is tight. A standalone bound `Z_H<=H^2/6` is false:
for the N=69 extremizer and H=16, every distance 1..15 is duplicated and
`Z_16=120`.

Exact audit: `problems/864/compute/verify_gpt_support_identity.py` checks
(1) for 16,128 pairs `(A,X)` and the N=69 example exactly with `Fraction`.