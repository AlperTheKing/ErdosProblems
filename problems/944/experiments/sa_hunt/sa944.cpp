// SA hunt for 4-vertex-critical graphs with no critical edge (Dirac k=4).
// Objective(G) = BIG*[G 3-colorable] + sum_v [G-v not 3-col] + sum_{e in E} [G-e 3-col]  -> want 0
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <random>
#include <thread>
#include <atomic>
#include <vector>
#include <mutex>
#include <algorithm>
#include <cmath>
using namespace std;

static const int MAXN = 32;
struct G {
    int n; uint32_t adj[MAXN];
    void clear(int n_){ n=n_; memset(adj,0,sizeof(adj)); }
    bool has(int u,int v) const { return (adj[u]>>v)&1; }
    void add(int u,int v){ adj[u]|=1u<<v; adj[v]|=1u<<u; }
    void del(int u,int v){ adj[u]&=~(1u<<v); adj[v]&=~(1u<<u); }
    int deg(int u) const { return __builtin_popcount(adj[u]); }
};

// 3-colorability via DFS on vertices ordered by degree (simple, fast for n<=20)
static bool col3(const G&g, uint32_t removedMask, int eu=-1, int ev=-1){
    int idx[MAXN], m=0;
    for(int v=0;v<g.n;v++) if(!((removedMask>>v)&1)) idx[m++]=v;
    // order by degree desc (static order fine)
    for(int i=1;i<m;i++){int k=idx[i],j=i-1;while(j>=0&&g.deg(idx[j])<g.deg(k)){idx[j+1]=idx[j];j--;}idx[j+1]=k;}
    int8_t color[MAXN]; memset(color,-1,sizeof(color));
    // iterative DFS
    int pos=0; int8_t tryc[MAXN]; memset(tryc,0,sizeof(tryc));
    while(pos>=0){
        if(pos==m) return true;
        int v=idx[pos];
        bool advanced=false;
        for(int c=tryc[pos];c<3;c++){
            bool ok=true;
            uint32_t nb=g.adj[v];
            while(nb){ int u=__builtin_ctz(nb); nb&=nb-1;
                if(((removedMask>>u)&1)) continue;
                if(eu>=0 && ((u==eu&&v==ev)||(u==ev&&v==eu))) continue; // removed edge
                if(color[u]==c){ ok=false; break; } }
            if(ok){ color[v]=c; tryc[pos]=c+1; pos++; if(pos<m) tryc[pos]=0; advanced=true; break; }
        }
        if(!advanced){ color[v]=-1; tryc[pos]=0; pos--; if(pos>=0){} }
    }
    return false;
}

static long long objective(const G&g, int&critEdges, int&badVerts, bool&g3col){
    g3col = col3(g, 0);
    long long obj = 0;
    if(g3col){ critEdges=-1; badVerts=-1; return 1000000; }
    badVerts=0;
    for(int v=0; v<g.n; v++) if(!col3(g, 1u<<v)) badVerts++;
    critEdges=0;
    for(int u=0;u<g.n;u++) for(int v=u+1;v<g.n;v++) if(g.has(u,v))
        if(col3(g, 0, u, v)) critEdges++;
    obj = (long long)badVerts*50 + critEdges;
    return obj;
}

static mutex outmx;
static atomic<bool> found(false);

static void worker(int n, unsigned seed, double targetEdgeFrac){
    mt19937 rng(seed);
    G g; g.clear(n);
    // init: random graph around target density with delta>=3
    int target=(int)(targetEdgeFrac*n*(n-1)/2);
    vector<pair<int,int>> all;
    for(int u=0;u<n;u++)for(int v=u+1;v<n;v++) all.push_back({u,v});
    shuffle(all.begin(), all.end(), rng);
    for(int i=0;i<target && i<(int)all.size();i++) g.add(all[i].first, all[i].second);
    int ce,bv; bool c3;
    long long cur = objective(g,ce,bv,c3);
    long long best=cur; int bce=ce,bbv=bv;
    double T=8.0;
    for(long long it=0; it<6000000 && !found.load(); it++){
        if((it&1023)==0){ T*=0.999; if(T<0.05){ T=8.0; } }
        // move: 60% single flip, 40% swap (del one existing + add one missing)
        G save=g;
        if(rng()%10<4){
            int tries=0; int du=-1,dv=-1,au=-1,av=-1;
            while(tries++<50){ int u=rng()%n,v=rng()%n; if(u!=v&&g.has(u,v)&&g.deg(u)>3&&g.deg(v)>3){du=u;dv=v;break;} }
            while(tries++<100){ int u=rng()%n,v=rng()%n; if(u!=v&&!g.has(u,v)){au=u;av=v;break;} }
            if(du<0||au<0) continue;
            g.del(du,dv); g.add(au,av);
        } else {
            int u=rng()%n, v=rng()%n; if(u==v) continue;
            bool had=g.has(u,v);
            if(had){ if(g.deg(u)<=3||g.deg(v)<=3) continue; g.del(u,v); } else g.add(u,v);
        }
        int ce2,bv2; bool c32;
        long long nxt = objective(g,ce2,bv2,c32);
        if(nxt<=cur || exp((cur-nxt)/T) > uniform_real_distribution<double>(0,1)(rng)){
            cur=nxt; ce=ce2; bv=bv2; c3=c32;
            if(cur<best){best=cur;bce=ce;bbv=bv;}
            if(cur==0){
                found.store(true);
                lock_guard<mutex> lk(outmx);
                printf("FOUND n=%d seed=%u\n", n, seed);
                printf("edges:");
                for(int a=0;a<n;a++)for(int b=a+1;b<n;b++) if(g.has(a,b)) printf(" %d-%d",a,b);
                printf("\n"); fflush(stdout);
                return;
            }
        } else { g=save; }
    }
    lock_guard<mutex> lk(outmx);
    printf("n=%d seed=%u best-ish: obj=%lld badV=%d critE=%d%s\n", n, seed, cur, bv, ce, c3?" (3col!)":"");
    fflush(stdout);
}

int main(int argc, char**argv){
    int nlo = argc>1?atoi(argv[1]):11, nhi = argc>2?atoi(argv[2]):16;
    int threads = argc>3?atoi(argv[3]):32;
    vector<thread> ts;
    unsigned s0=12345;
    int per = threads/(nhi-nlo+1)+1;
    for(int n=nlo;n<=nhi;n++)
        for(int i=0;i<per;i++)
            ts.emplace_back(worker, n, s0+n*1000+i, 0.30+0.02*(i%4));
    for(auto&t:ts) t.join();
    return 0;
}
