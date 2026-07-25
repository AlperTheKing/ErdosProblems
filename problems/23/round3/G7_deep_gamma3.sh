#!/bin/bash
# deep exhaustive certification of 25*M(Gamma_3,q) <= q^2 for the Wagner graph
W="0-3,0-4,0-5,1-4,1-5,1-6,2-5,2-6,2-7,3-6,3-7,4-7"
cd "E:/Projects/ErdosProblems/problems/23/round3"
for q in $(seq 145 1 400); do
  ./G7_psi_search.exe 8 "$W" $q max 8 G7_aut_Gamma_3.txt 2>/dev/null | head -1
done
