// h4_grow.cpp -- complete one-vertex growth step for MAXIMAL triangle-free (MTF) graphs.
//
// GENERATION THEOREM (proved in H4_EXACT_DECISION.md, section "peel rule").
//   Let G be MTF on n vertices and v any vertex, S := N_G(v), H := G - v.
//   Every addable pair of H lies inside S (a non-edge xy of H with a common neighbour
//   w != v is not addable; G maximal forces such a w unless x,y in S).  S is
//   independent in H, so for ANY maximalisation H* = H + F of H we have F subset of
//   the pairs inside S and therefore  H = H* - E_{H*}(S)  and  G = (H* - E(S)) + v.
//   Hence            MTF(n)  subset of  { (H - E(S)) + v : H in MTF(n-1), S subset V(H) }
//   and the right-hand side is enumerable in |MTF(n-1)| * 2^(n-1) steps.
//
// MAXIMALITY TEST for a candidate G = (H - E(S)) + v, given H in MTF(n-1):
//   pairs i,j both outside S : common neighbour in H survives (only edges INSIDE S are
//                              deleted), so nothing to check;
//   pairs i,j both inside  S : v is a common neighbour, nothing to check;
//   pairs i in S, j outside S, non-adjacent in H : need (N_H(i) \ S) ^ N_H(j) != 0;
//   pair  u outside S and v : need N_H(u) ^ S != 0.
//   Triangle-freeness is automatic: H - E(S) is a subgraph of H and S is independent in it.
//
// build: clang++ -O3 -march=native -std=c++17 -pthread h4_grow.cpp -o h4_grow.exe
// usage: h4_grow.exe <in.g6 of MTF(n-1)> <out.g6> [threads]
//        then:  labelg -q out.g6 | sort -u   to reject isomorphs.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>

static inline int popc(uint32_t x) { return __builtin_popcount(x); }

struct G { int n; uint32_t a[32]; };

static bool decode(const char* s, G& g) {
    int len = (int)strlen(s);
    while (len && (s[len-1]=='\n' || s[len-1]=='\r')) len--;
    if (len <= 0) return false;
    g.n = s[0] - 63;
    if (g.n < 1 || g.n > 30) return false;
    for (int i = 0; i < g.n; i++) g.a[i] = 0;
    int p = 1, bit = 0; unsigned cur = 0;
    for (int j = 1; j < g.n; j++)
        for (int i = 0; i < j; i++) {
            if (bit == 0) { if (p >= len) return false; cur = (unsigned)(s[p++] - 63); bit = 6; }
            bit--;
            if ((cur >> bit) & 1u) { g.a[i] |= 1u<<j; g.a[j] |= 1u<<i; }
        }
    return true;
}

static void encode(const G& g, char* out) {
    int n = g.n, o = 0;
    out[o++] = (char)(n + 63);
    unsigned cur = 0; int nb = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            cur = (cur<<1) | ((g.a[i]>>j)&1u);
            if (++nb == 6) { out[o++] = (char)(cur + 63); cur = 0; nb = 0; }
        }
    if (nb) out[o++] = (char)((cur << (6-nb)) + 63);
    out[o] = '\0';
}

static std::vector<G> parents;
static std::mutex outmx;
static FILE* fout;
static std::atomic<uint64_t> ncand{0}, nkeep{0}, nexact{0};
static int MINBIP = -1;          // -1 = do not evaluate bip, output every MTF child
static std::atomic<int> GBEST{-1};
static std::mutex bestmx;
static std::vector<std::string> BESTG;

// exact maximum cut, Gray-code over all 2^(n-1) bipartitions
static inline int maxcut_exact(const G& g) {
    int deg[32];
    for (int i = 0; i < g.n; i++) deg[i] = popc(g.a[i]);
    uint32_t S = 0; int cut = 0, best = 0;
    uint32_t lim = 1u << (g.n - 1);
    for (uint32_t k = 1; k < lim; k++) {
        int v = __builtin_ctz(k) + 1;
        int a = popc(g.a[v] & S);
        if ((S>>v)&1u) { cut += 2*a - deg[v]; S &= ~(1u<<v); }
        else           { cut += deg[v] - 2*a; S |=  (1u<<v); }
        if (cut > best) best = cut;
    }
    return best;
}

// cheap lower bound on maxcut: greedy sweep, a few restarts.  Used only to SKIP
// the exact computation when it cannot possibly reach the reporting threshold;
// it never affects a reported value.
static inline int maxcut_greedy(const G& g) {
    int best = 0;
    for (int start = 0; start < 3; start++) {
        uint32_t S = 0; 
        for (int rep = 0; rep < 2; rep++)
            for (int i = 0; i < g.n; i++) {
                int v = (i + start*5) % g.n;
                int inS = popc(g.a[v] & S), out = popc(g.a[v] & ~S) - 0;
                if (out > inS) S |= 1u<<v; else S &= ~(1u<<v);
            }
        int cut = 0;
        for (int i = 0; i < g.n; i++) if ((S>>i)&1u) cut += popc(g.a[i] & ~S);
        if (cut > best) best = cut;
    }
    return best;
}

static void worker(int lo, int hi) {
    std::string buf;
    buf.reserve(1<<22);
    char g6[64];
    for (int pi = lo; pi < hi; pi++) {
        const G& H = parents[pi];
        int k = H.n;                 // parent order
        uint32_t full = (k==32)?0xffffffffu:((1u<<k)-1u);
        for (uint32_t S = 1; S <= full; S++) {
            ncand.fetch_add(1, std::memory_order_relaxed);
            uint32_t outside = full & ~S;
            // (a) every u outside S has a neighbour in S
            bool ok = true;
            uint32_t t = outside;
            while (t) { int u = __builtin_ctz(t); t &= t-1;
                        if (!(H.a[u] & S)) { ok = false; break; } }
            if (!ok) continue;
            // (b) i in S, j outside S, non-adjacent in H : (N(i)\S) & N(j) != 0
            uint32_t ti = S;
            while (ti && ok) {
                int i = __builtin_ctz(ti); ti &= ti-1;
                uint32_t ni = H.a[i] & ~S;
                uint32_t tj = outside & ~H.a[i];      // j outside S, non-adjacent to i
                while (tj) { int j = __builtin_ctz(tj); tj &= tj-1;
                             if (!(ni & H.a[j])) { ok = false; break; } }
            }
            if (!ok) continue;
            G Gg; Gg.n = k + 1;
            for (int i = 0; i < k; i++) {
                uint32_t ai = H.a[i];
                if ((S>>i)&1u) { ai &= ~S; ai |= 1u<<k; }
                Gg.a[i] = ai;
            }
            Gg.a[k] = S;
            nkeep.fetch_add(1, std::memory_order_relaxed);
            if (MINBIP >= 0) {
                int m = 0; for (int i = 0; i < Gg.n; i++) m += popc(Gg.a[i]); m /= 2;
                int gb = GBEST.load(std::memory_order_relaxed);
                // Evaluate exactly whenever the candidate could either (a) be output
                // (bip >= MINBIP) or (b) raise the running maximum (bip > GBEST).
                // maxcut_greedy only LOWER-bounds maxcut, so m-greedy UPPER-bounds bip:
                // skipping below `need` can never discard either kind of candidate.
                int need = (MINBIP < gb + 1) ? MINBIP : gb + 1;
                if (m - maxcut_greedy(Gg) < need) continue;
                nexact.fetch_add(1, std::memory_order_relaxed);
                int b = m - maxcut_exact(Gg);
                if (b > GBEST.load(std::memory_order_relaxed)) {
                    std::lock_guard<std::mutex> lk(bestmx);
                    if (b > GBEST.load()) { GBEST.store(b); BESTG.clear(); }
                }
                if (b < MINBIP) continue;
                encode(Gg, g6);
                if (b == GBEST.load()) {
                    std::lock_guard<std::mutex> lk(bestmx);
                    if (BESTG.size() < 30) BESTG.push_back(g6);
                }
                buf += g6; buf += '\n';
            } else {
                encode(Gg, g6);
                buf += g6; buf += '\n';
            }
            if (buf.size() > (1u<<21)) {
                std::lock_guard<std::mutex> lk(outmx);
                fwrite(buf.data(), 1, buf.size(), fout);
                buf.clear();
            }
        }
    }
    if (!buf.empty()) {
        std::lock_guard<std::mutex> lk(outmx);
        fwrite(buf.data(), 1, buf.size(), fout);
    }
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: h4_grow in.g6 out.g6 [threads] [minbip]\n"); return 1; }
    int nthr = (argc > 3) ? atoi(argv[3]) : 8;
    if (argc > 4) MINBIP = atoi(argv[4]);
    FILE* fin = fopen(argv[1], "r");
    if (!fin) { perror("in"); return 1; }
    char line[512];
    while (fgets(line, sizeof line, fin)) {
        if (line[0]=='\0' || line[0]=='>' || line[0]=='\n') continue;
        G g; if (decode(line, g)) parents.push_back(g);
    }
    fclose(fin);
    if (parents.empty()) { fprintf(stderr, "no parents\n"); return 1; }
    fout = fopen(argv[2], "w");
    if (!fout) { perror("out"); return 1; }
    fprintf(stderr, "[grow] %zu parents on %d vertices -> %d vertices, %d threads\n",
            parents.size(), parents[0].n, parents[0].n + 1, nthr);
    std::vector<std::thread> th;
    int P = (int)parents.size();
    for (int t = 0; t < nthr; t++) {
        int lo = (int)((int64_t)P * t / nthr), hi = (int)((int64_t)P * (t+1) / nthr);
        if (lo < hi) th.emplace_back(worker, lo, hi);
    }
    for (auto& x : th) x.join();
    fclose(fout);
    fprintf(stderr, "[grow] candidates=%llu kept=%llu\n",
            (unsigned long long)ncand.load(), (unsigned long long)nkeep.load());
    return 0;
}
