# Erdős 742 R1 exact SAT lane

Build:

```powershell
g++ -std=c++20 -O2 -Wall -Wextra -pedantic generate_d2c_cnf.cpp -o generate_d2c_cnf.exe
g++ -std=c++20 -O2 -Wall -Wextra -pedantic verify_b.cpp -o verify_b.exe
g++ -std=c++20 -O2 -Wall -Wextra -pedantic decode_model.cpp -o decode_model.exe
```

Calibrate before any search:

```powershell
python calibrate.py
python audit_exhaustive.py
generate_d2c_cnf.exe --n 25 --min-edges 157 --output d2c_n25_m157.cnf --map d2c_n25_m157.map
python audit_target_boundary.py
```

The production CNF contains no symmetry breaking.  Edge variables are the
first \(\binom n2\) variables in lexicographic pair order.  A SAT solver model
can be converted to Verifier B's strict binary matrix format with:

```powershell
decode_model.exe d2c_n25_m157.map solver.model candidate.matrix
verify_b.exe --input candidate.matrix --expect-n 25 --min-edges 157
```

Verifier B recomputes every pair's length-at-most-two reachability after
every edge deletion.  A second verifier with a different input parser and
algorithm is still required before accepting any candidate.
