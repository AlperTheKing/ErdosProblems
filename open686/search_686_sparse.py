import mpmath as mp
from math import gcd
mp.mp.dps = 100

def prod(k,x):
    r=1
    for i in range(1,k+1): r*=x+i
    return r

def exact(k,n,m):
    return m>=n+k and prod(k,m)==25*prod(k,n)

def cf_convergents(x, qmax):
    a0 = mp.floor(x); a=int(a0)
    p_nm2,p_nm1=0,1; q_nm2,q_nm1=1,0
    y=x
    out=[]
    for _ in range(200):
        a=int(mp.floor(y))
        p=a*p_nm1+p_nm2; q=a*q_nm1+q_nm2
        out.append((p,q))
        if q>qmax: break
        frac=y-a
        if abs(frac) < mp.mpf('1e-90'): break
        y=1/frac
        p_nm2,p_nm1=p_nm1,p; q_nm2,q_nm1=q_nm1,q
    return out

def center(k,n):
    alpha=mp.power(25, mp.mpf(1)/k)
    c=(mp.mpf(k)+1)/2
    A=-(mp.mpf(k)*(mp.mpf(k)*k-1))/24
    beta=alpha*A*(1-1/(alpha*alpha))/k
    N=mp.mpf(n)+c
    return int(mp.floor(alpha*N + beta/N - c + mp.mpf('0.5')))

def search(Nmin,Nmax,K0,K1):
    checked=0
    for k in range(K0,K1+1):
        alpha=mp.power(25, mp.mpf(1)/k)
        c=(mp.mpf(k)+1)/2
        delta=alpha*c-c
        conv=cf_convergents(alpha, Nmax)
        seen=set()
        for a,q in conv:
            if q < 1000: continue
            if q > Nmax*10: break
            # inhomogeneous target residues a*n/q + delta ~= integer.
            if gcd(a,q)!=1: continue
            inv=pow(a % q, -1, q)
            base=int(mp.floor((-delta)*q + mp.mpf('0.5')))
            for rr in range(-8,9):
                target=(base+rr) % q
                r=(target*inv) % q
                if r < Nmin:
                    t=(Nmin-r + q-1)//q
                    n=r+t*q
                else:
                    n=r
                cap=0
                while n<=Nmax and cap<2000:
                    for dn in range(-2,3):
                        nn=n+dn
                        if nn<Nmin or nn>Nmax or nn in seen: continue
                        seen.add(nn); checked+=1
                        m0=center(k,nn)
                        for dm in range(-8,9):
                            m=m0+dm
                            if exact(k,nn,m):
                                print('HIT',k,nn,m,flush=True); return True
                    n += q; cap += 1
        print(f'sparse completed k={k} candidates={len(seen)} total_checked={checked}', flush=True)
    print('NO_HIT_SPARSE',K0,K1,Nmin,Nmax,'checked',checked,flush=True)
    return False

search(100_000_001, 10_000_000_000, 3, 300)
