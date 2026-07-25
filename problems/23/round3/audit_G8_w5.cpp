// AUDIT of G8 section 7: independent exact integer check of the 5-cut family on
// And(3) = C8(1,4), for BOTH
//   (i)  the MIN form      25 * min_j q_j(a)  <=  (sum a)^2          [report's check]
//   (ii) the PRODUCT form  5^10 * q1q2q3q4q5(a) <= (sum a)^10        [TERMINAL LEMMA,
//        which the report never checked exactly on the integer grid]
// __int128 throughout for (ii).  Full enumeration, no symmetry reduction.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
using namespace std;
typedef __int128 i128;

static int a[8];
static long long bestmin; static int argmin_[8];
static i128 bestratio_num; static int argprod[8]; static i128 bestprodL, bestprodR;
static int viol;

static inline void qs(const int*x, long long*v){
    v[0]=(long long)x[0]*x[7]+(long long)x[3]*x[4];
    v[1]=(long long)x[1]*x[2]+(long long)x[5]*x[6];
    v[2]=(long long)x[0]*x[1]+(long long)x[4]*x[5];
    v[3]=(long long)x[2]*x[3]+(long long)x[6]*x[7];
    v[4]=(long long)x[0]*x[4]+(long long)x[1]*x[5]+(long long)x[2]*x[6]+(long long)x[3]*x[7];
}

static i128 P10;   // 5^10
static i128 Q10;   // q^10

static void visit(int q){
    long long v[5]; qs(a,v);
    long long m=v[0]; for(int i=1;i<5;i++) if(v[i]<m) m=v[i];
    if(m>bestmin){bestmin=m; for(int j=0;j<8;j++)argmin_[j]=a[j];}
    i128 pr=1; for(int i=0;i<5;i++) pr*= (i128)v[i];
    i128 L=P10*pr;
    if(L>Q10){viol++; if(viol<=3){ }}
    // track the largest L (closest to / above Q10)
    if(L>bestprodL){bestprodL=L; for(int j=0;j<8;j++)argprod[j]=a[j];}
}

static void rec(int i,int rem,int q){
    if(i==7){ a[7]=rem; visit(q); a[7]=0; return;}
    for(int t=0;t<=rem;t++){ a[i]=t; rec(i+1,rem-t,q);} a[i]=0;
}

static void pr128(i128 x){
    if(x==0){printf("0");return;}
    char buf[64]; int n=0; bool neg=x<0; if(neg)x=-x;
    while(x>0){buf[n++]='0'+(int)(x%10); x/=10;}
    if(neg)putchar('-');
    while(n>0)putchar(buf[--n]);
}

int main(int argc,char**argv){
    int qmax=atoi(argv[1]);
    P10=1; for(int i=0;i<10;i++)P10*=5;
    printf("# q | maxmin 25*maxmin q^2 | prodviol max(5^10*prod) q^10 argprod\n");
    for(int q=1;q<=qmax;q++){
        bestmin=-1; bestprodL=-1; viol=0;
        Q10=1; for(int i=0;i<10;i++)Q10*=(i128)q;
        rec(0,q,q);
        long long lhs=25*bestmin, rhs=(long long)q*q;
        printf("%d %lld %lld %lld %s | prodviol=%d max5^10prod=",q,bestmin,lhs,rhs,
               lhs>rhs?"*** MIN FAILS ***":(lhs==rhs?"EQ":""), viol);
        pr128(bestprodL); printf(" q^10="); pr128(Q10);
        printf(" arg=[");
        for(int j=0;j<8;j++)printf("%d%s",argprod[j],j<7?",":"");
        printf("]%s\n", bestprodL>Q10?"  *** TERMINAL LEMMA FALSE ***":(bestprodL==Q10?"  PROD-EQ":""));
        fflush(stdout);
    }
    return 0;
}
