#!/bin/sh
cd "E:/Projects/ErdosProblems/problems/23/round4"
run () {  # name g6 qmax
  nm=$1; g6=$2; qmax=$3
  for q in $(seq 5 5 $qmax); do
    printf "%s q=%s : " "$nm" "$q"
    ./H3_psi.exe "$g6" $q 8 256 2>/dev/null | head -1
  done
  for q in 6 7 8 9 11 12 13 14 16 17 18 19; do
    if [ $q -le $qmax ]; then
      printf "%s q=%s : " "$nm" "$q"
      ./H3_psi.exe "$g6" $q 8 256 2>/dev/null | head -1
    fi
  done
}
run Ups2-y-2i "JRBHOrBHOk?" 40
