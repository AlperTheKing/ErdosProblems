import mpmath as mp
from math import gcd
mp.mp.dps = 90
MODS=[1000000007,1000000009]
THRESH=mp.mpf('1e-8')

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

def cf_convergents(x,qmax):
    y=x; p0,p1=0,1; q0,q1=1,0; out=[]
    for _ in range(160):
        a=int(mp.floor(y)); p=a*p1+p0; q=a*q1+q0; out.append((p,q))
        if q>qmax: break
        frac=y-a
        if abs(frac)<mp.mpf('1e-80'): break
        y=1/frac; p0,p1=p1,p; q0,q1=q1,q
    return out

def consts(k):
    alpha=mp.power(25,mp.mpf(1)/k); c=(mp.mpf(k)+1)/2; A=-(mp.mpf(k)*(mp.mpf(k)*k-1))/24; beta=alpha*A*(1-1/(alpha*alpha))/k; delta=alpha*c-c
    return alpha,c,beta,delta

def zval(alpha,c,beta,n):
    N=mp.mpf(n)+c
    return alpha*N + beta/N - c

def search(Nmin,Nmax,K0,K1):
    exact_checked=0; near_checked=0
    for k in range(K0,K1+1):
        alpha,c,beta,delta=consts(k); conv=cf_convergents(alpha,Nmax); seen=set(); near=0
        for a,q in conv:
            if q<10000 or gcd(a,q)!=1: continue
            inv=pow(a%q,-1,q); base=int(mp.floor((-delta)*q+mp.mpf('0.5')))
            if (Nmax-Nmin)//q > 50000: continue
            for rr in range(-4,5):
                r=((base+rr)%q)*inv%q
                n=r if r>=Nmin else r+((Nmin-r+q-1)//q)*q
                while n<=Nmax:
                    for dn in range(-1,2):
                        nn=n+dn
                        if nn<Nmin or nn>Nmax or nn in seen: continue
                        seen.add(nn)
                        z=zval(alpha,c,beta,nn); m0=int(mp.floor(z+mp.mpf('0.5'))); dist=abs(z-m0)
                        if dist > THRESH: continue
                        near+=1; near_checked+=1
                        for dm in range(-2,3):
                            exact_checked+=1
                            if exact(k,nn,m0+dm): print('HIT',k,nn,m0+dm,flush=True); return True
                    n+=q
        print('sparse-near completed k=%d candidates=%d near=%d total_near=%d exact_checks=%d'%(k,len(seen),near,near_checked,exact_checked),flush=True)
    print('NO_HIT_SPARSE_NEAR',K0,K1,Nmin,Nmax,'near',near_checked,'exact_checks',exact_checked,flush=True)
    return False
if __name__=='__main__':
    import sys
    search(int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[1]),int(sys.argv[2]))
