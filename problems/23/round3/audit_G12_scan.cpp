// AUDIT of G12: independent exhaustive scan over connected triangle-free graphs.
// Reads graph6 lines on stdin (from geng -tc n).  Everything is exact integer.
//
// For each graph computes
//   m          = |E|
//   bip        = m - maxcut, by exhaustive enumeration of all 2^(n-1) bipartitions
//   M1         = min_v e(G - N(v))                       (report's neighbourhood cut)
//   M2         = min over INDEPENDENT sets I of e(G - I)  (exact, all 2^n subsets)
//   M4num      = m*n - sum_v d(v)^2   (so M4 = M4num/n)
// and reports
//   (a) any graph with bip > M1 or bip > M2       -> falsifies the covering theorem
//   (b) any graph with 5*bip > m                  -> EXACT integrality-gap witness,
//       because nu* <= tau* <= m/5 (uniform 1/5 cover, valid since triangle-free)
//   (c) any graph with 25*bip > n*n               -> counterexample to Erdos #23
//   (d) exact maxima of bip, M1, M2 with witnesses (over ALL connected triangle-free
//       graphs, including bipartite ones, which the target's scan skipped)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <iostream>
#include <vector>
using namespace std;

int main(int argc, char **argv) {
    string line;
    long long cnt = 0, viol1 = 0, viol2 = 0, gapw = 0, ce = 0;
    int bestbip = -1, bestM1 = -1, bestM2 = -1;
    string gb, g1, g2;
    long long nchk = 0;
    while (getline(cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        if (line.empty()) continue;
        // ---- graph6 decode (n <= 62) ----
        int n = line[0] - 63;
        int need = n * (n - 1) / 2;
        vector<int> bits;
        bits.reserve(need + 8);
        for (size_t i = 1; i < line.size(); i++) {
            int v = line[i] - 63;
            for (int k = 5; k >= 0; k--) bits.push_back((v >> k) & 1);
        }
        vector<unsigned> adj(n, 0u);
        vector<pair<int,int>> E;
        int p = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                if (p < (int)bits.size() && bits[p]) { adj[i] |= 1u << j; adj[j] |= 1u << i; E.push_back({i, j}); }
                p++;
            }
        int m = (int)E.size();
        // ---- triangle-free assertion ----
        for (auto &e : E) if (adj[e.first] & adj[e.second]) { printf("NOT TRIANGLE FREE %s\n", line.c_str()); return 2; }
        // ---- bip by exhaustive cut enumeration ----
        unsigned full = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
        int best = m;
        for (unsigned S = 0; S < (1u << (n - 1)); S++) {
            unsigned T = full ^ S;
            int cross = 0;
            unsigned x = S;
            while (x) { int u = __builtin_ctz(x); cross += __builtin_popcount(adj[u] & T); x &= x - 1; }
            if (m - cross < best) { best = m - cross; if (!best) break; }
        }
        int bip = best;
        // ---- M1 ----
        int M1 = m;
        for (int v = 0; v < n; v++) {
            unsigned S = adj[v];
            int mono = 0;
            for (auto &e : E) if (!((S >> e.first) & 1) && !((S >> e.second) & 1)) mono++;
            if (mono < M1) M1 = mono;
        }
        // ---- M2 : exact over all independent sets ----
        vector<int> d(n, 0);
        for (auto &e : E) { d[e.first]++; d[e.second]++; }
        int bestw = 0;
        for (unsigned S = 0; S < (1u << n); S++) {
            bool ok = true; int w = 0; unsigned x = S;
            while (x) { int u = __builtin_ctz(x); if (adj[u] & S) { ok = false; break; } w += d[u]; x &= x - 1; }
            if (ok && w > bestw) bestw = w;
        }
        int M2 = m - bestw;
        cnt++;
        if (bip > M1 || bip > M2) { viol1++; if (viol1 < 6) printf("COVERING-THEOREM FALSIFIER %s bip=%d M1=%d M2=%d\n", line.c_str(), bip, M1, M2); }
        long long sd2 = 0; for (int v = 0; v < n; v++) sd2 += (long long)d[v] * d[v];
        if ((long long)bip * n > (long long)m * n - sd2) { viol2++; if (viol2 < 6) printf("M4 FALSIFIER %s bip=%d m=%d sumd2=%lld n=%d\n", line.c_str(), bip, m, sd2, n); }
        if (5 * bip > m) { gapw++; if (gapw < 21) printf("EXACT GAP WITNESS (bip > m/5 >= nu*) %s n=%d m=%d bip=%d\n", line.c_str(), n, m, bip); }
        if (25 * bip > n * n) { ce++; printf("COUNTEREXAMPLE?! %s n=%d bip=%d\n", line.c_str(), n, bip); }
        if (argc > 1 && bip >= atoi(argv[1])) { nchk++; printf("EXTREMAL %s n=%d m=%d bip=%d\n", line.c_str(), n, m, bip); }
        if (bip > bestbip) { bestbip = bip; gb = line; }
        if (M1 > bestM1) { bestM1 = M1; g1 = line; }
        if (M2 > bestM2) { bestM2 = M2; g2 = line; }
        nchk++;
    }
    printf("graphs=%lld  covering-violations=%lld  M4-violations=%lld  exact-gap-witnesses=%lld  conj-counterexamples=%lld\n",
           cnt, viol1, viol2, gapw, ce);
    printf("max bip=%d (%s)   max M1=%d (%s)   max M2=%d (%s)\n",
           bestbip, gb.c_str(), bestM1, g1.c_str(), bestM2, g2.c_str());
    return 0;
}
