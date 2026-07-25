// G8: exact integer verification of the 5-cut family for And(3)=Wagner=C8(1,4).
// q1=a0a7+a3a4, q2=a1a2+a5a6, q3=a0a1+a4a5, q4=a2a3+a6a7,
// q5=a0a4+a1a5+a2a6+a3a7.
// Checks   25*min_j q_j(a)  <=  (sum a)^2   for every integer a>=0 with sum a = q.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <cstdint>
using namespace std;
static inline long long mn(const int*a){
    long long v1=(long long)a[0]*a[7]+(long long)a[3]*a[4];
    long long v2=(long long)a[1]*a[2]+(long long)a[5]*a[6];
    long long v3=(long long)a[0]*a[1]+(long long)a[4]*a[5];
    long long v4=(long long)a[2]*a[3]+(long long)a[6]*a[7];
    long long v5=(long long)a[0]*a[4]+(long long)a[1]*a[5]+(long long)a[2]*a[6]+(long long)a[3]*a[7];
    long long m=v1; if(v2<m)m=v2; if(v3<m)m=v3; if(v4<m)m=v4; if(v5<m)m=v5; return m;
}
int a[8]; long long best; int barg[8];
void rec(int i,int rem){
    if(i==7){ a[7]=rem; long long v=mn(a); if(v>best){best=v; for(int j=0;j<8;j++)barg[j]=a[j];} a[7]=0; return;}
    for(int t=0;t<=rem;t++){ a[i]=t; rec(i+1,rem-t);} a[i]=0;
}
int main(int argc,char**argv){
    int qmax=atoi(argv[1]);
    printf("# q  max_a min_j q_j  25*val  q^2  argmax\n");
    for(int q=1;q<=qmax;q++){
        best=-1; rec(0,q);
        long long lhs=25*best, rhs=(long long)q*q;
        printf("%d %lld %lld %lld [",q,best,lhs,rhs);
        for(int j=0;j<8;j++)printf("%d%s",barg[j],j<7?",":"");
        printf("]%s\n", lhs>rhs?"  *** 5-CUT FAMILY FAILS ***":"");
        fflush(stdout);
    }
    return 0;
}
