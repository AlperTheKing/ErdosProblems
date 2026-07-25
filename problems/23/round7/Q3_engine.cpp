// Q3_engine.cpp  --  Erdos #23, round 7, label Q3 (stability).
//
// EXACT INTEGER engine.  Three modes:
//
//   mtf                 : read graph6 lines on stdin, print those that are MAXIMAL triangle-free
//                         (triangle-free and every non-adjacent pair has a common neighbour).
//   graphs   <file>     : for each graph6 line: N, |E|, bip(G), dist(G), and the optimal 5-colouring.
//   weighted <file>     : each line "<g6> w0,w1,...,w_{n-1}" with nonnegative integer weights;
//                         prints  Q=sum w, bip(H[w]) (blow-up identity), dist_w(H,w), colouring.
//
// bip(H[w]) = min over cuts S of V(H) of  sum_{uv monochromatic} w_u w_v         (accepted base 1)
// dist_w(H,w) = min over phi : V -> Z_5 of
//        sum_{uv in E, phi(u)phi(v) not consecutive mod 5} w_u w_v
//      + sum_{uv not in E, phi(u)phi(v) consecutive mod 5} w_u w_v
// i.e. the WEIGHTED EDIT DISTANCE to the nearest C5-blow-up structure (any part sizes, empty parts
// allowed).  Both quantities are integers; they are normalised by Q^2 outside this program.
//
// Everything is exact 64-bit integer arithmetic; no floating point anywhere on an acceptance path.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

static const int MAXN = 18;

struct Graph {
    int n;
    uint32_t adj[MAXN];
};

static bool parse_g6(const string &s, Graph &G) {
    if (s.empty()) return false;
    size_t p = 0;
    int n = (int)(s[0] - 63);
    p = 1;
    if (n == 63) {
        n = (((int)(s[1] - 63)) << 12) | (((int)(s[2] - 63)) << 6) | ((int)(s[3] - 63));
        p = 4;
    }
    if (n <= 0 || n > MAXN) return false;
    G.n = n;
    for (int i = 0; i < n; i++) G.adj[i] = 0;
    int need = n * (n - 1) / 2;
    vector<int> bits;
    bits.reserve(need + 6);
    for (size_t i = p; i < s.size() && (int)bits.size() < need; i++) {
        int c = (int)(s[i] - 63);
        if (c < 0 || c > 63) return false;
        for (int k = 5; k >= 0; k--) bits.push_back((c >> k) & 1);
    }
    if ((int)bits.size() < need) return false;
    int idx = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (bits[idx]) { G.adj[i] |= 1u << j; G.adj[j] |= 1u << i; }
            idx++;
        }
    return true;
}

static bool triangle_free(const Graph &G) {
    for (int u = 0; u < G.n; u++)
        for (int v = u + 1; v < G.n; v++)
            if (G.adj[u] >> v & 1)
                if (G.adj[u] & G.adj[v]) return false;
    return true;
}

static bool maximal_triangle_free(const Graph &G) {
    if (!triangle_free(G)) return false;
    for (int u = 0; u < G.n; u++)
        for (int v = u + 1; v < G.n; v++)
            if (!((G.adj[u] >> v) & 1))
                if (!(G.adj[u] & G.adj[v])) return false;   // could add uv without a triangle
    return true;
}

// ---------------------------------------------------------------- bip -----------------------

// min over cuts of the monochromatic weight, exact integers.
static long long bip_weighted(const Graph &G, const long long *w) {
    int n = G.n;
    int full = (1 << n) - 1;
    vector<long long> ws(1 << n, 0), inside(1 << n, 0);
    for (int S = 1; S <= full; S++) {
        int lo = S & (-S);
        int l = __builtin_ctz(lo);
        ws[S] = ws[S ^ lo] + w[l];
    }
    for (int S = 1; S <= full; S++) {
        int lo = S & (-S);
        int l = __builtin_ctz(lo);
        int rest = S ^ lo;
        inside[S] = inside[rest] + w[l] * ws[(int)(G.adj[l]) & rest];
    }
    long long best = -1;
    // vertex 0 fixed on side A; S ranges over subsets of {1..n-1} united with {0}
    for (int T = 0; T < (1 << (n - 1)); T++) {
        int S = (T << 1) | 1;
        long long v = inside[S] + inside[full ^ S];
        if (best < 0 || v < best) best = v;
    }
    return best;
}

// ---------------------------------------------------------------- distance -------------------

struct DistSolver {
    int n;
    long long w[MAXN];
    bool E[MAXN][MAXN];
    int ord[MAXN];              // DFS order (degree descending)
    long long best;
    int phi[MAXN];              // current assignment, indexed by ORIGINAL vertex
    int bestphi[MAXN];
    long long P[MAXN][5];       // partial cost of unassigned vertex u in class a vs assigned ones
    static inline bool req(int a, int b) { int d = a - b; if (d < 0) d = -d; return d == 1 || d == 4; }

    inline long long pcost(int u, int v, int a, int b) const {
        bool need = req(a, b);
        return (E[u][v] != need) ? w[u] * w[v] : 0LL;
    }

    void greedy() {
        // greedy + one-vertex local search, gives an initial upper bound
        for (int i = 0; i < n; i++) phi[ord[i]] = 0;
        for (int i = 0; i < n; i++) {
            int u = ord[i];
            long long bc = -1; int ba = 0;
            for (int a = 0; a < 5; a++) {
                long long c = 0;
                for (int j = 0; j < i; j++) { int v = ord[j]; c += pcost(u, v, a, phi[v]); }
                if (bc < 0 || c < bc) { bc = c; ba = a; }
            }
            phi[u] = ba;
        }
        bool improved = true;
        while (improved) {
            improved = false;
            for (int u = 0; u < n; u++) {
                long long bc = -1; int ba = phi[u];
                for (int a = 0; a < 5; a++) {
                    long long c = 0;
                    for (int v = 0; v < n; v++) if (v != u) c += pcost(u, v, a, phi[v]);
                    if (bc < 0 || c < bc) { bc = c; ba = a; }
                }
                if (ba != phi[u]) { phi[u] = ba; improved = true; }
            }
        }
        long long tot = 0;
        for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) tot += pcost(u, v, phi[u], phi[v]);
        best = tot;
        for (int u = 0; u < n; u++) bestphi[u] = phi[u];
    }

    void dfs(int depth, long long cost, bool refl_free) {
        if (depth == n) {
            if (cost < best) { best = cost; for (int u = 0; u < n; u++) bestphi[u] = phi[u]; }
            return;
        }
        // admissible bound: each unassigned vertex costs at least its best class vs assigned ones
        long long lb = 0;
        for (int j = depth; j < n; j++) {
            int u = ord[j];
            long long m = P[u][0];
            for (int a = 1; a < 5; a++) if (P[u][a] < m) m = P[u][a];
            lb += m;
        }
        if (cost + lb >= best) return;

        int u = ord[depth];
        int amax = 5;
        if (depth == 0) amax = 1;                 // rotation symmetry: first vertex in class 0
        int order[5] = {0, 1, 2, 3, 4};
        // try classes in increasing partial cost
        long long key[5];
        for (int a = 0; a < 5; a++) key[a] = P[u][a];
        for (int i = 1; i < 5; i++) { int t = order[i]; int j = i - 1;
            while (j >= 0 && key[order[j]] > key[t]) { order[j + 1] = order[j]; j--; }
            order[j + 1] = t; }

        for (int oi = 0; oi < 5; oi++) {
            int a = order[oi];
            if (depth == 0 && a != 0) continue;
            (void)amax;
            // reflection symmetry a -> -a (fixes 0, swaps 1<->4 and 2<->3):
            // the first vertex receiving a nonzero class must get class 1 or 2.
            bool nrf = refl_free;
            if (!refl_free && a != 0) {
                if (a == 3 || a == 4) continue;
                nrf = true;
            }
            long long nc = cost + P[u][a];
            if (nc >= best) continue;
            phi[u] = a;
            // update partial costs of the still-unassigned vertices
            for (int j = depth + 1; j < n; j++) {
                int v = ord[j];
                for (int b = 0; b < 5; b++) P[v][b] += pcost(v, u, b, a);
            }
            dfs(depth + 1, nc, nrf);
            for (int j = depth + 1; j < n; j++) {
                int v = ord[j];
                for (int b = 0; b < 5; b++) P[v][b] -= pcost(v, u, b, a);
            }
        }
    }

    long long solve(const Graph &G, const long long *ww) {
        n = G.n;
        for (int i = 0; i < n; i++) w[i] = ww[i];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) E[i][j] = (i != j) && ((G.adj[i] >> j) & 1);
        vector<pair<long long,int>> d;
        for (int i = 0; i < n; i++) {
            long long deg = 0;
            for (int j = 0; j < n; j++) if (E[i][j]) deg += w[j];
            d.push_back({-(deg * (w[i] + 1)), i});
        }
        sort(d.begin(), d.end());
        for (int i = 0; i < n; i++) ord[i] = d[i].second;
        greedy();
        for (int i = 0; i < n; i++) for (int a = 0; a < 5; a++) P[i][a] = 0;
        for (int i = 0; i < n; i++) phi[i] = 0;
        dfs(0, 0, false);
        return best;
    }
};

// verify a claimed distance value by brute force over all 5^n colourings (small n only)
static long long dist_brute(const Graph &G, const long long *w, int *outphi) {
    int n = G.n;
    long long total = 1;
    for (int i = 0; i < n; i++) total *= 5;
    long long best = -1;
    vector<int> phi(n, 0);
    for (long long code = 0; code < total; code++) {
        long long c = code;
        for (int i = 0; i < n; i++) { phi[i] = (int)(c % 5); c /= 5; }
        long long cost = 0;
        for (int u = 0; u < n && (best < 0 || cost < best); u++)
            for (int v = u + 1; v < n; v++) {
                int dd = phi[u] - phi[v]; if (dd < 0) dd = -dd;
                bool need = (dd == 1 || dd == 4);
                bool e = (G.adj[u] >> v) & 1;
                if (e != need) cost += w[u] * w[v];
            }
        if (best < 0 || cost < best) { best = cost; if (outphi) for (int i = 0; i < n; i++) outphi[i] = phi[i]; }
    }
    return best;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: engine mtf | graphs <file> | weighted <file> | brute <file>\n"); return 1; }
    string mode = argv[1];

    if (mode == "mtf") {
        string line;
        ios::sync_with_stdio(false);
        while (getline(cin, line)) {
            while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
            if (line.empty()) continue;
            Graph G;
            if (!parse_g6(line, G)) continue;
            if (maximal_triangle_free(G)) printf("%s\n", line.c_str());
        }
        return 0;
    }

    if (mode != "graphs" && mode != "weighted" && mode != "brute") { fprintf(stderr, "bad mode\n"); return 1; }
    if (argc < 3) { fprintf(stderr, "need file\n"); return 1; }
    FILE *f = fopen(argv[2], "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[2]); return 1; }
    char buf[4096];
    printf("g6\tn\tm\tQ\tbip\tdist\tphi\ttf\tmtf\n");
    while (fgets(buf, sizeof buf, f)) {
        string line(buf);
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty()) continue;
        string g6s = line; string ws = "";
        size_t sp = line.find_first_of(" \t");
        if (sp != string::npos) { g6s = line.substr(0, sp); ws = line.substr(sp + 1); }
        Graph G;
        if (!parse_g6(g6s, G)) { fprintf(stderr, "parse fail: %s\n", g6s.c_str()); continue; }
        long long w[MAXN];
        for (int i = 0; i < G.n; i++) w[i] = 1;
        if (mode != "graphs" && !ws.empty()) {
            int i = 0; size_t pos = 0;
            while (pos < ws.size() && i < G.n) {
                size_t c = ws.find(',', pos);
                string tok = (c == string::npos) ? ws.substr(pos) : ws.substr(pos, c - pos);
                w[i++] = atoll(tok.c_str());
                if (c == string::npos) break; else pos = c + 1;
            }
        }
        long long Q = 0; for (int i = 0; i < G.n; i++) Q += w[i];
        int m = 0; for (int u = 0; u < G.n; u++) for (int v = u + 1; v < G.n; v++) if ((G.adj[u] >> v) & 1) m++;
        long long b = bip_weighted(G, w);
        long long dst; int ph[MAXN];
        if (mode == "brute") { dst = dist_brute(G, w, ph); }
        else { DistSolver S; dst = S.solve(G, w); for (int i = 0; i < G.n; i++) ph[i] = S.bestphi[i]; }
        string ps;
        for (int i = 0; i < G.n; i++) ps += (char)('0' + ph[i]);
        printf("%s\t%d\t%d\t%lld\t%lld\t%lld\t%s\t%d\t%d\n", g6s.c_str(), G.n, m, Q, b, dst, ps.c_str(),
               triangle_free(G) ? 1 : 0, maximal_triangle_free(G) ? 1 : 0);
    }
    fclose(f);
    return 0;
}
