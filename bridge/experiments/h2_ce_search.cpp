// H2 counterexample search at n=3 (N=15), native multithreaded.
//
// H2 (n=3): every triangle-free G on 15 vtx admits a 5-set S with
//   beta(G) - beta(G-S) <= 2n-1 = 5.   (trivial when beta<=5)
// A COUNTEREXAMPLE = triangle-free, beta>=6, with min over all C(15,5) 5-sets of
//   [beta(G)-beta(G-S)]  > 5.
//
// beta = E - MaxCut, MaxCut by exact brute force (fix vtx0, iterate 2^(m-1)).
// Generators: all C5-blowup compositions, random-maximal triangle-free,
// perturbation hill-climb (push beta up), and the non-C5-hom hard cores
// (Petersen+5, Grotzsch+4) + their hill-climbs. Flags ANY violation.
//
// Build: clang++ -O3 -std=c++17 -pthread h2_ce_search.cpp -o h2_ce_search.exe
#include <cstdio>
#include <cstdint>
#include <vector>
#include <array>
#include <random>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>

static const int N = 15;
static const int TARGET = 5;   // 2n-1, n=3
static const int BAND_LO = 6;

typedef uint16_t Mask;         // 15-bit vertex sets

struct Graph { std::array<Mask,15> adj{}; };

static inline int popc(unsigned x){ return __builtin_popcount(x); }

static inline bool addEdgeSafe(Graph&g,int u,int v){
    // add edge u-v iff it keeps triangle-free (no common neighbour). returns added.
    if(u==v) return false;
    if(g.adj[u]&(1u<<v)) return false;        // already present
    if(g.adj[u]&g.adj[v]) return false;       // common neighbour -> triangle
    g.adj[u]|=(1u<<v); g.adj[v]|=(1u<<u); return true;
}
static inline void delEdge(Graph&g,int u,int v){ g.adj[u]&=~(1u<<v); g.adj[v]&=~(1u<<u); }

static inline bool triangleFree(const Graph&g){
    for(int u=0;u<N;u++){ Mask a=g.adj[u]&(~((1u<<(u+1))-1)); // v>u
        while(a){ int v=__builtin_ctz(a); a&=a-1; if(g.adj[u]&g.adj[v]) return false; } }
    return true;
}

// MaxCut + edge count on induced subgraph given by vertex list `verts` (compact).
static int maxcut_induced(const Graph&g,const int*verts,int m,int&Eout){
    if(m<=1){ Eout=0; return 0; }
    // compact adjacency
    int idx[15]; for(int i=0;i<15;i++) idx[i]=-1;
    for(int i=0;i<m;i++) idx[verts[i]]=i;
    Mask badj[15]={0}; int E=0;
    for(int i=0;i<m;i++){ int v=verts[i]; Mask a=g.adj[v];
        while(a){ int w=__builtin_ctz(a); a&=a-1; if(idx[w]>=0 && w>v){ badj[idx[w]]|=(1u<<i); badj[i]|=(1u<<idx[w]); E++; } } }
    Eout=E;
    int best=0; int lim=1<<(m-1);
    for(int half=0; half<lim; half++){
        int side1 = half<<1;               // vtx0 fixed side0
        int cut=0; int x=side1;
        while(x){ int v=__builtin_ctz(x); x&=x-1; cut+=popc(badj[v]&~side1); }
        if(cut>best) best=cut;
    }
    return best;
}

static int beta_full(const Graph&g,int&Eout){
    int verts[15]; for(int i=0;i<15;i++) verts[i]=i;
    int mc=maxcut_induced(g,verts,15,Eout); return Eout-mc;
}
static int beta_minus5(const Graph&g,const std::array<int,5>&S){
    int verts[10]; int k=0; bool in[15]={false}; for(int i=0;i<5;i++) in[S[i]]=true;
    for(int i=0;i<15;i++) if(!in[i]) verts[k++]=i;
    int E; int mc=maxcut_induced(g,verts,10,E); return E-mc;
}

// returns min 5-set drop (early-exits at <=TARGET). bG passed in.
static int min5drop(const Graph&g,int bG){
    int mn=999;
    std::array<int,5> S;
    for(S[0]=0;S[0]<15;S[0]++)
    for(S[1]=S[0]+1;S[1]<15;S[1]++)
    for(S[2]=S[1]+1;S[2]<15;S[2]++)
    for(S[3]=S[2]+1;S[3]<15;S[3]++)
    for(S[4]=S[3]+1;S[4]<15;S[4]++){
        int d = bG - beta_minus5(g,S);
        if(d<mn){ mn=d; if(mn<=TARGET) return mn; }
    }
    return mn;
}

// ---- generators ----
static Graph c5_blowup(const std::array<int,5>&parts){
    Graph g; int grp[5][12]; int sz[5];
    int idx=0; for(int p=0;p<5;p++){ sz[p]=parts[p]; for(int j=0;j<parts[p];j++) grp[p][j]=idx++; }
    for(int p=0;p<5;p++){ int q=(p+1)%5; for(int a=0;a<sz[p];a++) for(int b=0;b<sz[q];b++){ int u=grp[p][a],v=grp[q][b]; g.adj[u]|=(1u<<v); g.adj[v]|=(1u<<u);} }
    return g;
}
static Graph random_maximal(std::mt19937&rng){
    Graph g; std::vector<std::pair<int,int>> pairs;
    for(int u=0;u<N;u++)for(int v=u+1;v<N;v++) pairs.push_back({u,v});
    std::shuffle(pairs.begin(),pairs.end(),rng);
    for(auto&pr:pairs) addEdgeSafe(g,pr.first,pr.second);
    return g;
}
static int beta_quick(const Graph&g){ int E; return beta_full(g,E); }

static Graph perturb(Graph g,std::mt19937&rng,int steps){
    int cur=beta_quick(g); std::uniform_int_distribution<int> vd(0,N-1);
    for(int s=0;s<steps;s++){ int u=vd(rng),v=vd(rng); if(u==v) continue;
        if(g.adj[u]&(1u<<v)){ delEdge(g,u,v); int nb=beta_quick(g); if(nb>=cur) cur=nb; else { g.adj[u]|=(1u<<v); g.adj[v]|=(1u<<u);} }
        else { if(g.adj[u]&g.adj[v]) continue; g.adj[u]|=(1u<<v); g.adj[v]|=(1u<<u); int nb=beta_quick(g); if(nb>=cur) cur=nb; else delEdge(g,u,v); } }
    return g;
}
static Graph petersen_plus5(std::mt19937&rng){
    Graph g; int PE[15][2]={{0,1},{1,2},{2,3},{3,4},{4,0},{5,7},{7,9},{9,6},{6,8},{8,5},{0,5},{1,6},{2,7},{3,8},{4,9}};
    for(auto&e:PE){ g.adj[e[0]]|=(1u<<e[1]); g.adj[e[1]]|=(1u<<e[0]); }
    std::vector<std::pair<int,int>> pairs;
    for(int x=10;x<15;x++) for(int y=0;y<15;y++) if(y!=x) pairs.push_back({std::min(x,y),std::max(x,y)});
    std::sort(pairs.begin(),pairs.end()); pairs.erase(std::unique(pairs.begin(),pairs.end()),pairs.end());
    std::shuffle(pairs.begin(),pairs.end(),rng);
    for(auto&pr:pairs) addEdgeSafe(g,pr.first,pr.second);
    return g;
}
static Graph grotzsch_plus4(std::mt19937&rng){
    Graph g; // Grotzsch = Mycielskian of C5: 0..4 C5, 5..9 shadow, 10 apex
    int C5[5][2]={{0,1},{1,2},{2,3},{3,4},{4,0}};
    for(auto&e:C5){ g.adj[e[0]]|=(1u<<e[1]); g.adj[e[1]]|=(1u<<e[0]); }
    int nbr[5][2]={{1,4},{0,2},{1,3},{2,4},{0,3}};
    for(int i=0;i<5;i++){ for(int j=0;j<2;j++){ int a=5+i,b=nbr[i][j]; g.adj[a]|=(1u<<b); g.adj[b]|=(1u<<a);} int a=5+i; g.adj[a]|=(1u<<10); g.adj[10]|=(1u<<a); }
    std::vector<std::pair<int,int>> pairs;
    for(int x=11;x<15;x++) for(int y=0;y<15;y++) if(y!=x) pairs.push_back({std::min(x,y),std::max(x,y)});
    std::sort(pairs.begin(),pairs.end()); pairs.erase(std::unique(pairs.begin(),pairs.end()),pairs.end());
    std::shuffle(pairs.begin(),pairs.end(),rng);
    for(auto&pr:pairs) addEdgeSafe(g,pr.first,pr.second);
    return g;
}

struct Res { long tested=0; int worst=-99; Graph worstG; long viol=0; std::vector<Graph> viols; int betaHist[20]={0}; };

static void consider(const Graph&g, Res&r){
    if(!triangleFree(g)) return;
    int E; int bG=beta_full(g,E);
    if(bG<BAND_LO) return;
    int mn=min5drop(g,bG);
    r.tested++; if(bG<20) r.betaHist[bG]++;
    int margin=mn-TARGET;
    if(margin>r.worst){ r.worst=margin; r.worstG=g; }
    if(margin>0){ r.viol++; if(r.viols.size()<20) r.viols.push_back(g); }
}

static void worker(int tid,int seedbase,long nrand,long nhard,Res&out){
    std::mt19937 rng(seedbase+tid*7919u);
    Res r;
    // random maximal + perturbs
    for(long i=0;i<nrand;i++){ Graph g=random_maximal(rng); consider(g,r);
        if(i%4==0){ Graph p=perturb(g,rng,180); consider(p,r); } }
    // hard cores + perturbs
    for(long i=0;i<nhard;i++){ Graph g=petersen_plus5(rng); consider(g,r);
        Graph g2=grotzsch_plus4(rng); consider(g2,r);
        if(i%3==0){ consider(perturb(g,rng,180),r); consider(perturb(g2,rng,180),r); } }
    out=r;
}

static void printGraph(const Graph&g){
    int E; int b=beta_full((Graph&)g,E);
    printf("    beta=%d E=%d edges:",b,E);
    for(int u=0;u<N;u++){ Mask a=g.adj[u]&(~((1u<<(u+1))-1)); while(a){int v=__builtin_ctz(a);a&=a-1; printf(" %d-%d",u,v);} }
    printf("\n");
}

int main(int argc,char**argv){
    int nthreads = argc>1?atoi(argv[1]):16;
    long nrand = argc>2?atol(argv[2]):20000;   // per thread
    long nhard = argc>3?atol(argv[3]):8000;    // per thread
    printf("H2 n=3 counterexample search: threads=%d nrand/thr=%ld nhard/thr=%ld\n",nthreads,nrand,nhard);
    fflush(stdout);

    // main thread: all blowup compositions (deterministic)
    Res master;
    for(int a=1;a<=11;a++)for(int b=1;b<=11;b++)for(int c=1;c<=11;c++)for(int d=1;d<=11;d++){
        int e=15-a-b-c-d; if(e<1||e>11) continue;
        consider(c5_blowup({a,b,c,d,e}),master);
    }
    printf("blowups done: tested=%ld worstMargin=%d\n",master.tested,master.worst); fflush(stdout);

    std::vector<Res> outs(nthreads);
    std::vector<std::thread> th;
    for(int t=0;t<nthreads;t++) th.emplace_back(worker,t,20260620,nrand,nhard,std::ref(outs[t]));
    for(auto&x:th) x.join();

    for(auto&r:outs){ master.tested+=r.tested; for(int i=0;i<20;i++) master.betaHist[i]+=r.betaHist[i];
        if(r.worst>master.worst){ master.worst=r.worst; master.worstG=r.worstG; }
        master.viol+=r.viol; for(auto&g:r.viols) if(master.viols.size()<20) master.viols.push_back(g); }

    printf("\n==== H2 n=3 search complete ====\n");
    printf("tested (beta>=6): %ld\n",master.tested);
    printf("beta histogram:"); for(int i=BAND_LO;i<20;i++) if(master.betaHist[i]) printf(" b%d=%d",i,master.betaHist[i]); printf("\n");
    printf("worst margin (min_drop - 5): %d   (>0 = H2 VIOLATION)\n",master.worst);
    printf("worst-case graph:\n"); printGraph(master.worstG);
    printf("# H2 violations: %ld\n",master.viol);
    for(auto&g:master.viols){ printf("  VIOLATION graph:\n"); printGraph(g); }
    return 0;
}
