import sys
sys.path.insert(0,'problems/23/writeup')
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_rowgen as rg
for mode in ['none','tight','all']:
 t,g,m=lp.build_chart(0, extra_maxcut=mode)
 rows={mon for mon,c in t.items() if c<0}
 cols=rg.repair_columns_for_rows(rows,g,None)
 print(mode,'gens',len(g),'rows',len(rows),'cols',len(cols))
