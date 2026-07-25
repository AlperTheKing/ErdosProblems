// Order-by-order beam search, v2.
//
// Fixes over v1: (a) O(1) hashed dedup on a canonical-ish invariant instead of an O(K^2) scan
// on a coarse signature that collapsed the beam onto one lineage; (b) much wider beams;
// (c) structured injection at every order -- all C5 blow-ups with the given order, so the beam
// can never drift away from the known extremal family; (d) keeps several graphs per invariant.
//
// A vertex may be appended to a triangle-free graph with neighbourhood S iff S is an INDEPENDENT
// set (a triangle through the new vertex needs two adjacent neighbours), so the one-step
// extension is exhaustive. Scores are EXACT bip via full 2^(n-1) Gray-code maximum cut.
//
// Usage: claude_beam2.exe n_start n_end beam [cap_per_graph] < seeds.g6

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <unordered_set>
#include <iostream>

static inline int popcnt(uint64_t x) { return __builtin_popcountll(x); }

struct Gr {
    int n = 0;
    std::vector<uint64_t> adj;
    int m = 0;
    int bip = -1;
};

static Gr decode(const std::string& s) {
    Gr g; g.n = (int)s[0] - 63; g.adj.assign(g.n, 0);
    size_t p = 1; int cur = 0, nb = 0;
    for (int j = 1; j < g.n; ++j)
        for (int i = 0; i < j; ++i) {
            if (nb == 0) { cur = (int)s[p++] - 63; nb = 6; }
            int bit = (cur >> (nb - 1)) & 1; --nb;
            if (bit) { g.adj[i] |= 1ull << j; g.adj[j] |= 1ull << i; ++g.m; }
        }
    return g;
}

static std::string encode(const Gr& g) {
    std::string out; out += char(g.n + 63);
    int cur = 0, nb = 0;
    for (int j = 1; j < g.n; ++j)
        for (int i = 0; i < j; ++i) {
            cur = (cur << 1) | (int)((g.adj[i] >> j) & 1);
            if (++nb == 6) { out += char(cur + 63); cur = 0; nb = 0; }
        }
    if (nb) { cur <<= (6 - nb); out += char(cur + 63); }
    return out;
}

static int maxcut(const Gr& g) {
    const int n = g.n;
    int deg[64];
    for (int i = 0; i < n; ++i) deg[i] = popcnt(g.adj[i]);
    uint64_t S = 1ull;
    int cut = deg[0], best = cut;
    const uint64_t steps = 1ull << (n - 1);
    for (uint64_t k = 1; k < steps; ++k) {
        int v = __builtin_ctzll(k) + 1;
        uint64_t bit = 1ull << v;
        int a = popcnt(g.adj[v] & S);
        if (S & bit) { cut += 2 * a - deg[v]; S &= ~bit; }
        else         { cut += deg[v] - 2 * a; S |= bit; }
        if (cut > best) best = cut;
    }
    return best;
}

// invariant: bip, m, sorted degrees, sorted multiset of sorted neighbour-degree lists
static uint64_t invariant(const Gr& g) {
    std::vector<uint64_t> rows;
    int deg[64];
    for (int i = 0; i < g.n; ++i) deg[i] = popcnt(g.adj[i]);
    for (int i = 0; i < g.n; ++i) {
        std::vector<int> nd;
        for (int j = 0; j < g.n; ++j) if ((g.adj[i] >> j) & 1) nd.push_back(deg[j]);
        std::sort(nd.begin(), nd.end());
        uint64_t h = 1469598103934665603ull;
        h = (h ^ (uint64_t)deg[i]) * 1099511628211ull;
        for (int d : nd) h = (h ^ (uint64_t)d) * 1099511628211ull;
        rows.push_back(h);
    }
    std::sort(rows.begin(), rows.end());
    uint64_t H = 1469598103934665603ull;
    H = (H ^ (uint64_t)g.bip) * 1099511628211ull;
    H = (H ^ (uint64_t)g.m) * 1099511628211ull;
    for (uint64_t r : rows) H = (H ^ r) * 1099511628211ull;
    return H;
}

template <class F>
static void indep_sets(const Gr& g, long long cap, F&& f) {
    long long visited = 0;
    struct Frame { int v; uint64_t cur; uint64_t cand; };
    std::vector<Frame> st;
    st.push_back({0, 0ull, (1ull << g.n) - 1});
    while (!st.empty()) {
        Frame fr = st.back(); st.pop_back();
        if (fr.v == g.n) { f(fr.cur); if (++visited >= cap) return; continue; }
        st.push_back({fr.v + 1, fr.cur, fr.cand});
        if ((fr.cand >> fr.v) & 1)
            st.push_back({fr.v + 1, fr.cur | (1ull << fr.v), fr.cand & ~g.adj[fr.v]});
    }
}

// all C5 blow-ups on n vertices, as structured injection
static std::vector<Gr> blowups(int n) {
    std::vector<Gr> out;
    for (int a = 1; a <= n; ++a)
      for (int b = 1; a + b <= n; ++b)
        for (int c = 1; a + b + c <= n; ++c)
          for (int d = 1; a + b + c + d <= n; ++d) {
              int e = n - a - b - c - d;
              if (e < 1) continue;
              int p[5] = {a, b, c, d, e};
              Gr g; g.n = n; g.adj.assign(n, 0); g.m = 0;
              int start[5], acc = 0;
              for (int i = 0; i < 5; ++i) { start[i] = acc; acc += p[i]; }
              for (int k = 0; k < 5; ++k) {
                  int l = (k + 1) % 5;
                  for (int u = start[k]; u < start[k] + p[k]; ++u)
                      for (int w = start[l]; w < start[l] + p[l]; ++w) {
                          g.adj[u] |= 1ull << w; g.adj[w] |= 1ull << u; ++g.m;
                      }
              }
              g.bip = g.m - maxcut(g);
              out.push_back(std::move(g));
          }
    return out;
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: %s n_start n_end beam [cap] < seeds.g6\n", argv[0]); return 2; }
    const int n0 = std::atoi(argv[1]);
    const int n1 = std::atoi(argv[2]);
    const size_t BEAM = (size_t)std::atoll(argv[3]);
    const long long CAP = (argc > 4) ? std::atoll(argv[4]) : 2000000;

    std::vector<Gr> beam;
    std::string line;
    std::ios::sync_with_stdio(false);
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        Gr g = decode(line);
        if (g.n != n0) { std::fprintf(stderr, "seed order %d != %d\n", g.n, n0); return 3; }
        g.bip = g.m - maxcut(g);
        beam.push_back(std::move(g));
    }
    std::printf("seeds n=%d: %zu\n", n0, beam.size());
    std::fflush(stdout);

    for (int n = n0; n < n1; ++n) {
        std::vector<Gr> next;
        for (const Gr& g : beam)
            indep_sets(g, CAP, [&](uint64_t S) {
                Gr h; h.n = g.n + 1; h.adj = g.adj; h.adj.push_back(S);
                h.m = g.m + popcnt(S);
                for (int v = 0; v < g.n; ++v) if ((S >> v) & 1) h.adj[v] |= 1ull << g.n;
                h.bip = h.m - maxcut(h);
                next.push_back(std::move(h));
            });
        for (Gr& b : blowups(n + 1)) next.push_back(std::move(b));

        std::sort(next.begin(), next.end(), [](const Gr& a, const Gr& b) {
            if (a.bip != b.bip) return a.bip > b.bip;
            return a.m > b.m;
        });
        std::unordered_set<uint64_t> seen;
        std::vector<Gr> keep;
        for (const Gr& g : next) {
            uint64_t inv = invariant(g);
            if (!seen.insert(inv).second) continue;
            keep.push_back(g);
            if (keep.size() >= BEAM) break;
        }
        if (keep.empty()) { std::printf("n=%d: beam died\n", n + 1); break; }
        beam.swap(keep);
        int best = beam.front().bip;
        int nn = n + 1;
        std::printf("n=%2d  best_bip=%3d  bound=%7.2f  floor=%3d  beam=%zu  %s  top=%s\n",
                    nn, best, nn * nn / 25.0, (nn * nn) / 25, beam.size(),
                    (25LL * best > 1LL * nn * nn) ? "*** VIOLATION ***" : "ok",
                    encode(beam.front()).c_str());
        std::fflush(stdout);
        if (25LL * best > 1LL * nn * nn) {
            std::printf("*** COUNTEREXAMPLE CANDIDATE n=%d bip=%d g6=%s\n", nn, best, encode(beam.front()).c_str());
            std::fflush(stdout);
            return 0;
        }
    }
    return 0;
}
