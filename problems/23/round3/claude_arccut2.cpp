// ROOT-AGENT GATE ENGINE (Claude, round 3): the ARC-CUT conjecture on circle graphs.
//
// Gamma_m := vertices Z_m, u ~ v iff 3 * circdist(u,v) > m.   And(k) = Gamma_{3k-1} exactly, and
// every finite discretisation of the continuum circle graph (x ~ y iff d(x,y) > 1/3) is a Gamma_m.
//
// ARC CUT: A = {i, i+1, ..., i+l-1} (a cyclic interval), B = complement.
//     arcval(A) = sum of a_u a_v over adjacent pairs inside A, plus the same inside B.
// ARCBOUND(a) = min over all m*(m+1) arc cuts.  Every arc cut is a cut, so bip(Gamma_m[a]) <=
// ARCBOUND(a) <= ... and the CONJECTURE under test is
//
//         25 * ARCBOUND(a)  <=  (sum a)^2      for every integer weighting a >= 0.
//
// A single violation kills the mechanism (it would NOT disprove Erdos 23; it would only show that
// arcs are too few).  Equality is expected exactly at the C5 configurations.
//
// Usage: claude_arccut.exe <m> <qmax> [--from q0]
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <algorithm>
#include <functional>

int m;
std::vector<std::vector<std::pair<int,int>>> arcPairs;   // per arc cut: adjacent pairs (u,v) monochromatic

static bool adjacent(int u, int v) {
    int d = std::abs(u - v);
    d = std::min(d, m - d);
    return 3 * d > m;
}

int main(int argc, char** argv) {
    m = (argc > 1) ? atoi(argv[1]) : 8;
    int qmax = (argc > 2) ? atoi(argv[2]) : 15;
    int q0 = 1; bool halfOnly = false;
    for (int i = 3; i < argc; ++i) {
        if (!strcmp(argv[i], "--from") && i + 1 < argc) q0 = atoi(argv[++i]);
        if (!strcmp(argv[i], "--half")) halfOnly = true;
    }

    // triangle check
    int tri = 0;
    for (int a = 0; a < m; ++a) for (int b = a + 1; b < m; ++b) for (int c = b + 1; c < m; ++c)
        if (adjacent(a,b) && adjacent(b,c) && adjacent(a,c)) ++tri;

    // build arc cuts
    for (int i = 0; i < m; ++i) {
        for (int l = 0; l <= m; ++l) {
            if (halfOnly && l != m/2 && l != (m+1)/2) continue;
            std::vector<char> inA(m, 0);
            for (int t = 0; t < l; ++t) inA[(i + t) % m] = 1;
            std::vector<std::pair<int,int>> mono;
            for (int u = 0; u < m; ++u) for (int v = u + 1; v < m; ++v)
                if (adjacent(u, v) && inA[u] == inA[v]) mono.push_back({u, v});
            arcPairs.push_back(std::move(mono));
        }
    }
    // dedupe and sort by size so the prune fires early
    std::sort(arcPairs.begin(), arcPairs.end());
    arcPairs.erase(std::unique(arcPairs.begin(), arcPairs.end()), arcPairs.end());
    std::sort(arcPairs.begin(), arcPairs.end(),
              [](const std::vector<std::pair<int,int>>& a, const std::vector<std::pair<int,int>>& b){
                  return a.size() < b.size(); });

    int deg = 0; for (int v = 1; v < m; ++v) if (adjacent(0, v)) ++deg;
    std::printf("Gamma_%d: degree=%d triangles=%d distinct arc cuts=%zu\n", m, deg, tri, arcPairs.size());
    if (tri) { std::printf("NOT TRIANGLE-FREE\n"); return 3; }

    int nthreads = (int)std::min<unsigned>(std::thread::hardware_concurrency(), 16u);

    for (int q = q0; q <= qmax; ++q) {
        std::atomic<long long> best{-1};
        std::mutex mtx;
        std::vector<int> bestA;

        auto work = [&](int lo, int hi) {
            std::vector<int> parts(m, 0);
            long long localBest = -1;
            std::vector<int> localA;
            std::function<void(int,int)> rec = [&](int idx, int rem) {
                if (idx == m - 1) {
                    parts[idx] = rem;
                    // canonical under rotation (lexicographically minimal)
                    for (int r = 1; r < m; ++r) {
                        for (int t = 0; t < m; ++t) {
                            int pv = parts[(r + t) % m];
                            if (pv != parts[t]) { if (pv < parts[t]) return; break; }
                        }
                    }
                    long long bound = std::max(localBest, best.load(std::memory_order_relaxed));
                    long long v = -1;
                    for (auto& mono : arcPairs) {
                        long long s = 0;
                        for (auto& e : mono) s += (long long)parts[e.first] * parts[e.second];
                        if (v < 0 || s < v) v = s;
                        if (v <= bound) break;
                    }
                    if (v > localBest) { localBest = v; localA = parts; }
                    return;
                }
                int start = (idx == 0) ? lo : 0;
                int stop  = (idx == 0) ? std::min(hi, rem) : rem;
                for (int k = start; k <= stop; ++k) { parts[idx] = k; rec(idx + 1, rem - k); }
                parts[idx] = 0;
            };
            rec(0, q);
            std::lock_guard<std::mutex> lk(mtx);
            if (localBest > best.load()) { best.store(localBest); bestA = localA; }
        };

        std::vector<std::thread> th;
        int chunk = std::max(1, (q + 1 + nthreads - 1) / nthreads);
        for (int t = 0; t * chunk <= q; ++t)
            th.emplace_back(work, t * chunk, std::min(q, (t + 1) * chunk - 1));
        for (auto& t : th) t.join();

        long long B = best.load();
        bool viol = (25 * B > (long long)q * q);
        std::printf("  q=%3d  max ARCBOUND = %6lld   25*ARC - q^2 = %8lld  %s",
                    q, B, 25 * B - (long long)q * q, viol ? "  *** ARCS INSUFFICIENT ***" : "");
        if (25 * B == (long long)q * q || viol) {
            std::printf("   tight at [");
            for (int i = 0; i < m; ++i) std::printf("%d%s", bestA[i], i + 1 < m ? "," : "");
            std::printf("]");
        }
        std::printf("\n");
        std::fflush(stdout);
        if (viol) return 1;
    }
    return 0;
}
