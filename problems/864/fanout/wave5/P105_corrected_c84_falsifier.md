# P105: exact falsifier to the global collision-corrected C84 inequality

## Verdict

The global candidate

\[
                 T_F(B,h)\le C_S(B,h)+V_b(B,h)
\]

is false for endpoint-normalized integer Sidon systems. An exact witness has

\[
 (p,h,b,C_S,T_F,V_b)=(57,6572,1,159,160,0).
\]

It also satisfies the literal hole. Its defect is `-1726`, so this does not
falsify the candidate with an additional positive-defect hypothesis and does
not by itself obstruct the P82 application.

## Exact witness

Take

```text
B={1,245,327,703,977,999,1057,1107,1363,1675,1677,1841,
1883,2103,2141,2235,2681,2829,2899,3041,3217,3227,3235,
3431,3707,3733,3851,4115,4149,4307,4347,4481,4641,4761,
4951,5043,5129,5193,5197,5309,5577,5679,5803,5901,5917,
6053,6141,6153,6263,6341,6369,6401,6425,6431,6445,6497,6571}.
```

All `57*58/2=1653` diagonal-inclusive unordered sums and all
`57*56/2=1596` positive differences are distinct, and `max(B)=6571=h-1`.
Exact enumeration gives

\[
 C_S=159,\qquad T_F=160,\qquad V_1=0.
\]

The SHA-256 of the comma-separated mark list, with no spaces, is

```text
760cd38d911ce0790ab6e1ce71b5e7e6bb888d3d2a8f3ce150d9abdbc3fdce99
```

## Transformation

Start with an endpoint system `(B_0,h_0)` and apply

\[
 B=2B_0+1,\qquad h=2h_0,\qquad b=1.
\]

Every pair sum becomes `2s+2`, so folds and their three shadow projections
are carried bijectively to the new system. Hence both `C_S` and `T_F` are
unchanged. All positive differences are even, while every low sum plus one
is odd. Therefore `V_1=0`; the same parity separation proves the full
literal hole.

Applying this to the P88 row gives the immediate 60-mark witness
`(C_S,T_F,V_1)=(182,200,0)`. CP-SAT then selected an endpoint-preserving
subset of the P88 source before the lift. The solver returned `OPTIMAL` with
objective and best bound both 57, proving that no smaller subset of that
fixed 60-mark source remains a `T_F>C_S` witness. This is not a global
minimality claim over all integer Sidon systems.

## Reproduction

Run

```powershell
python -B problems/864/compute/p105/verify_witness.py
python -B problems/864/compute/p105/search_corrected_c84_falsifier.py `
  --verify problems/864/compute/p105/corrected_c84_falsifier.json
```

The first program is a standalone integer verifier. The JSON certificate
stores all 159 folds, all 160 loose triangles, the CP-SAT statistics, the
60-mark transformed source, and the retained 57-mark witness.
