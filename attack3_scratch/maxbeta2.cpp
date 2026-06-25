// Faster: Gray-code maxcut. Read graph6, output max beta among triangle-free.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
static inline int pc(u64 x){return __builtin_popcountll(x);}

int maxcut(const vector<u64>&adj,int n){
    // side[] as bitmask 'side' (bit i = side of vtx i). Start all side 0. cut=0.
    // Gray code over vertices 1..n-1 (vertex0 fixed side0). When we flip vertex v,
    // change in cut = (#neighbors on same side) - (#neighbors on other side)
    // = deg_in_currentSameSide - deg_other. Easier: delta = (sameSideNbrs - otherSideNbrs).
    // Maintain 'side' mask. cut counts edges crossing.
    u64 side=0; int cut=0; int best=0;
    u64 steps=(1ULL<<(n-1)); // number of gray codes for n-1 free bits
    // gray code: at step k (1..steps-1) flip bit = ctz(k) of the (n-1)-bit counter, mapped to vertex (bit+1)
    for(u64 k=1;k<steps;k++){
        int b=__builtin_ctzll(k);
        int v=b+1;
        u64 nb=adj[v];
        u64 sameMask = ((side>>v)&1)? side : ~side; // neighbors on same side as v currently
        int same=pc(nb & sameMask);
        int other=pc(nb)-same;
        // flipping v: edges to same-side become crossing (+same), edges to other-side become non-crossing (-other)
        cut += same - other;
        side ^= (1ULL<<v);
        if(cut>best)best=cut;
    }
    // also best could be at step0 (cut=0) - fine
    return best;
}
int main(){
    string line; long long ng=0; int mx=-1; string mxg;
    while(getline(cin,line)){
        if(line.empty())continue;
        const char*s=line.c_str(); int n=s[0]-63;
        vector<u64> adj(n,0); vector<int> bits;
        for(size_t k=1;k<line.size();k++){int v=s[k]-63;for(int b=5;b>=0;b--)bits.push_back((v>>b)&1);}
        int idx=0;
        for(int j=1;j<n;j++)for(int i=0;i<j;i++){if(idx<(int)bits.size()&&bits[idx]){adj[i]|=1ULL<<j;adj[j]|=1ULL<<i;}idx++;}
        ng++;
        int e=0;for(int i=0;i<n;i++)e+=pc(adj[i]);e/=2;
        int beta=e-maxcut(adj,n);
        if(beta>mx){mx=beta;mxg=line;}
    }
    printf("graphs=%lld maxbeta=%d achiever=%s\n",ng,mx,mxg.c_str());
    return 0;
}
