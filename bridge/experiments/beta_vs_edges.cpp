// beta-vs-edge-count profile for triangle-free graphs at N=15 and N=20.
// Goal: quantify how far below n^2 the OPEN medium-density band (0.2486..0.3197)
// sits. The extremizer C5[n] is at density 0.4; a counterexample would have to be
// sparser yet have higher beta. This maps max beta as a function of e.
//
// For each target edge count e_t, generate many random triangle-free graphs with
// EXACTLY e_t edges (random edge order, stop at e_t), record max beta seen.
// Build: clang++ -O3 -std=c++17 -pthread beta_vs_edges.cpp -o beta_vs_edges.exe
#include <cstdio>
#include <cstdint>
#include <vector>
#include <random>
#include <algorithm>

static int N;
static inline int popc(uint32_t x){ return __builtin_popcount(x); }

struct G { std::vector<uint32_t> a; G():a(32,0){} };
static inline bool addSafe(G&g,int u,int v){ if(g.a[u]&(1u<<v))return false; if(g.a[u]&g.a[v])return false; g.a[u]|=(1u<<v);g.a[v]|=(1u<<u);return true; }

static long maxcut(const G&g,long&E){
    uint32_t b[32]; for(int i=0;i<N;i++) b[i]=g.a[i];
    E=0; for(int i=0;i<N;i++) E+=popc(g.a[i]); E/=2;
    long best=0; long lim=1L<<(N-1);
    for(long h=0;h<lim;h++){ uint32_t s1=(uint32_t)(h<<1); long cut=0; uint32_t x=s1; while(x){int v=__builtin_ctz(x);x&=x-1; cut+=popc(b[v]&~s1);} if(cut>best)best=cut; }
    return best;
}
static long betaOf(const G&g){ long E; long mc=maxcut(g,E); return E-mc; }

// generate a random triangle-free graph with exactly et edges (or as close as reachable)
static G genExact(std::mt19937&rng,int et){
    for(int attempt=0;attempt<40;attempt++){
        G g; std::vector<std::pair<int,int>> pr;
        for(int u=0;u<N;u++)for(int v=u+1;v<N;v++) pr.push_back({u,v});
        std::shuffle(pr.begin(),pr.end(),rng);
        int cnt=0;
        for(auto&p:pr){ if(cnt>=et) break; if(addSafe(g,p.first,p.second)) cnt++; }
        if(cnt==et) return g;
    }
    return G(); // failed (et not reachable triangle-free); caller checks edge count
}

int main(int argc,char**argv){
    N=argc>1?atoi(argv[1]):15; int reps=argc>2?atoi(argv[2]):3000;
    int n=N/5; int maxE=N*N/4; // Turan bound for triangle-free
    double C2=N*(N-1)/2.0;
    printf("N=%d n=%d n^2=%d  Turan maxE=%d  band density(0.2486,0.3197) -> e in [%.0f, %.0f]\n",
           N,n,n*n,maxE,0.2486*C2,0.3197*C2);
    printf("extremizer C5[n] density=0.4 -> e=%d (beta=%d)\n", (int)(0.4*C2+0.5), n*n);
    printf(" e   density   maxbeta_seen   (n^2=%d)   band?\n",n*n);
    std::mt19937 rng(20260620u);
    for(int et=N; et<=maxE; et++){
        long mb=0; int got=0;
        for(int r=0;r<reps;r++){ G g=genExact(rng,et); long E; maxcut(g,E); if(E!=et) continue; got++; long b=betaOf(g); if(b>mb)mb=b; }
        if(got<reps/4) continue; // skip edge counts hard to reach
        double dens=et/C2;
        const char* band = (dens>=0.2486 && dens<=0.3197) ? "  <-- OPEN BAND" : "";
        printf(" %3d  %.4f      %3ld          %s\n",et,dens,mb,band);
    }
    return 0;
}
