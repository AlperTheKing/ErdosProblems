# C27: exact bracketing data for the growing-block mass gate

## Verdict

Five additional primitive rays were counted exactly with the Boolean offset
recursion

\[
D_{a,b,c}=2D_{a-1,b,c}\cup(3D_{a,b-1,c}+1)\cup(5D_{a,b,c-1}+3).
\]

The normalized mass is

\[
J_k=\sqrt{k(a+b+c)}\,|D_{ka,kb,kc}|/(2^a3^b5^c)^k.
\]

The data place the low-surplus rays below the favorable `(3,2,1)` ray, but
do not establish an asymptotic threshold.

| ray | entropy surplus | exact `J_k` values |
|---|---:|---|
| `(4,2,1)` | 0.015807 | 0.3822, 0.2973, 0.2501 |
| `(2,1,1)` | 0.016135 | 0.4000, 0.3213, 0.2761, 0.2458, 0.2235, 0.2059 (Fable) |
| `(2,2,1)` | 0.016329 | 0.3727, 0.3011, 0.2613, 0.2351 |
| `(6,3,2)` | 0.024597 | 0.3347, 0.2721 |
| `(4,3,2)` | 0.028935 | 0.3411, 0.2918 |
| `(3,2,1)` | 0.030387 | 0.4082, 0.3493, 0.3222, 0.3075 (Fable) |
| `(5,3,2)` | 0.031608 | 0.3531, 0.3081 |

Exact terminal counts newly obtained here are:

| ray and depth | modulus | support size |
|---|---:|---:|
| `(4,2,1)`, `k=3` | 373248000 | 20370027 |
| `(2,2,1)`, `k=4` | 1049760000 | 55184581 |
| `(6,3,2)`, `k=2` | 1866240000 | 108277936 |
| `(4,3,2)`, `k=2` | 116640000 | 8022073 |
| `(5,3,2)`, `k=2` | 466560000 | 32142875 |

The computation used `claude_rd_offset_mass_deep.py`, SHA-256
`ba85e7a0c15ed27275033ef52ce656c55bede1a7bb5bee7a9870237da19adc9a`.
Raw transcripts are under
`problems/424/compute/wave3/C27_rd_mass_bracket/`.

These are exact finite counts only. In particular, two points on the larger
rays cannot distinguish convergence to a positive constant from slow decay.

Transcript SHA-256 values:

```text
ray_2_2_1_k4.txt 5746643ECD6605A74F7B1E116A7FF5F5C18A10A3767209924B6E6AC08050D1F1
ray_4_2_1_k3.txt A2AED6E4CE30B71C594D0DA31D9F835DB20CE8BB1FFD8DBC4B9C600D473646DD
ray_4_3_2_k2.txt CDACD2CCCCD83CCAA2C9C6138678E159AC4518678FD335C12FAA4E66DFCEDCF0
ray_5_3_2_k2.txt C5C05A0C8A252FB0C8C8D01F3C18881CC5B0D1520C95BB4EB3D81E233FE18B0A
ray_6_3_2_k2.txt DA2A4F49390BEA6419A5B3DE6C02FB2C8C41D287325D4613D023D28F28129ABB
```
