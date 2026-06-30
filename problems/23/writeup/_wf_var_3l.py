import _wf_var_3d_data as D
from fractions import Fraction as F
data=D.data
def t(name,fn):
    fh=0;wh=None;fi=0;wi=None
    for rec in data:
        nm,n,f,ll,row,Q,var,Smax,Smin,pfmin=rec
        N=F(n);mean=row/ll
        rhs=fn(N,row,ll,mean)
        if Q>rhs:
            fh+=1
            if wh is None or Q-rhs>wh[0]: wh=(Q-rhs,nm,n,f)
        if rhs-row*row/ll>(N-row)*(N-mean):
            fi+=1
            if wi is None: wi=(nm,n,f)
    print(name,'Qhold-fails',fh,wh,'| imply-E1-fails',fi,wi)
t('Q<=N*row', lambda N,row,ll,mean: N*row)
t('Q<=row*2mean', lambda N,row,ll,mean: row*2*mean)
t('Q<=row*(mean+N)/?halfN', lambda N,row,ll,mean: row*(mean+N)/2)
t('Q<=E1exact', lambda N,row,ll,mean: N*N-N*mean-ll*N*mean+2*ll*mean*mean)
print('rows',len(data))
