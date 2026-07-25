// ROOT-AGENT COUNTEREXAMPLE ENGINE (Claude, round 5).
//
// COMPLETE search over patterns:  a counterexample to Erdos 23 exists iff some triangle-free H has
// max_x psi(H,x) > 1/25, i.e. iff some integer weighting a >= 0 has 25*bip(H[a]) > (sum a)^2, where
//         bip(H[a]) = min over cuts S of H of sum_{uv monochromatic} a_u a_v.
//
// Two proved reductions make the pattern search over a SMALL set:
//   * adding edges only increases every q_S, hence increases psi pointwise, so it suffices to test
//     MAXIMAL triangle-free patterns;
//   * psi is concave along transfers between twins and invariant under swapping them, so some
//     maximiser is constant on twin classes and max psi(H[a]) = max psi(H): TWIN-FREE suffices.
// So: for each n, the complete pattern space is {maximal triangle-free, twin-free graphs on n
// vertices}, which is tiny (147 at n = 12, 392 at n = 13, 1274 at n = 14 before twin-filtering).
//
// This engine reads graph6 lines and, for each, enumerates ALL a >= 0 with sum a = q (zeros allowed,
// which is essential - the induced-C5 point has zeros) for q in a range, in exact integers.
//
// Usage: claude_pattern_sweep.exe <g6file> <qmin> <qmax>
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <functional>

static int decodeG6(const std::string& s, std::vector<std::pair<int,int>>& E) {
    size_t p = 0;
    int n = s[p++] - 63;
    if (n == 63) { n = 0; for (int k = 0; k < 3; ++k) n = (n << 6) | (s[p++] - 63); }
    E.clear();
    int cur = 0, bits = 0;
    for (int j = 1; j < n; ++j)
        for (int i = 0; i < j; ++i) {
            if (bits == 0) { cur = s[p++] - 63; bits = 6; }
            int b = (cur >> (bits - 1)) & 1; --bits;
            if (b) E.push_back({i, j});
        }
    return n;
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: %s <g6file> <qmin> <qmax>\n", argv[0]); return 2; }
    FILE* f = std::fopen(argv[1], "r");
    if (!f) { std::fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    int qmin = atoi(argv[2]), qmax = atoi(argv[3]);

    char line[4096];
    long long count = 0, violations = 0;
    double bestRatio = 0; std::string bestG6;
    while (std::fgets(line, sizeof line, f)) {
        std::string g6(line);
        while (!g6.empty() && (g6.back() == '\n' || g6.back() == '\r')) g6.pop_back();
        if (g6.empty()) continue;
        std::vector<std::pair<int,int>> E;
        int n = decodeG6(g6, E);
        if (n < 5 || n > 20) continue;
        ++count;

        // triangle check (never trust the corpus)
        std::vector<std::vector<char>> A(n, std::vector<char>(n, 0));
        for (auto& e : E) { A[e.first][e.second] = A[e.second][e.first] = 1; }
        bool tri = false;
        for (int i = 0; i < n && !tri; ++i) for (int j = i+1; j < n && !tri; ++j) for (int k = j+1; k < n; ++k)
            if (A[i][j] && A[j][k] && A[i][k]) { tri = true; break; }
        if (tri) { std::printf("SKIP non-triangle-free %s\n", g6.c_str()); continue; }

        // monochromatic edge lists per cut, smallest first (so the prune fires early)
        std::vector<std::vector<std::pair<int,int>>> cuts;
        cuts.reserve(1u << (n - 1));
        for (uint32_t m = 0; m < (1u << (n - 1)); ++m) {
            uint32_t S = (m << 1) | 1u;
            std::vector<std::pair<int,int>> mono;
            for (auto& e : E) if (((S >> e.first) & 1u) == ((S >> e.second) & 1u)) mono.push_back(e);
            cuts.push_back(std::move(mono));
        }
        std::sort(cuts.begin(), cuts.end(),
                  [](const std::vector<std::pair<int,int>>& a, const std::vector<std::pair<int,int>>& b)
                  { return a.size() < b.size(); });

        for (int q = qmin; q <= qmax; ++q) {
            long long best = -1;
            std::vector<int> parts(n, 0), bestA;
            std::function<void(int,int)> rec = [&](int idx, int rem) {
                if (idx == n - 1) {
                    parts[idx] = rem;
                    long long v = -1;
                    for (auto& mono : cuts) {
                        long long s = 0;
                        for (auto& e : mono) s += (long long)parts[e.first] * parts[e.second];
                        if (v < 0 || s < v) v = s;
                        if (v <= best) break;
                    }
                    if (v > best) { best = v; bestA = parts; }
                    return;
                }
                for (int k = 0; k <= rem; ++k) { parts[idx] = k; rec(idx + 1, rem - k); }
                parts[idx] = 0;
            };
            rec(0, q);
            double ratio = (double)(25 * best) / ((double)q * q);
            if (ratio > bestRatio) { bestRatio = ratio; bestG6 = g6; }
            if (25 * best > (long long)q * q) {
                ++violations;
                std::printf("*** COUNTEREXAMPLE  %s  q=%d  bip=%lld  25bip=%lld > q^2=%lld  a=[",
                            g6.c_str(), q, best, 25 * best, (long long)q * q);
                for (int i = 0; i < n; ++i) std::printf("%d%s", bestA[i], i + 1 < n ? "," : "");
                std::printf("]\n");
                std::fflush(stdout);
            }
        }
        if (count % 200 == 0) { std::printf("... %lld patterns, %lld violations\n", count, violations); std::fflush(stdout); }
    }
    std::printf("DONE %lld patterns, q in [%d,%d], violations = %lld, best 25*bip/q^2 = %.10f (%s)\n",
                count, qmin, qmax, violations, bestRatio, bestG6.c_str());
    return violations ? 1 : 0;
}
