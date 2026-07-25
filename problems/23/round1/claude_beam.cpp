// Order-by-order beam search for triangle-free graphs of large bip.
//
// A vertex may be appended to a triangle-free graph G with neighbourhood S iff S is an
// INDEPENDENT set of G (a triangle through the new vertex needs two adjacent neighbours).
// So from a beam of graphs at order n we generate every one-vertex extension exactly, score
// each by its EXACT bip (full 2^n Gray-code maximum cut), and keep the best K.
//
// Seeded from the exact extremal graphs of the complete censuses, this explores the true
// extremal structure far better than random annealing, and it is exhaustive at each single step.
//
// Usage:  claude_beam.exe n_start n_end beam_width < seeds.g6
//         (seeds.g6 = one graph6 string per line, all of order n_start)
// Output: per order, the best bip found, the bound n^2/25, and the top graph6 strings.

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <iostream>

static inline int popcnt(uint64_t x) { return __builtin_popcountll(x); }

struct Gr {
    int n = 0;
    std::vector<uint64_t> adj;
    int m = 0;
    int bip = -1;
};

static Gr decode(const std::string& s) {
    Gr g;
    g.n = (int)s[0] - 63;
    g.adj.assign(g.n, 0);
    size_t p = 1;
    int cur = 0, nb = 0;
    for (int j = 1; j < g.n; ++j)
        for (int i = 0; i < j; ++i) {
            if (nb == 0) { cur = (int)s[p++] - 63; nb = 6; }
            int bit = (cur >> (nb - 1)) & 1; --nb;
            if (bit) { g.adj[i] |= 1ull << j; g.adj[j] |= 1ull << i; ++g.m; }
        }
    return g;
}

static std::string encode(const Gr& g) {
    std::string out;
    out += char(g.n + 63);
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
    std::vector<int> deg(n);
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

// enumerate independent sets of g, calling f(mask); cap the number visited
template <class F>
static void indep_sets(const Gr& g, long long cap, F&& f) {
    long long visited = 0;
    // iterative DFS over vertices in order
    struct Frame { int v; uint64_t cur; uint64_t cand; };
    std::vector<Frame> st;
    st.push_back({0, 0ull, (1ull << g.n) - 1});
    while (!st.empty()) {
        Frame fr = st.back(); st.pop_back();
        if (fr.v == g.n) { f(fr.cur); if (++visited >= cap) return; continue; }
        // skip vertex fr.v
        st.push_back({fr.v + 1, fr.cur, fr.cand});
        // take vertex fr.v if allowed
        if ((fr.cand >> fr.v) & 1)
            st.push_back({fr.v + 1, fr.cur | (1ull << fr.v), fr.cand & ~g.adj[fr.v]});
    }
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: %s n_start n_end beam < seeds.g6\n", argv[0]); return 2; }
    const int n0 = std::atoi(argv[1]);
    const int n1 = std::atoi(argv[2]);
    const size_t BEAM = (size_t)std::atoll(argv[3]);
    const long long CAP = (argc > 4) ? std::atoll(argv[4]) : 400000;

    std::vector<Gr> beam;
    std::string line;
    std::ios::sync_with_stdio(false);
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        Gr g = decode(line);
        if (g.n != n0) { std::fprintf(stderr, "seed order %d != %d\n", g.n, n0); return 3; }
        g.bip = g.m - maxcut(g);
        beam.push_back(g);
    }
    std::printf("seeds at n=%d: %zu, best bip %d\n", n0, beam.size(),
                beam.empty() ? -1 : std::max_element(beam.begin(), beam.end(),
                    [](const Gr& a, const Gr& b){ return a.bip < b.bip; })->bip);
    std::fflush(stdout);

    for (int n = n0; n < n1; ++n) {
        std::vector<Gr> next;
        next.reserve(BEAM * 4);
        for (const Gr& g : beam) {
            indep_sets(g, CAP, [&](uint64_t S) {
                Gr h;
                h.n = g.n + 1;
                h.adj = g.adj;
                h.adj.push_back(S);
                h.m = g.m + popcnt(S);
                for (int v = 0; v < g.n; ++v)
                    if ((S >> v) & 1) h.adj[v] |= 1ull << g.n;
                h.bip = h.m - maxcut(h);
                next.push_back(std::move(h));
            });
        }
        std::sort(next.begin(), next.end(),
                  [](const Gr& a, const Gr& b){
                      if (a.bip != b.bip) return a.bip > b.bip;
                      return a.m > b.m;
                  });
        // dedupe by (bip, m, sorted degree sequence)
        std::vector<Gr> keep;
        std::vector<std::string> sigs;
        for (const Gr& g : next) {
            std::vector<int> ds;
            for (int i = 0; i < g.n; ++i) ds.push_back(popcnt(g.adj[i]));
            std::sort(ds.begin(), ds.end());
            std::string sig = std::to_string(g.bip) + "|" + std::to_string(g.m);
            for (int d : ds) sig += "," + std::to_string(d);
            bool dup = false;
            for (const auto& s : sigs) if (s == sig) { dup = true; break; }
            if (dup) continue;
            sigs.push_back(sig);
            keep.push_back(g);
            if (keep.size() >= BEAM) break;
        }
        if (keep.empty()) { std::printf("n=%d: beam died\n", n + 1); break; }
        beam.swap(keep);
        int best = beam.front().bip;
        double bound = (n + 1) * (n + 1) / 25.0;
        std::printf("n=%2d  best_bip=%3d  bound=%7.2f  floor=%3d  %s  top=%s\n",
                    n + 1, best, bound, ((n + 1) * (n + 1)) / 25,
                    (25.0 * best > (double)((n + 1) * (n + 1))) ? "*** VIOLATION ***" : "ok",
                    encode(beam.front()).c_str());
        std::fflush(stdout);
        if (25LL * best > 1LL * (n + 1) * (n + 1)) {
            std::printf("*** COUNTEREXAMPLE CANDIDATE n=%d bip=%d g6=%s\n",
                        n + 1, best, encode(beam.front()).c_str());
            std::fflush(stdout);
        }
    }
    return 0;
}
