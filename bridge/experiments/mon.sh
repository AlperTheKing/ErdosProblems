p='C:\Users\a\AppData\Local\Temp\claude\E--Projects-ErdosProblems\461052bb-8cbc-4d9f-996c-62e0fcc0bfcb\tasks\bn7z97ek6.output'
until grep -q "FINAL" "$p" 2>/dev/null; do sleep 5; done
tail -25 "$p"
