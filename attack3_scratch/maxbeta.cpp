// Read graph6 from stdin, output max beta among triangle-free graphs.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
int popcount_u(u64 x){return __builtin_popcountll(x);}
int maxcut(const vector<u64>&adj,int n){
    int best=0; u64 lim=1ULL<<(n-1);
    for(u64 mask=0;mask<lim;mask++){
        u64 side=mask<<1; int cut=0;
        for(int i=0;i<n;i++){
            u64 nb=adj[i] & (~0ULL<<(i+1));
            u64 hi = nb & (((side>>i)&1)? ~side : side);
            cut+=popcount_u(hi);
        }
        if(cut>best)best=cut;
    }
    return best;
}
int main(){
    string line; long long ng=0; int mx=-1; string mxg;
    while(getline(cin,line)){
        if(line.empty())continue;
        const char*s=line.c_str(); int n=s[0]-63;
        vector<u64> adj(n,0);
        vector<int> bits;
        for(size_t k=1;k<line.size();k++){int v=s[k]-63;for(int b=5;b>=0;b--)bits.push_back((v>>b)&1);}
        int idx=0;
        for(int j=1;j<n;j++)for(int i=0;i<j;i++){if(idx<(int)bits.size()&&bits[idx]){adj[i]|=1ULL<<j;adj[j]|=1ULL<<i;}idx++;}
        ng++;
        int e=0;for(int i=0;i<n;i++)e+=popcount_u(adj[i]);e/=2;
        int beta=e-maxcut(adj,n);
        if(beta>mx){mx=beta;mxg=line;}
    }
    printf("graphs=%lld maxbeta=%d achiever=%s\n",ng,mx,mxg.c_str());
    return 0;
}
