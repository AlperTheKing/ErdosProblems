#!/bin/sh
cd "E:/Projects/ErdosProblems/problems/23/round4"
paste -d'|' H3_vega.g6 H3_vega_names.txt | while IFS='|' read g6 nm; do
  name=$(echo "$nm" | awk '{print $1}')
  nn=$(echo "$nm" | awk '{print $2}' | sed 's/n=//')
  case $nn in
    11|12|13) QMAX=35 ;;
    14|15|16) QMAX=30 ;;
    17|18|19) QMAX=25 ;;
    20|21|22) QMAX=22 ;;
    23|24|25) QMAX=18 ;;
    *) continue ;;
  esac
  q=5
  while [ $q -le $QMAX ]; do
    printf "%-12s q=%-3s " "$name" "$q"
    timeout 1800 ./H3_psi.exe "$g6" $q 8 256 2>/dev/null | head -1
    if [ $? -ne 0 ]; then echo "TIMEOUT"; break; fi
    q=$((q+5))
  done
done
