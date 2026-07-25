// audit_Q3_engine.cpp -- INDEPENDENT audit engine for round7/Q3.md (pass 1 + pass 2).
// Own graph6 decoder, own exact bip (|E| - maxcut over all 2^(n-1) cuts),
// own exact dist = min_{phi:V->Z5} |E(G) symdiff E(B_phi)| by branch and bound.
// All integer arithmetic.  No floating point on any acceptance path.
//
// modes:
//   scan            : stdin g6 lines -> "g6 n m bip dist"
//   bipscan         : stdin g6 lines -> "g6 n m bip"        (no dist; fast)
//   sub  <g6> <bipTarget>   : explore ALL spanning subgraphs H of the given graph with
//                             bip(H) == bipTarget (connected under single-edge deletion,
//                             by monotonicity of bip), report max dist and a witness.
//   check           : stdin g6 lines -> verify triangle-free + maximal-triangle-free flags
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>
#include <unordered_set>
#include <unordered_map>
using namespace std;

struct Graph {
    int n = 0;
    vector<unsigned int> adj;   // bitmask rows, n <= 32
    int m = 0;
    vector<pair<int,int>> edges;
};

// ---------------- graph6 decode (written from the format description) -------
static Graph g6decode(const string &line) {
    string s = line;
    while (!s.empty() && (s.back()=='\n' || s.back()=='\r' || s.back()==' ')) s.pop_back();
    if (s.rfind(">>graph6<<",0)==0) s = s.substr(10);
    vector<int> b;
    for (char c : s) b.push_back((int)(unsigned char)c - 63);
    size_t p = 0;
    int n;
    if (b[0] <= 62) { n = b[0]; p = 1; }
    else if (b[1] <= 62) { n = (b[1]<<12) | (b[2]<<6) | b[3]; p = 4; }
    else { n = 0; for (int k=2;k<8;k++) n = (n<<6) | b[k]; p = 8; }
    Graph g; g.n = n; g.adj.assign(n,0u);
    // bit stream, column-major upper triangle: (0,1),(0,2),(1,2),(0,3),...
    long long idx = 0;
    for (int j=1;j<n;j++) for (int i=0;i<j;i++) {
        long long byteIdx = idx/6, bitIdx = idx%6;
        int bit = 0;
        if (p + byteIdx < b.size()) bit = (b[p+byteIdx] >> (5-bitIdx)) & 1;
        if (bit) { g.adj[i] |= 1u<<j; g.adj[j] |= 1u<<i; g.edges.push_back({i,j}); }
        idx++;
    }
    g.m = (int)g.edges.size();
    return g;
}

static string g6encode(int n, const vector<pair<int,int>> &edges) {
    vector<vector<char>> A(n, vector<char>(n,0));
    for (auto &e : edges) { A[e.first][e.second]=1; A[e.second][e.first]=1; }
    string out;
    out += (char)(n+63);
    vector<int> bits;
    for (int j=1;j<n;j++) for (int i=0;i<j;i++) bits.push_back(A[i][j]);
    while (bits.size()%6) bits.push_back(0);
    for (size_t k=0;k<bits.size();k+=6) {
        int v=0; for (int t=0;t<6;t++) v = (v<<1)|bits[k+t];
        out += (char)(v+63);
    }
    return out;
}

// ---------------- exact bip = |E| - maxcut over all 2^(n-1) cuts ------------
static int bip_exact(const Graph &g) {
    int n = g.n;
    unsigned int full = (n>=32)?0xffffffffu:((1u<<n)-1);
    int best = 1<<30;
    unsigned int half = 1u << (n-1);
    for (unsigned int S = 0; S < half; ++S) {
        // monochromatic count = sum over edges with both endpoints on same side
        int mono = 0;
        for (auto &e : g.edges) {
            unsigned int a = (S>>e.first)&1u, b = (S>>e.second)&1u;
            if (a==b) ++mono;
        }
        if (mono < best) best = mono;
        if (best == 0) break;
    }
    (void)full;
    return best;
}

// faster bitmask version for repeated use
static int bip_exact_fast(const Graph &g) {
    int n = g.n;
    unsigned int half = 1u << (n-1);
    int best = 1<<30;
    for (unsigned int S = 0; S < half; ++S) {
        int cut = 0;
        unsigned int T = S;
        while (T) {
            int v = __builtin_ctz(T); T &= T-1;
            cut += __builtin_popcount(g.adj[v] & ~S);
        }
        int mono = g.m - cut;
        if (mono < best) { best = mono; if (best==0) break; }
    }
    return best;
}

// ---------------- exact distance to the C5-blow-up family -------------------
// dist = min over phi : V -> Z5 of  #{uv in E : phi(u)-phi(v) != +-1} +
//                                   #{uv not in E, u!=v : phi(u)-phi(v) == +-1}
// (empty classes allowed).  Branch and bound; phi(0)=0 by rotation symmetry.
static int CONS[5][5];
struct DistBB {
    const Graph *g;
    int n;
    int best;
    vector<int> phi;
    vector<int> bestphi;
    // cost of assigning vertex k colour a against already-assigned 0..k-1
    inline int localCost(int k, int a) const {
        int c = 0;
        for (int u = 0; u < k; ++u) {
            int e = (g->adj[u] >> k) & 1u;
            if (e != CONS[phi[u]][a]) ++c;
        }
        return c;
    }
    void rec(int k, int cur) {
        if (cur >= best) return;
        if (k == n) { best = cur; bestphi = phi; return; }
        // lower bound: each unassigned vertex v>=k pays at least min over colours
        // of its cost against the assigned prefix (these contributions are disjoint)
        int lb = cur;
        for (int v = k; v < n; ++v) {
            int mv = 1<<29;
            for (int a = 0; a < 5; ++a) {
                int c = 0;
                for (int u = 0; u < k; ++u) {
                    int e = (g->adj[u] >> v) & 1u;
                    if (e != CONS[phi[u]][a]) ++c;
                }
                if (c < mv) mv = c;
            }
            lb += mv;
            if (lb >= best) return;
        }
        int lo = (k==0)?0:0, hi = (k==0)?1:5;
        vector<pair<int,int>> cand;
        for (int a = lo; a < hi; ++a) cand.push_back({localCost(k,a), a});
        sort(cand.begin(), cand.end());
        for (auto &pr : cand) {
            phi[k] = pr.second;
            rec(k+1, cur + pr.first);
        }
        phi[k] = -1;
    }
};

static int dist_exact(const Graph &g, vector<int> *witness = nullptr) {
    for (int a=0;a<5;a++) for (int b=0;b<5;b++) { int d=((a-b)%5+5)%5; CONS[a][b] = (d==1||d==4)?1:0; }
    DistBB bb; bb.g = &g; bb.n = g.n; bb.phi.assign(g.n,-1);
    // greedy upper bound: random restarts + steepest descent (heuristic only,
    // never on the acceptance path - it only seeds the exact B&B bound)
    unsigned int seed = 12345;
    auto rnd = [&]() { seed = seed*1664525u + 1013904223u; return seed; };
    int ub = 1<<29; vector<int> ubphi;
    vector<int> col(g.n);
    for (int trial = 0; trial < 300; ++trial) {
        for (int v=0;v<g.n;v++) col[v] = rnd()%5;
        bool improved = true;
        while (improved) {
            improved = false;
            for (int v=0;v<g.n;v++) {
                int bc = 1<<29, ba = col[v];
                for (int a=0;a<5;a++) {
                    int c=0;
                    for (int u=0;u<g.n;u++) if (u!=v) {
                        int e = (g.adj[u]>>v)&1u;
                        if (e != CONS[col[u]][a]) ++c;
                    }
                    if (c<bc) { bc=c; ba=a; }
                }
                if (ba != col[v]) { col[v]=ba; improved=true; }
            }
        }
        int tot=0;
        for (int u=0;u<g.n;u++) for (int v=u+1;v<g.n;v++) {
            int e=(g.adj[u]>>v)&1u;
            if (e != CONS[col[u]][col[v]]) ++tot;
        }
        if (tot<ub) { ub=tot; ubphi=col; }
    }
    bb.best = ub + 1;    // strictly above a realisable value => B&B returns the true min
    bb.bestphi = ubphi;
    bb.rec(0,0);
    if (bb.best > ub) { bb.best = ub; bb.bestphi = ubphi; }
    if (witness) *witness = bb.bestphi;
    return bb.best;
}

static bool triangle_free(const Graph &g) {
    for (auto &e : g.edges) if (g.adj[e.first] & g.adj[e.second]) return false;
    return true;
}
static bool maximal_tf(const Graph &g) {
    if (!triangle_free(g)) return false;
    for (int u=0;u<g.n;u++) for (int v=u+1;v<g.n;v++)
        if (!((g.adj[u]>>v)&1u) && !(g.adj[u]&g.adj[v])) return false;
    return true;
}

int main(int argc, char **argv) {
    ios::sync_with_stdio(false);
    string mode = (argc>1)?argv[1]:"scan";
    if (mode=="scan" || mode=="bipscan" || mode=="check") {
        string line;
        long long cnt=0, tfbad=0, mtfbad=0;
        while (getline(cin,line)) {
            if (line.empty()) continue;
            Graph g = g6decode(line);
            ++cnt;
            if (mode=="check") {
                if (!triangle_free(g)) ++tfbad;
                else if (!maximal_tf(g)) ++mtfbad;
                continue;
            }
            int b = bip_exact_fast(g);
            if (mode=="bipscan") { printf("%s\t%d\t%d\t%d\n", line.c_str(), g.n, g.m, b); }
            else {
                int d = dist_exact(g);
                printf("%s\t%d\t%d\t%d\t%d\n", line.c_str(), g.n, g.m, b, d);
            }
        }
        if (mode=="check") printf("graphs %lld  not-triangle-free %lld  tf-but-not-maximal %lld\n", cnt, tfbad, mtfbad);
        return 0;
    }
    if (mode=="sub") {
        // explore all spanning subgraphs H of G with bip(H) == target
        string g6 = argv[2];
        int target = atoi(argv[3]);
        Graph G = g6decode(g6);
        printf("base n=%d m=%d bip=%d dist=%d\n", G.n, G.m, bip_exact_fast(G), dist_exact(G));
        int M = G.m;
        // state = bitmask over edges present
        unsigned long long fullmask = (M>=64)?~0ULL:((1ULL<<M)-1);
        unordered_set<unsigned long long> seen;
        vector<unsigned long long> frontier;
        auto build = [&](unsigned long long mask) {
            Graph h; h.n = G.n; h.adj.assign(G.n,0u);
            for (int i=0;i<M;i++) if ((mask>>i)&1ULL) {
                int u=G.edges[i].first, v=G.edges[i].second;
                h.adj[u]|=1u<<v; h.adj[v]|=1u<<u; h.edges.push_back({u,v});
            }
            h.m = (int)h.edges.size();
            return h;
        };
        seen.insert(fullmask);
        frontier.push_back(fullmask);
        int bestdist = -1; unsigned long long bestmask = fullmask;
        long long explored = 0;
        int layer = 0;
        while (!frontier.empty()) {
            vector<unsigned long long> next;
            for (unsigned long long mask : frontier) {
                Graph h = build(mask);
                int d = dist_exact(h);
                ++explored;
                if (d > bestdist) { bestdist = d; bestmask = mask; }
                for (int i=0;i<M;i++) if ((mask>>i)&1ULL) {
                    unsigned long long nm = mask & ~(1ULL<<i);
                    if (seen.count(nm)) continue;
                    Graph h2 = build(nm);
                    if (bip_exact_fast(h2) == target) { seen.insert(nm); next.push_back(nm); }
                    else seen.insert(nm);
                }
            }
            printf("layer %d : %zu states, running max dist = %d (explored %lld)\n", layer, frontier.size(), bestdist, explored);
            fflush(stdout);
            frontier.swap(next);
            ++layer;
            if (explored > 2000000) { printf("ABORT: too many states\n"); break; }
        }
        Graph hb = build(bestmask);
        printf("RESULT target bip=%d : states=%lld  max dist=%d  witness=%s  m=%d bip=%d\n",
               target, explored, bestdist, g6encode(hb.n, hb.edges).c_str(), hb.m, bip_exact_fast(hb));
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 1;
}
