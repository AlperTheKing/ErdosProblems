// ROOT-AGENT GATE ENGINE (Claude, round 3).
//
// EXACT exhaustive search for a counterexample among weighted blow-ups of a fixed pattern H.
//
// By the accepted blow-up identity, for nonnegative integer weights a with sum a = q,
//         bip(H[a]) = min over cuts S of H of sum_{uv monochromatic} a_u a_v,
// and H[a] is triangle-free whenever H is, on N = q vertices.  So
//         25 * bip(H[a]) > q^2      <=>      the conjecture is FALSE.
//
// This engine enumerates ALL a >= 0 with sum a = q.  Zero parts are ESSENTIAL and were the bug in
// the earlier engine (round2/claude_blowup_sup.cpp enumerated only strictly positive parts, which
// is why it reported 0.0355 for the Wagner graph when the truth is >= 1/25 = 0.04, attained by
// putting the weight on an induced C5 and zero elsewhere).
//
// Optional canonical-form pruning for circulant patterns: keep only weight vectors that are
// lexicographically minimal among their rotations and reflections.
//
// Usage: claude_blowup_zero.exe <pattern> <qmax> [--nosym] [--from q0]
//        pattern in {c5,c7,c9,wagner,and4,and5,and6,petersen,grotzsch,c11_13,c13_15,ex12a,ex12b,ex13,ex14}
//        or  g6:<graph6 string>
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <algorithm>
#include <functional>

static long long gcdll(long long a, long long b) { while (b) { long long t = a % b; a = b; b = t; } return a < 0 ? -a : a; }

struct Graph {
    int n = 0;
    std::vector<std::pair<int,int>> E;
    bool circulant = false;
    int mod = 0;
};

static void addEdge(std::vector<std::pair<int,int>>& E, int u, int v) {
    if (u == v) return;
    int a = std::min(u,v), b = std::max(u,v);
    for (auto& e : E) if (e.first == a && e.second == b) return;
    E.push_back({a,b});
}

static Graph circulantG(int m, std::vector<int> S) {
    Graph g; g.n = m; g.circulant = true; g.mod = m;
    for (int v = 0; v < m; ++v) for (int s : S) addEdge(g.E, v, (v + s) % m);
    return g;
}

// graph6 decode
static Graph fromGraph6(const std::string& s) {
    Graph g;
    size_t p = 0;
    int n = s[p] - 63; ++p;
    if (n == 63) { // 4-byte form
        n = 0;
        for (int k = 0; k < 3; ++k) { n = (n << 6) | (s[p] - 63); ++p; }
    }
    g.n = n;
    int bitpos = 0;
    int cur = 0, bitsLeft = 0;
    for (int j = 1; j < n; ++j) {
        for (int i = 0; i < j; ++i) {
            if (bitsLeft == 0) { cur = s[p] - 63; ++p; bitsLeft = 6; }
            int bit = (cur >> (bitsLeft - 1)) & 1; --bitsLeft;
            if (bit) addEdge(g.E, i, j);
            (void)bitpos;
        }
    }
    return g;
}

static Graph named(const std::string& w) {
    if (w.rfind("g6:", 0) == 0) return fromGraph6(w.substr(3));
    if (w == "c5")  return circulantG(5, {1});
    if (w == "c7")  return circulantG(7, {1});
    if (w == "c9")  return circulantG(9, {1});
    if (w == "wagner") return circulantG(8, {1,4});              // And(3)
    if (w == "and4") return circulantG(11, {1,4});               // residues 1 mod 3 on Z_11 = {1,4,7,10} = +-{1,4}
    if (w == "and5") return circulantG(14, {1,4,7});             // {1,4,7,10,13} = +-{1,4} u {7}
    if (w == "and6") return circulantG(17, {1,4,7});             // {1,4,7,10,13,16} = +-{1,4,7}
    if (w == "c11_13") return circulantG(11, {1,3});
    if (w == "c13_15") return circulantG(13, {1,5});
    if (w == "petersen") {
        Graph g; g.n = 10;
        for (int i = 0; i < 5; ++i) {
            addEdge(g.E, i, (i+1)%5);
            addEdge(g.E, i, 5+i);
            addEdge(g.E, 5+i, 5+((i+2)%5));
        }
        return g;
    }
    if (w == "grotzsch") {
        Graph g; g.n = 11;
        for (int i = 0; i < 5; ++i) addEdge(g.E, i, (i+1)%5);
        for (int i = 0; i < 5; ++i) {
            addEdge(g.E, 5+i, (i+1)%5);
            addEdge(g.E, 5+i, (i+4)%5);
            addEdge(g.E, 5+i, 10);
        }
        return g;
    }
    if (w == "ex12a") return fromGraph6("K?ABBBwerwBw");
    if (w == "ex12b") return fromGraph6("K?BD@g]Qvo^?");
    if (w == "ex13")  return fromGraph6("L??ED@_~?~^_Fw");
    if (w == "ex14")  return fromGraph6("M?AE@bH{AYN_LgBs?");
    std::fprintf(stderr, "unknown pattern %s\n", w.c_str());
    std::exit(2);
}

int main(int argc, char** argv) {
    std::string which = (argc > 1) ? argv[1] : "wagner";
    int qmax = (argc > 2) ? atoi(argv[2]) : 20;
    bool useSym = true;
    int q0 = 1;
    for (int i = 3; i < argc; ++i) {
        if (!strcmp(argv[i], "--nosym")) useSym = false;
        else if (!strcmp(argv[i], "--from") && i + 1 < argc) q0 = atoi(argv[++i]);
    }

    Graph g = named(which);
    int n = g.n;

    // triangle check
    std::vector<std::vector<char>> A(n, std::vector<char>(n, 0));
    for (auto& e : g.E) { A[e.first][e.second] = 1; A[e.second][e.first] = 1; }
    int tri = 0;
    for (int i = 0; i < n; ++i) for (int j = i+1; j < n; ++j) for (int k = j+1; k < n; ++k)
        if (A[i][j] && A[j][k] && A[i][k]) ++tri;

    // all cuts (vertex 0 fixed to side 1), monochromatic edge lists
    std::vector<std::vector<std::pair<int,int>>> cuts;
    cuts.reserve(1u << (n-1));
    for (uint32_t m = 0; m < (1u << (n-1)); ++m) {
        uint32_t S = (m << 1) | 1u;
        std::vector<std::pair<int,int>> mono;
        for (auto& e : g.E)
            if (((S >> e.first) & 1u) == ((S >> e.second) & 1u)) mono.push_back(e);
        cuts.push_back(std::move(mono));
    }
    // order cuts by size: small monochromatic sets first -> the prune fires sooner
    std::sort(cuts.begin(), cuts.end(),
              [](const std::vector<std::pair<int,int>>& a, const std::vector<std::pair<int,int>>& b){ return a.size() < b.size(); });

    // symmetry: rotations and reflections of a circulant
    std::vector<std::vector<int>> perms;   // perms[k][v] = image of v
    if (useSym && g.circulant) {
        int m = g.mod;
        for (int r = 0; r < m; ++r) {
            std::vector<int> p(m); for (int v = 0; v < m; ++v) p[v] = (v + r) % m;
            perms.push_back(p);
            std::vector<int> q(m); for (int v = 0; v < m; ++v) q[v] = ((r - v) % m + m) % m;
            perms.push_back(q);
        }
    }

    std::printf("pattern=%s n=%d |E|=%zu triangles=%d cuts=%zu sym=%zu\n",
                which.c_str(), n, g.E.size(), tri, cuts.size(), perms.size());
    if (tri) { std::printf("NOT TRIANGLE-FREE - aborting\n"); return 3; }
    std::printf("%4s %14s %18s %12s %s\n", "q", "max bip", "bip/q^2", "vs 1/25", "argmax a");
    std::fflush(stdout);

    unsigned hw = std::thread::hardware_concurrency();
    int nthreads = (int)std::min<unsigned>(hw ? hw : 8, 16);

    for (int q = q0; q <= qmax; ++q) {
        std::atomic<long long> globalBest{-1};
        std::mutex mtx;
        std::vector<int> bestA;

        auto work = [&](int lo, int hi) {
            std::vector<int> parts(n, 0);
            long long localBest = -1;
            std::vector<int> localA;
            std::function<void(int,int)> rec = [&](int idx, int rem) {
                if (idx == n - 1) {
                    parts[idx] = rem;
                    if (!perms.empty()) {          // canonical form: keep lex-min under the group
                        for (auto& p : perms) {
                            // compare permuted vector to parts lexicographically
                            int cmp = 0;
                            for (int v = 0; v < n; ++v) {
                                int pv = parts[p[v]];
                                if (pv != parts[v]) { cmp = (pv < parts[v]) ? -1 : 1; break; }
                            }
                            if (cmp < 0) return;   // a smaller rotation exists -> skip
                        }
                    }
                    long long snap = globalBest.load(std::memory_order_relaxed);
                    long long bound = std::max(localBest, snap);
                    long long v = -1;
                    for (auto& mono : cuts) {
                        long long s = 0;
                        for (auto& e : mono) s += (long long)parts[e.first] * parts[e.second];
                        if (v < 0 || s < v) v = s;
                        if (v <= bound) break;     // cannot beat the record
                    }
                    if (v > localBest) { localBest = v; localA = parts; }
                    return;
                }
                int start = (idx == 0) ? lo : 0;
                int stop  = (idx == 0) ? std::min(hi, rem) : rem;
                for (int k = start; k <= stop; ++k) {
                    parts[idx] = k;
                    rec(idx + 1, rem - k);
                }
                parts[idx] = 0;
            };
            rec(0, q);
            std::lock_guard<std::mutex> lk(mtx);
            if (localBest > globalBest.load()) { globalBest.store(localBest); bestA = localA; }
        };

        std::vector<std::thread> th;
        int chunk = (q + 1 + nthreads - 1) / nthreads;
        for (int t = 0; t < nthreads; ++t) {
            int lo = t * chunk, hi = std::min(q, lo + chunk - 1);
            if (lo > q) break;
            th.emplace_back(work, lo, hi);
        }
        for (auto& t : th) t.join();

        long long best = globalBest.load();
        long long gg = gcdll(best, (long long)q * q);
        char frac[64]; std::snprintf(frac, sizeof frac, "%lld/%lld", best / (gg ? gg : 1), ((long long)q*q) / (gg ? gg : 1));
        std::string as = "[";
        for (int i = 0; i < (int)bestA.size(); ++i) { as += std::to_string(bestA[i]); if (i + 1 < (int)bestA.size()) as += ","; }
        as += "]";
        bool above = (25LL * best > (long long)q * q);
        std::printf("%4d %14lld %18s %12.8f %s%s\n", q, best, frac, (double)best / ((double)q*q), as.c_str(),
                    above ? "   *** 25*bip > q^2 : COUNTEREXAMPLE ***" : "");
        std::fflush(stdout);
    }
    return 0;
}
