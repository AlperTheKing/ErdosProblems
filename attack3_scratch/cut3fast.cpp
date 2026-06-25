// Read graph6 from stdin (geng output), for triangle-free graphs:
// compute beta = e - maxcut, and best CUT3 bound (min over nonedges),
// compare to conjectured cap = best balanced C5-blowup value on N vertices.
// Report any graph where best-CUT3-bound > cap (CUT3 fails to prove conjecture),
// and any where beta > cap (would be a counterexample to Erdos #23).
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;

int N;
int conjcap(int Nn){
    int best=-1;
    for(int a=0;a<=Nn;a++)for(int b=0;b+a<=Nn;b++)for(int c=0;a+b+c<=Nn;c++)
      for(int d=0;a+b+c+d<=Nn;d++){int e=Nn-a-b-c-d;
        int ms[5]={a,b,c,d,e}; int v=INT_MAX;
        for(int i=0;i<5;i++)v=min(v,ms[i]*ms[(i+1)%5]);
        if(v>best)best=v;}
    return best;
}

int popcount_u(u64 x){return __builtin_popcountll(x);}

// maxcut by brute force over 2^(N-1), fix vertex0 side0. N<=14 ok-ish.
int maxcut(const vector<u64>&adj,int n){
    // precompute edge list
    int best=0;
    u64 lim=1ULL<<(n-1);
    for(u64 mask=0;mask<lim;mask++){
        u64 side=mask<<1; // bit i set => side1
        int cut=0;
        for(int i=0;i<n;i++){
            u64 nb=adj[i] & (~0ULL<<(i+1)); // j>i
            // edges (i,j) with i in side s, j other side
            u64 hi = nb & (((side>>i)&1)? ~side : side);
            cut+=popcount_u(hi);
        }
        if(cut>best)best=cut;
    }
    return best;
}

int main(){
    string line;
    long long ngraphs=0, capfail=0, betaover=0;
    int worst=-100;
    string worstg;
    while(getline(cin,line)){
        if(line.empty())continue;
        const char*s=line.c_str();
        int p=0;
        int n=s[0]-63; p=1;
        N=n;
        vector<u64> adj(n,0);
        // decode bits
        int bitidx=0;
        int totalbits=n*(n-1)/2;
        // read characters
        vector<int> bits; bits.reserve(totalbits+6);
        for(size_t k=1;k<line.size();k++){
            int v=s[k]-63;
            for(int b=5;b>=0;b--)bits.push_back((v>>b)&1);
        }
        int idx=0;
        for(int j=1;j<n;j++)for(int i=0;i<j;i++){
            if(idx<(int)bits.size() && bits[idx]){adj[i]|=1ULL<<j; adj[j]|=1ULL<<i;}
            idx++;
        }
        ngraphs++;
        int e=0; for(int i=0;i<n;i++)e+=popcount_u(adj[i]); e/=2;
        int mc=maxcut(adj,n);
        int beta=e-mc;
        int cap=conjcap(n);
        // best cut3 over nonedges
        int bestcut3=INT_MAX;
        for(int u=0;u<n;u++)for(int v=u+1;v<n;v++){
            if((adj[u]>>v)&1)continue; // edge
            u64 Nu=adj[u], Nv=adj[v];
            u64 C=Nu&Nv;
            u64 A=Nu&~C; u64 B=Nv&~C;
            u64 all=(n==64)?~0ULL:((1ULL<<n)-1);
            u64 R=all & ~((1ULL<<u)|(1ULL<<v)) & ~Nu & ~Nv;
            int t=popcount_u(C);
            // p=e(A,B)
            int pe=0; { u64 aa=A; while(aa){int i=__builtin_ctzll(aa); aa&=aa-1; pe+=popcount_u(adj[i]&B);} }
            int qe=0; { u64 rr=R; while(rr){int i=__builtin_ctzll(rr); rr&=rr-1; qe+=popcount_u(adj[i]&R);} qe/=2;}
            int xe=0; { u64 aa=A; while(aa){int i=__builtin_ctzll(aa); aa&=aa-1; xe+=popcount_u(adj[i]&R);} }
            int ye=0; { u64 bb=B; while(bb){int i=__builtin_ctzll(bb); bb&=bb-1; ye+=popcount_u(adj[i]&R);} }
            int bd=min(pe+qe, min(t+qe+xe, t+qe+ye));
            if(bd<bestcut3)bestcut3=bd;
        }
        if(bestcut3==INT_MAX)bestcut3=e;
        if(beta>cap){betaover++;}
        if(bestcut3>cap){
            capfail++;
            if(bestcut3-cap>worst){worst=bestcut3-cap; worstg=line;}
        }
    }
    printf("N=%d graphs=%lld cap=%d : CUT3-bound>cap count=%lld (worst overshoot %d), beta>cap count=%lld\n",
           N,ngraphs,conjcap(N),capfail,worst,betaover);
    if(capfail>0) printf("  worst graph6: %s\n", worstg.c_str());
    return 0;
}
