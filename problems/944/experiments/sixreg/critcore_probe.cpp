// critcore_probe.cpp -- dense-core probe for R3-prime avenue B.
// Input: graph6 lines (geng -c -d3 -D6 n lo:hi). For each 4-CRITICAL graph
// (chi>=4 and every edge-deletion 3-colourable) with Delta<=6:
//   for each vertex z* and each split N(z*) = A | B (both nonempty, unordered):
//     J := split graph (z1 keeps A, new vertex z2 gets B). If J 3-colourable:
//     for each w != z* with deg(w)==6: "dead" if NO proper 3-colouring of J-w
//     has trace (2,2,2) on N_J(w).  A split is ALIVE if no deg-6 vertex is dead.
// Any counterexample to R3-prime that contains this core as its forced-difference
// witness must use an ALIVE split (deg-6 core vertices cannot be padded).
// Output: per-graph summary + tallies.
// Build: clang++ -O2 -std=c++17 -pthread critcore_probe.cpp -o critcore_probe.exe
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
#include <atomic>
#include <thread>
#include <mutex>
#include <algorithm>
using namespace std;

struct Graph { uint32_t adj[32]; int n; };

static bool parse_g6(const char* s, Graph& g){
    int n=s[0]-63; if(n<1||n>31) return false;
    g.n=n; for(int i=0;i<n;i++) g.adj[i]=0;
    const char* p=s+1; int val=0,have=0;
    for(int y=1;y<n;y++) for(int x=0;x<y;x++){
        if(have==0){ val=*p++-63; have=6; }
        have--;
        if((val>>have)&1){ g.adj[x]|=1u<<y; g.adj[y]|=1u<<x; }
    }
    return true;
}

// generic 3-colouring enumeration over vertex mask, cb -> false aborts
template<class F>
static void enum_col(const Graph& g, uint32_t verts, F&& cb){
    int order[32],m=0;
    for(int v=0;v<g.n;v++) if(verts>>v&1) order[m++]=v;
    int degs[32];
    for(int i=0;i<m;i++){int v=order[i];degs[v]=__builtin_popcount(g.adj[v]&verts);}
    sort(order,order+m,[&](int a,int b){return degs[a]>degs[b];});
    int8_t col[32]; memset(col,-1,sizeof col);
    struct R{
        const Graph&g; uint32_t verts; int m; int*order; int8_t*col; F&cb; bool ab=false;
        R(const Graph&g_,uint32_t v_,int m_,int*o_,int8_t*c_,F&cb_):g(g_),verts(v_),m(m_),order(o_),col(c_),cb(cb_){}
        void go(int i,int mu){
            if(ab) return;
            if(i==m){ if(!cb(col)) ab=true; return; }
            int v=order[i]; uint32_t nb=g.adj[v]&verts; int used=0;
            uint32_t t=nb; while(t){int u=__builtin_ctz(t);t&=t-1;if(col[u]>=0)used|=1<<col[u];}
            int cm=min(2,mu+1);
            for(int c=0;c<=cm;c++){
                if(used>>c&1) continue;
                col[v]=c; go(i+1,max(mu,c)); col[v]=-1;
                if(ab) return;
            }
        }
    } r(g,verts,m,order,col,cb);
    r.go(0,-1);
}

static bool colourable(const Graph& g, uint32_t verts){
    bool found=false;
    enum_col(g,verts,[&](const int8_t*)->bool{found=true;return false;});
    return found;
}

static mutex out_mtx;
struct Tally{
    uint64_t graphs=0, crit=0, critWithDeg6=0;
    uint64_t splits=0, splitsCol=0, aliveSplits=0, aliveSplitsBig=0;
    uint64_t graphsWithAlive=0, graphsWithAliveBig=0;
    int maxDeg6=0;
};

static void process(const Graph& g, Tally& t, const string& line){
    t.graphs++;
    int n=g.n;
    uint32_t all=(1u<<n)-1;
    if(colourable(g,all)) return;            // chi>=4 required
    // edge-criticality: every edge deletion 3-colourable
    Graph h=g;
    for(int x=0;x<n;x++) for(int y=x+1;y<n;y++){
        if(!(g.adj[x]>>y&1)) continue;
        h.adj[x]&=~(1u<<y); h.adj[y]&=~(1u<<x);
        bool ok=colourable(h,all);
        h.adj[x]|=1u<<y; h.adj[y]|=1u<<x;
        if(!ok) return;                       // not critical
    }
    t.crit++;
    int deg6cnt=0; for(int v=0;v<n;v++) if(__builtin_popcount(g.adj[v])==6) deg6cnt++;
    t.maxDeg6=max(t.maxDeg6,deg6cnt);
    if(deg6cnt>0) t.critWithDeg6++;
    bool anyAlive=false, anyAliveBig=false;
    // splits
    Graph J; // n+1 vertices, z1=z*, z2=n
    for(int z=0;z<n;z++){
        uint32_t nb=g.adj[z];
        int d=__builtin_popcount(nb);
        if(d<2) continue;
        int nbl[8],dd=0; uint32_t tt=nb; while(tt){nbl[dd++]=__builtin_ctz(tt);tt&=tt-1;}
        int lowest=nbl[0];
        for(uint32_t Smask=1;Smask<(1u<<d)-1u;Smask++){
            if(!(Smask&1)) continue;          // lowest neighbour stays with z1 (unordered split)
            t.splits++;
            // build J
            J.n=n+1;
            for(int v=0;v<n;v++) J.adj[v]=g.adj[v];
            J.adj[n]=0;
            for(int i=0;i<d;i++){
                if(Smask>>i&1) continue;       // stays at z1
                int u=nbl[i];                  // moves to z2
                J.adj[z]&=~(1u<<u); J.adj[u]&=~(1u<<z);
                J.adj[n]|=1u<<u;  J.adj[u]|=1u<<n;
            }
            uint32_t allJ=(1u<<(n+1))-1;
            if(!colourable(J,allJ)) continue;
            t.splitsCol++;
            // dead test on deg-6 vertices (other than z; z1 has reduced degree)
            bool alive=true;
            for(int w=0;w<n && alive;w++){
                if(w==z) continue;
                if(__builtin_popcount(g.adj[w])!=6) continue;
                uint32_t nbw=J.adj[w];
                bool wit=false;
                enum_col(J, allJ&~(1u<<w), [&](const int8_t* col)->bool{
                    int c0=0,c1=0,c2=0; uint32_t b=nbw;
                    while(b){int u=__builtin_ctz(b);b&=b-1;
                        if(col[u]==0)c0++; else if(col[u]==1)c1++; else c2++;}
                    if(c0==2&&c1==2&&c2==2){wit=true;return false;}
                    return true;
                });
                if(!wit) alive=false;          // dead deg-6 vertex kills the split
            }
            if(alive){
                t.aliveSplits++; anyAlive=true;
                if(deg6cnt>=3){
                    t.aliveSplitsBig++; anyAliveBig=true;
                    lock_guard<mutex> lk(out_mtx);
                    printf("ALIVE-BIG %s deg6=%d z=%d Smask=%u\n",line.c_str(),deg6cnt,z,Smask);
                    fflush(stdout);
                }
            }
        }
        (void)lowest;
    }
    if(anyAlive) t.graphsWithAlive++;
    if(anyAliveBig) t.graphsWithAliveBig++;
    if(deg6cnt>0){
        lock_guard<mutex> lk(out_mtx);
        printf("CRIT %s n=%d deg6=%d alive=%d\n",line.c_str(),n,deg6cnt,(int)anyAlive);
    }
}

int main(int argc,char**argv){
    int nth = argc>1?atoi(argv[1]):32;
    vector<string> lines;
    { char buf[256];
      while(fgets(buf,sizeof buf,stdin)){
          size_t L=strlen(buf);
          while(L&&(buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
          if(L) lines.emplace_back(buf,L);
      } }
    fprintf(stderr,"read %zu graphs\n",lines.size());
    atomic<size_t> next(0);
    vector<Tally> ts(nth);
    vector<thread> th;
    for(int t=0;t<nth;t++) th.emplace_back([&,t]{
        Graph g;
        for(;;){
            size_t i=next.fetch_add(64);
            if(i>=lines.size()) break;
            size_t e=min(lines.size(),i+64);
            for(size_t j=i;j<e;j++) if(parse_g6(lines[j].c_str(),g)) process(g,ts[t],lines[j]);
        }
    });
    for(auto&x:th) x.join();
    Tally tot; for(auto&x:ts){
        tot.graphs+=x.graphs; tot.crit+=x.crit; tot.critWithDeg6+=x.critWithDeg6;
        tot.splits+=x.splits; tot.splitsCol+=x.splitsCol; tot.aliveSplits+=x.aliveSplits;
        tot.aliveSplitsBig+=x.aliveSplitsBig; tot.graphsWithAlive+=x.graphsWithAlive;
        tot.graphsWithAliveBig+=x.graphsWithAliveBig; tot.maxDeg6=max(tot.maxDeg6,x.maxDeg6);
    }
    printf("graphs=%llu fourCritical=%llu critWithDeg6=%llu maxDeg6=%d splits=%llu "
           "splitsColourable=%llu aliveSplits=%llu graphsWithAlive=%llu "
           "aliveSplitsDeg6ge3=%llu graphsWithAliveDeg6ge3=%llu\n",
        (unsigned long long)tot.graphs,(unsigned long long)tot.crit,
        (unsigned long long)tot.critWithDeg6,tot.maxDeg6,
        (unsigned long long)tot.splits,(unsigned long long)tot.splitsCol,
        (unsigned long long)tot.aliveSplits,(unsigned long long)tot.graphsWithAlive,
        (unsigned long long)tot.aliveSplitsBig,(unsigned long long)tot.graphsWithAliveBig);
    return 0;
}
