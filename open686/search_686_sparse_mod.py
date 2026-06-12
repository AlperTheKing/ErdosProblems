import mpmath as mp
from math import gcd
mp.mp.dps = 90
MODS=[1000000007,1000000009]

def prod_mod(k,x,p):
    r=1; xm=x%p
    for i in range(1,k+1): r=(r*((xm+i)%p))%p
    return r

def prod(k,x):
    r=1
    for i in range(1,k+1): r*=x+i
    return r

def exact(k,n,m):
    if m<n+k: return False
    for p in MODS:
        if prod_mod(k,m,p)!=(25*prod_mod(k,n,p))%p: return False
    return prod(k,m)==25*prod(k,n)

def cf_convergents(x, qmax):
    y=x; p0,p1=0,1; q0,q1=1,0; out=[]
    for _ in range(160):
        a=int(mp.floor(y)); p=a*p1+p0; q=a*q1+q0; out.append((p,q))
        if q>qmax: break
        frac=y-a
        if abs(frac)<mp.mpf('1e-80'): break
        y=1/frac; p0,p1=p1,p; q0,q1=q1,q
    return out

def center_consts(k):
    alpha=mp.power(25, mp.mpf(1)/k); c=(mp.mpf(k)+1)/2
    A=-(mp.mpf(k)*(mp.mpf(k)*k-1))/24
    beta=alpha*A*(1-1/(alpha*alpha))/k
    return alpha,c,beta,alpha*c-c

def center(alpha,c,beta,n):
    N=mp.mpf(n)+c
    return int(mp.floor(alpha*N + beta/N - c + mp.mpf('0.5')))

def search(Nmin,Nmax,K0,K1):
    checked=0
    for k in range(K0,K1+1):
        alpha,c,beta,delta=center_consts(k)
        seen=set(); conv=cf_convergents(alpha,Nmax)
        for a,q in conv:
            if q<10000: continue
            if gcd(a,q)!=1: continue
            inv=pow(a%q,-1,q)
            base=int(mp.floor((-delta)*q+mp.mpf('0.5')))
            # only use convergents whose arithmetic progression is sparse enough
            if (Nmax-Nmin)//q > 20000: continue
            for rr in range(-16,17):
                r=((base+rr)%q)*inv%q
                n=r if r>=Nmin else r+((Nmin-r+q-1)//q)*q
                while n<=Nmax:
                    for dn in range(-2,3):
                        nn=n+dn
                        if nn<Nmin or nn>Nmax or nn in seen: continue
                        seen.add(nn); checked+=1
                        m0=center(alpha,c,beta,nn)
                        for dm in range(-8,9):
                            if exact(k,nn,m0+dm):
                                print('HIT',k,nn,m0+dm,flush=True); return True
                    n+=q
        print('sparse completed k=%d candidates=%d total_checked=%d'%(k,len(seen),checked),flush=True)
    print('NO_HIT_SPARSE',K0,K1,Nmin,Nmax,'checked',checked,flush=True)
    return False

if __name__=='__main__':
    import sys
    K0=int(sys.argv[1]); K1=int(sys.argv[2]); Nmin=int(sys.argv[3]); Nmax=int(sys.argv[4])
    search(Nmin,Nmax,K0,K1)
