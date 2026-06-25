// r3prime_scan.cpp -- exhaustive R3-prime check on small graphs.
// Input: graph6 lines on stdin (geng -c -D6 n e:e), n <= 31.
// For each graph with total deficiency 6 (e = 3n-3 guaranteed by caller):
//   * enumerate proper 3-colourings (colour-symmetry reduced),
//   * find deficient non-triangle triples that are rainbow in EVERY colouring,
//   * if any exist ("instance"): for each full vertex v test frozenness:
//       no proper 3-colouring of G-v with trace (2,2,2) on N(v).
//   * counterexample = instance where EVERY full vertex is unfrozen.
// Output: tallies + any counterexamples (g6 + triple), per-thread aggregated.
// Build: clang++ -O2 -std=c++17 -pthread r3prime_scan.cpp -o r3prime_scan.exe
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
#include <atomic>
#include <thread>
#include <mutex>
#include <algorithm>
#include <array>
using namespace std;

static int N;                       // vertices (fixed per run)
struct Tally {
    uint64_t graphs=0, threecol=0, instances=0, withFrozen=0, counterex=0;
    uint64_t tripleCount=0;         // total rigid non-triangle deficient triples
    uint64_t minFrozenFull=UINT64_MAX, maxFrozenFull=0;
};

struct Graph {
    uint32_t adj[31];
    int n;
};

static bool parse_g6(const char* s, Graph& g){
    int n = s[0]-63;
    if(n<1||n>31) return false;
    g.n=n;
    for(int i=0;i<n;i++) g.adj[i]=0;
    int bitpos=0;
    const char* p=s+1;
    int need = n*(n-1)/2;
    int val=0, have=0;
    for(int y=1;y<n;y++) for(int x=0;x<y;x++){
        if(have==0){ val=*p++-63; have=6; }
        have--;
        if((val>>have)&1){ g.adj[x]|=1u<<y; g.adj[y]|=1u<<x; }
        bitpos++;
    }
    (void)bitpos;(void)need;
    return true;
}

// enumerate proper 3-colourings of the graph restricted to mask 'verts'
// callback returns false to abort enumeration.
template<class F>
static void enum_colourings(const Graph& g, uint32_t verts, F&& cb, bool symReduce){
    int order[31], m=0;
    for(int v=0;v<g.n;v++) if(verts>>v&1) order[m++]=v;
    // order by degree desc within the induced graph for better pruning
    int degs[31];
    for(int i=0;i<m;i++){ int v=order[i]; degs[v]=__builtin_popcount(g.adj[v]&verts); }
    sort(order, order+m, [&](int a,int b){return degs[a]>degs[b];});
    int8_t col[31];
    memset(col,-1,sizeof col);
    bool aborted=false;
    // iterative-recursive backtracking
    struct Rec {
        const Graph& g; uint32_t verts; int m; int* order; int8_t* col;
        F& cb; bool symReduce; bool aborted=false;
        Rec(const Graph& g_, uint32_t v_, int m_, int* o_, int8_t* c_, F& cb_, bool s_)
            :g(g_),verts(v_),m(m_),order(o_),col(c_),cb(cb_),symReduce(s_){}
        void go(int i, int maxused){
            if(aborted) return;
            if(i==m){ if(!cb(col)) aborted=true; return; }
            int v=order[i];
            uint32_t nb=g.adj[v]&verts;
            int used=0; // colours used by coloured neighbours
            uint32_t tmp=nb;
            while(tmp){ int u=__builtin_ctz(tmp); tmp&=tmp-1; if(col[u]>=0) used|=1<<col[u]; }
            int cmax = symReduce ? min(2,maxused+1) : 2;
            for(int c=0;c<=cmax;c++){
                if(used>>c&1) continue;
                col[v]=c;
                go(i+1, max(maxused, c));
                col[v]=-1;
                if(aborted) return;
            }
        }
    } rec(g, verts, m, order, col, cb, symReduce);
    rec.go(0,-1);
    (void)aborted;
}

static mutex out_mtx;

static void process(const Graph& g, Tally& t, const string& g6line){
    t.graphs++;
    int n=g.n;
    uint32_t full=0, defi=0;
    for(int v=0;v<n;v++){
        int d=__builtin_popcount(g.adj[v]);
        if(d==6) full|=1u<<v; else defi|=1u<<v;
    }
    // candidate triples: 3 deficient vertices, at least one non-adjacent pair
    int dv[8], nd=0;
    uint32_t tmp=defi; while(tmp){ dv[nd++]=__builtin_ctz(tmp); tmp&=tmp-1; }
    if(nd<3) return; // cannot prescribe 3 deficient anchors
    vector<array<int,3>> trip;
    for(int i=0;i<nd;i++)for(int j=i+1;j<nd;j++)for(int k=j+1;k<nd;k++){
        int a=dv[i],b=dv[j],c=dv[k];
        bool ab=g.adj[a]>>b&1, ac=g.adj[a]>>c&1, bc=g.adj[b]>>c&1;
        if(ab&&ac&&bc) continue;          // triangle => out of scope
        trip.push_back({a,b,c});
    }
    if(trip.empty()) return;
    // enumerate colourings; kill triples that are ever non-rainbow
    vector<char> alive(trip.size(),1);
    int aliveCnt=(int)trip.size();
    uint64_t ncol=0;
    uint32_t all=(n==31)?0x7fffffffu:((1u<<n)-1);
    enum_colourings(g, all, [&](const int8_t* col)->bool{
        ncol++;
        for(size_t s=0;s<trip.size();s++){
            if(!alive[s]) continue;
            int a=trip[s][0],b=trip[s][1],c=trip[s][2];
            if(col[a]==col[b]||col[a]==col[c]||col[b]==col[c]){
                alive[s]=0; aliveCnt--;
            }
        }
        return aliveCnt>0;  // abort once no triple can be rigid
    }, true);
    if(ncol==0) return;       // not 3-colourable
    t.threecol++;
    if(aliveCnt==0) return;   // no rigid non-triangle deficient triple
    t.instances++;
    t.tripleCount += aliveCnt;
    // freezing census over full vertices
    int frozenCnt=0;
    int fullCnt=__builtin_popcount(full);
    uint32_t fm=full;
    while(fm){
        int v=__builtin_ctz(fm); fm&=fm-1;
        uint32_t verts=all & ~(1u<<v);
        uint32_t nb=g.adj[v];
        bool witness=false;
        enum_colourings(g, verts, [&](const int8_t* col)->bool{
            int cnt[3]={0,0,0};
            uint32_t b=nb;
            while(b){ int u=__builtin_ctz(b); b&=b-1; cnt[col[u]]++; }
            if(cnt[0]==2&&cnt[1]==2&&cnt[2]==2){ witness=true; return false; }
            return true;
        }, true);
        if(!witness) frozenCnt++;
    }
    if(frozenCnt>0) t.withFrozen++;
    t.minFrozenFull=min<uint64_t>(t.minFrozenFull,frozenCnt);
    t.maxFrozenFull=max<uint64_t>(t.maxFrozenFull,frozenCnt);
    if(frozenCnt==0){
        t.counterex++;
        lock_guard<mutex> lk(out_mtx);
        printf("COUNTEREXAMPLE %s fullCnt=%d triples:", g6line.c_str(), fullCnt);
        for(size_t s=0;s<trip.size();s++) if(alive[s])
            printf(" (%d,%d,%d)",trip[s][0],trip[s][1],trip[s][2]);
        printf("\n"); fflush(stdout);
    }
}

int main(int argc,char**argv){
    int nthreads = argc>1 ? atoi(argv[1]) : 32;
    // read all lines
    vector<string> lines;
    {
        char buf[256];
        while(fgets(buf,sizeof buf,stdin)){
            size_t L=strlen(buf);
            while(L&&(buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
            if(L) lines.emplace_back(buf,L);
        }
    }
    fprintf(stderr,"read %zu graphs\n",lines.size());
    atomic<size_t> next(0);
    vector<Tally> tallies(nthreads);
    vector<thread> th;
    for(int t=0;t<nthreads;t++) th.emplace_back([&,t]{
        Graph g;
        for(;;){
            size_t i=next.fetch_add(256);
            if(i>=lines.size()) break;
            size_t end=min(lines.size(), i+256);
            for(size_t j=i;j<end;j++){
                if(parse_g6(lines[j].c_str(),g)) process(g,tallies[t],lines[j]);
            }
        }
    });
    for(auto&x:th) x.join();
    Tally tot;
    tot.minFrozenFull=UINT64_MAX;
    for(auto&t:tallies){
        tot.graphs+=t.graphs; tot.threecol+=t.threecol; tot.instances+=t.instances;
        tot.withFrozen+=t.withFrozen; tot.counterex+=t.counterex; tot.tripleCount+=t.tripleCount;
        tot.minFrozenFull=min(tot.minFrozenFull,t.minFrozenFull);
        tot.maxFrozenFull=max(tot.maxFrozenFull,t.maxFrozenFull);
    }
    printf("graphs=%llu threecol=%llu rigidInstances=%llu rigidTriples=%llu withFrozen=%llu "
           "counterexamples=%llu minFrozen=%lld maxFrozen=%llu\n",
        (unsigned long long)tot.graphs,(unsigned long long)tot.threecol,
        (unsigned long long)tot.instances,(unsigned long long)tot.tripleCount,
        (unsigned long long)tot.withFrozen,(unsigned long long)tot.counterex,
        tot.instances? (long long)tot.minFrozenFull : -1,
        (unsigned long long)tot.maxFrozenFull);
    return 0;
}
