# C119 independent audit

## Checks

- Recomputed the exact identity
  `2131353*8825 = 2144475*8771 = 18809190225`.
- Recomputed `gcd(2131353,2144475)=243`, giving reduced coprime swap
  factors `8771=7^2*179` and `8825=5^2*353`.  Both have two distinct
  prime divisors, so the pair is non-atomic.
- Re-ran `C119_atomic_swap_verify.py` normally and under `python -O`.
  Both are byte-identical to the submitted verification artifact, SHA-256
  `39D89D4BB525DD035053A53ADAA7B5BE45BD3393D485E9669E09AB7F0EEAFAD8`.
- Rehashed the C++ source, audit output, replay output, and Python verifier.
  The two C++ outputs are byte-identical with SHA-256
  `40D4893C6A79CC3BBB267360693A30F86D9AA9C1424D2A10240E879BFEA6D534`.

## Verdict

The `K=3` fibre certificate is accepted and falsifies AO1.  Because its
complete fibre has exactly two representations, no third representation can
factor this collision through atomic swaps.  This closes the atomic
prime-ownership branch only; fixed-`L` Gate T remains open.
