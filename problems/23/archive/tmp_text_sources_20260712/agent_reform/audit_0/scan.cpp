// exhaustive ALL-CUT scanner: beta, Rbest (anchored-pentagon count), #C5 via tr(A^5)
// exact integer arithmetic throughout. std::thread parallel over cut masks.
#include <cstdint>
#include <cstdio>
#include <vector>
#include <string>
#include <thread>
#include <fstream>
#include <sstream>
#include <algorithm>
using namespace std;

static inline int pc(uint32_t x){ return __builtin_popcount(x); }

int main(int argc, char** argv){
    ifstream in(argv[1]);
    int ng; in >> ng;
    int T = (int)thread::hardware_concurrency(); if(T<=0) T=8; if(T>64) T=64;
    for(int gi=0; gi<ng; ++gi){
        string name; int n, e;
        in >> name >> n >> e;
        vector<pair<int,int>> ed(e);
        vector<uint32_t> adj(n,0);
        for(int i=0;i<e;i++){
            string tok; in >> tok;
            int u,v; sscanf(tok.c_str(), "%d,%d", &u,&v);
            ed[i]={u,v};
            adj[u] |= 1u<<v; adj[v] |= 1u<<u;
        }
        // tr(A^5) exact (int64)
        vector<vector<long long>> A(n, vector<long long>(n,0));
        for(int i=0;i<n;i++) for(int j=0;j<n;j++) A[i][j] = (adj[i]>>j)&1u;
        auto mul=[&](const vector<vector<long long>>&X,const vector<vector<long long>>&Y){
            vector<vector<long long>> Z(n, vector<long long>(n,0));
            for(int i=0;i<n;i++) for(int k=0;k<n;k++){ long long x=X[i][k]; if(!x) continue;
                for(int j=0;j<n;j++) Z[i][j]+=x*Y[k][j]; }
            return Z;
        };
        auto A2=mul(A,A), A4=mul(A2,A2), A5=mul(A4,A);
        long long tr5=0; for(int i=0;i<n;i++) tr5+=A5[i][i];
        long long C5 = tr5/10;
        uint64_t total = 1ull << (n-1);
        uint32_t full = (n==32)?0xffffffffu:((1u<<n)-1u);
        vector<long long> tBeta(T, 1e18), tR(T, -1);
        vector<thread> th;
        uint64_t chunk = (total + T - 1)/T;
        for(int t=0;t<T;t++){
            th.emplace_back([&,t](){
                uint64_t lo = (uint64_t)t*chunk, hi = min(total, lo+chunk);
                long long bmin = (long long)4e18, rmax = -1;
                for(uint64_t m=lo; m<hi; ++m){
                    uint32_t m32=(uint32_t)m, comp=full^m32;
                    int mono=0; long long R=0;
                    for(int i=0;i<e;i++){
                        int u=ed[i].first, v=ed[i].second;
                        uint32_t su=(m32>>u)&1u;
                        if(su != ((m32>>v)&1u)) continue;
                        ++mono;
                        uint32_t opp = su? comp : m32;
                        uint32_t X = adj[u]&opp, Y = adj[v]&opp;
                        if(!X || !Y) continue;
                        for(int z=0;z<n;z++){
                            uint32_t az=adj[z];
                            R += (long long)pc(az&X)*pc(az&Y);
                        }
                    }
                    if(mono<bmin) bmin=mono;
                    if(R>rmax) rmax=R;
                }
                tBeta[t]=bmin; tR[t]=rmax;
            });
        }
        for(auto&x:th) x.join();
        long long beta=(long long)4e18, Rb=-1;
        for(int t=0;t<T;t++){ beta=min(beta,tBeta[t]); Rb=max(Rb,tR[t]); }
        printf("%s n=%d e=%d beta=%lld Rbest=%lld C5=%lld tr5mod10=%lld propA=%s\n",
               name.c_str(), n, e, beta, Rb, C5, tr5%10, (Rb<=C5?"OK":"VIOLATED"));
        fflush(stdout);
    }
    return 0;
}
