import importlib.util, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod
    assert spec.loader; spec.loader.exec_module(mod); return mod

soft=load("final_soft",ROOT/"tmp/fanout/r53_global_softcap_gate/global_softcap.py")
r35=load("final_r35",ROOT/"tmp/fanout/r35_24_trade/evaluate_trade.py")
ctx=soft.make_graph_context(r35.N,r35.BLUE,r35.BAD)
states={
 "displayed":tuple(r35.DISPLAYED),
 "h1min":(0,0,0,0,0,0,0,0,0,0,31,44),
 "zero_h2":(0,0,0,0,0,0,0,3,5,15,31,44),
}
for label,choice in states.items():
    rows=tuple(r35.ROW_FAMILIES[i][j] for i,j in enumerate(choice))
    st=soft.reconstruct_state(ctx,rows)
    print(label)
    for owner in (6,7,8):
        collision=sum(max(0,st.pair[owner][y]-1) for y in range(ctx.n))
        zero=sum(st.pair[owner][y]==0 for y in range(ctx.n))
        load=5*st.pair[owner][owner]
        internal=sum(owner in e and e[0]==e[1] for e in st.active_edges) # singleton A has no internal edge
        assert internal==0
        assert collision+ctx.n==load+zero
        print(owner,"rows",st.pair[owner][owner],"collision",collision,"zero",zero,"load",load,"N",ctx.n,"overload",load-ctx.n)
print("PASS_OWNER_OVERLOAD_IDENTITY_PROBE")