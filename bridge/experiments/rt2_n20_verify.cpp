// RED TEAM 2: exact H2 verification for explicit N=20 (n=4, target 2n-1=7) candidates.
// For each candidate edge list: check triangle-free, compute beta = E - MaxCut (exact, 2^20),
// then min over all C(20,5)=15504 5-sets of [beta(G) - beta(G-S)] via exact MaxCut on 15 vtx.
// A counterexample = triangle-free, beta>=band, min_drop > 7.
// Build: clang++ -O3 -std=c++17 rt2_n20_verify.cpp -o rt2_n20_verify.exe
#include <cstdio>
#include <cstdint>
#include <vector>
#include <string>
#include <array>
#include <algorithm>

static const int N = 20;
static const int TARGET = 7;   // 2n-1, n=4

typedef uint32_t Mask;   // up to 20 bits
static inline int popc(unsigned x){ return __builtin_popcount(x); }

struct Graph { std::array<Mask,20> adj{}; int E=0; std::string name; };

static bool triangleFree(const Graph&g){
    for(int u=0;u<N;u++){ Mask a=g.adj[u]&(~((1u<<(u+1))-1));
        while(a){ int v=__builtin_ctz(a); a&=a-1; if(g.adj[u]&g.adj[v]) return false; } }
    return true;
}

// MaxCut on induced subgraph given by verts[0..m-1]. Fix verts[0] to side 0 => 2^(m-1).
static int maxcut_induced(const Graph&g,const int*verts,int m,int&Eout){
    if(m<=1){ Eout=0; return 0; }
    int idx[20]; for(int i=0;i<20;i++) idx[i]=-1;
    for(int i=0;i<m;i++) idx[verts[i]]=i;
    uint32_t badj[20]={0}; int E=0;
    for(int i=0;i<m;i++){ int v=verts[i]; Mask a=g.adj[v];
        while(a){ int w=__builtin_ctz(a); a&=a-1; if(idx[w]>=0 && w>v){ badj[idx[w]]|=(1u<<i); badj[i]|=(1u<<idx[w]); E++; } } }
    Eout=E;
    int best=0; long lim=1L<<(m-1);
    for(long half=0; half<lim; half++){
        uint32_t side1 = (uint32_t)(half<<1);
        int cut=0; uint32_t x=side1;
        while(x){ int v=__builtin_ctz(x); x&=x-1; cut+=popc(badj[v]&~side1); }
        if(cut>best) best=cut;
    }
    return best;
}

static int beta_full(const Graph&g){
    int verts[20]; for(int i=0;i<20;i++) verts[i]=i;
    int E; int mc=maxcut_induced(g,verts,20,E); return E-mc;
}
static int beta_minus5(const Graph&g,const std::array<int,5>&S){
    int verts[15]; int k=0; bool in[20]={false}; for(int i=0;i<5;i++) in[S[i]]=true;
    for(int i=0;i<20;i++) if(!in[i]) verts[k++]=i;
    int E; int mc=maxcut_induced(g,verts,15,E); return E-mc;
}

static int min5drop(const Graph&g,int bG,std::array<int,5>&argmin){
    int mn=999;
    std::array<int,5> S;
    for(S[0]=0;S[0]<N;S[0]++)
    for(S[1]=S[0]+1;S[1]<N;S[1]++)
    for(S[2]=S[1]+1;S[2]<N;S[2]++)
    for(S[3]=S[2]+1;S[3]<N;S[3]++)
    for(S[4]=S[3]+1;S[4]<N;S[4]++){
        int d = bG - beta_minus5(g,S);
        if(d<mn){ mn=d; argmin=S; }
    }
    return mn;
}

static Graph mk(const std::string&name, const std::vector<std::pair<int,int>>&edges){
    Graph g; g.name=name;
    for(auto&e:edges){ int u=e.first,v=e.second; if(!(g.adj[u]&(1u<<v))){ g.adj[u]|=(1u<<v); g.adj[v]|=(1u<<u); g.E++; } }
    return g;
}

// circulant edges
static std::vector<std::pair<int,int>> circ(int n, std::vector<int> gens){
    std::vector<int> S;
    for(int gg:gens){ S.push_back(((gg%n)+n)%n); S.push_back(((-gg%n)+n)%n); }
    std::vector<std::pair<int,int>> E;
    for(int v=0; v<n; v++) for(int s:S){ if(s==0) continue; int w=(v+s)%n; int a=std::min(v,w),b=std::max(v,w); E.push_back({a,b}); }
    return E;
}

int main(){
    std::vector<Graph> C;

    // --- vertex-transitive circulants on Z20 (triangle-free, degree 6) ---
    C.push_back(mk("Cay(Z20,{1,4,9})", circ(20,{1,4,9})));
    C.push_back(mk("Cay(Z20,{1,5,8})", circ(20,{1,5,8})));
    C.push_back(mk("Cay(Z20,{2,5,9})", circ(20,{2,5,9})));
    C.push_back(mk("Cay(Z20,{1,3,7})", circ(20,{1,3,7})));
    C.push_back(mk("Cay(Z20,{1,4,7})", circ(20,{1,4,7})));
    C.push_back(mk("Cay(Z20,{3,4,9})", circ(20,{3,4,9})));
    C.push_back(mk("Cay(Z20,{1,6,9})", circ(20,{1,6,9})));
    // degree 4 sparser circulants
    C.push_back(mk("Cay(Z20,{1,8})", circ(20,{1,8})));
    C.push_back(mk("Cay(Z20,{3,8})", circ(20,{3,8})));
    C.push_back(mk("Cay(Z20,{2,9})", circ(20,{2,9})));
    C.push_back(mk("Cay(Z20,{1,9})", circ(20,{1,9})));

    // --- C5[4] reference (extremal, should be tight margin 0) ---
    {
        std::vector<std::pair<int,int>> e;
        int n4=4;
        for(int p=0;p<5;p++){ int q=(p+1)%5; for(int j=0;j<n4;j++) for(int k=0;k<n4;k++) e.push_back({p*n4+j,q*n4+k}); }
        C.push_back(mk("C5[4] (ref tight)", e));
    }

    // --- C5[3] + 5-vertex C5 blob: a C5[3] on 0..14 plus a C5 on 15..19 cross-linked ---
    {
        std::vector<std::pair<int,int>> e;
        int n3=3;
        for(int p=0;p<5;p++){ int q=(p+1)%5; for(int j=0;j<n3;j++) for(int k=0;k<n3;k++) e.push_back({p*n3+j,q*n3+k}); }
        // extra C5 on 15..19
        for(int i=0;i<5;i++) e.push_back({15+i, 15+(i+1)%5});
        // attach blob's vertex 15+i to part i (size-3 group) of C5[3] in a tri-free way:
        // connect 15+i to the single vertex part[(i+2)%5][0] (a non-adjacent part) -- keep tri-free
        for(int i=0;i<5;i++){ int part=(i+2)%5; e.push_back({15+i, part*n3+0}); }
        C.push_back(mk("C5[3]+C5blob", e));
    }

    // --- two interleaved C5[2]: a "double pentagon prism" style. Take C5[2] (10 vtx) on 0..9
    //     and another C5[2] on 10..19, joined by a matching to entangle odd structure ---
    {
        std::vector<std::pair<int,int>> e;
        int n2=2;
        for(int p=0;p<5;p++){ int q=(p+1)%5; for(int j=0;j<n2;j++) for(int k=0;k<n2;k++) e.push_back({p*n2+j,q*n2+k}); }
        // second copy shifted by 10
        for(int p=0;p<5;p++){ int q=(p+1)%5; for(int j=0;j<n2;j++) for(int k=0;k<n2;k++) e.push_back({10+p*n2+j,10+q*n2+k}); }
        C.push_back(mk("C5[2] disjoint x2", e));
    }

    // --- 4 disjoint C5 (max odd-cycle packing on 20 vtx) ---
    {
        std::vector<std::pair<int,int>> e;
        for(int b=0;b<4;b++) for(int i=0;i<5;i++) e.push_back({b*5+i, b*5+(i+1)%5});
        C.push_back(mk("4x disjoint C5", e));
    }
    // --- C5[4] minus one cross edge (probe rigidity of the tight extremal) ---
    {
        std::vector<std::pair<int,int>> e; int n4=4;
        for(int p=0;p<5;p++){ int q=(p+1)%5; for(int j=0;j<n4;j++) for(int k=0;k<n4;k++){ if(p==0&&j==0&&q==1&&k==0) continue; e.push_back({p*n4+j,q*n4+k}); } }
        C.push_back(mk("C5[4] minus 1 edge", e));
    }
    // --- Petersen blown up by 2 (20 vtx, tri-free, non-C5-hom core) ---
    {
        int PE[15][2]={{0,1},{1,2},{2,3},{3,4},{4,0},{5,7},{7,9},{9,6},{6,8},{8,5},{0,5},{1,6},{2,7},{3,8},{4,9}};
        std::vector<std::pair<int,int>> e;
        for(auto&p:PE) for(int a=0;a<2;a++) for(int b=0;b<2;b++) e.push_back({p[0]*2+a, p[1]*2+b});
        C.push_back(mk("Petersen[2] blowup", e));
    }

    // --- Desargues graph (20 vtx, bipartite, tri-free, vertex-transitive) ---
    // generalized Petersen GP(10,3): outer C10 0..9, inner 10..19 with step 3, spokes.
    {
        std::vector<std::pair<int,int>> e;
        for(int i=0;i<10;i++) e.push_back({i,(i+1)%10});          // outer C10
        for(int i=0;i<10;i++) e.push_back({10+i, 10+(i+3)%10});   // inner step-3
        for(int i=0;i<10;i++) e.push_back({i, 10+i});            // spokes
        C.push_back(mk("Desargues GP(10,3)", e));
    }

    // --- Dodecahedron graph (20 vtx, 3-regular, girth 5, vertex-transitive, tri-free) ---
    {
        // standard dodecahedron adjacency (0-indexed), 30 edges
        int de[30][2]={
            {0,1},{0,4},{0,5},{1,2},{1,6},{2,3},{2,7},{3,4},{3,8},{4,9},
            {5,10},{5,14},{6,10},{6,11},{7,11},{7,12},{8,12},{8,13},{9,13},{9,14},
            {10,15},{11,16},{12,17},{13,18},{14,19},{15,16},{15,19},{16,17},{17,18},{18,19}};
        std::vector<std::pair<int,int>> e;
        for(auto&x:de) e.push_back({x[0],x[1]});
        C.push_back(mk("Dodecahedron", e));
    }

    // --- Desargues-like + chords? keep to clean ones. Kneser/odd-graph not 20 vtx. ---

    printf("RED TEAM 2 -- H2 verification N=20 (n=4, target 2n-1=%d)\n", TARGET);
    printf("%-22s %5s %4s %6s %8s %7s  %s\n","name","E","beta","trifree","min_drop","margin","verdict");
    for(auto&g:C){
        bool tf=triangleFree(g);
        if(!tf){ printf("%-22s %5d  ---  %6s   --       --      INVALID(triangle)\n", g.name.c_str(), g.E, "NO"); continue; }
        int bG=beta_full(g);
        std::array<int,5> arg;
        int mn=min5drop(g,bG,arg);
        int margin=mn-TARGET;
        const char* verdict = margin>0 ? "*** H2 VIOLATION ***" : "H2 holds";
        printf("%-22s %5d  %3d  %6s   %2d       %+d      %s", g.name.c_str(), g.E, bG, "YES", mn, margin, verdict);
        if(margin>0) printf("  argmin=[%d,%d,%d,%d,%d]",arg[0],arg[1],arg[2],arg[3],arg[4]);
        printf("\n");
        fflush(stdout);
    }
    return 0;
}
