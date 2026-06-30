from _codex_ocpms_petersen_blow import blow

def cut_value(E,side):
    return sum(1 for a,b in E if side[a]!=side[b])

def maxcut(n,E):
    best=-1; bestmask=None
    for mask in range(1<<n):
        val=0
        for a,b in E:
            if ((mask>>a)&1)!=((mask>>b)&1): val+=1
        if val>best:
            best=val; bestmask=mask
    return best,bestmask
for w in [[1,2,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,2,1,1],[2,2,1,1,1,1,1,1,1,1],[1,1,1,1,1,2,1,2,1,1]]:
    n,E,side=blow(w)
    cv=cut_value(E,side)
    mc,mask=maxcut(n,E)
    print('w',w,'n',n,'cut',cv,'maxcut',mc,'ismax',cv==mc,'gap',mc-cv,'bestmask',bin(mask))
