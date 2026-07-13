"""Exact dynamic search for affine block maps of a fixed slope M.

For f_d(x)=d*x-1 and a word with all d in the exact Erdos-424 closure G,
write F(x)=M*x-C.  INTERCEPTS[M] is the exact set of all such C, including
all ordered factorizations of M over G.  Recurrence: appending outer d sends
(M/d,C0) to (M,d*C0+1).  INTERCEPTS[1]={0} is the empty word only.
"""
import argparse, json, math, hashlib


def spf_sieve(n):
    spf=list(range(n+1))
    for p in range(2,math.isqrt(n)+1):
        if spf[p]==p:
            for q in range(p*p,n+1,p):
                if spf[q]==q: spf[q]=p
    return spf


def divisors(n,spf):
    ds=[1]
    while n>1:
        p=spf[n]; e=0
        while n%p==0: n//=p; e+=1
        old=tuple(ds); pk=1
        for _ in range(e):
            pk*=p
            ds.extend(d*pk for d in old)
    return ds


def closure(limit,spf):
    g=bytearray(limit+1); g[2]=g[3]=1
    for n in range(4,limit+1):
        m=n+1
        for d in divisors(m,spf):
            q=m//d
            if 2<=d<q and g[d] and g[q]:
                g[n]=1; break
    return g


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--limit',type=int,default=10000)
    ap.add_argument('--top',type=int,default=30)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    L=args.limit
    spf=spf_sieve(L+1); g=closure(L,spf)
    cs=[None]*(L+1); cs[1]={0}
    rows=[]
    for m in range(2,L+1):
        cur=set()
        for d in divisors(m,spf):
            if d<2 or d>L or not g[d]: continue
            prev=cs[m//d]
            if not prev: continue
            cur.update(d*c+1 for c in prev)
        cs[m]=cur
        if cur:
            rows.append({'M':m,'maps':len(cur),'missing':m-1-len(cur),
                         'mass_num':len(cur),'mass_den':m,
                         'coverage':len(cur)/(m-1)})
    rows.sort(key=lambda r:(r['coverage'],r['maps']),reverse=True)
    out={'schema':1,'limit':L,'definition':'all nonempty G-word maps F(x)=M*x-C',
         'best':rows[:args.top],
         'perfect_M_minus_1':[r['M'] for r in rows if r['missing']==0],
         'at_least_half_count':sum(r['coverage']>=.5 for r in rows)}
    with open(args.output,'w') as f: json.dump(out,f,indent=2)
    print('G count',sum(g),'nonempty slopes',len(rows),'perfect',len(out['perfect_M_minus_1']))
    for r in rows[:args.top]: print(r)
    print('sha256',hashlib.sha256(open(__file__,'rb').read()).hexdigest())

if __name__=='__main__': main()
