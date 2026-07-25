// Fast exact scan of triangle-free graphs coming from geng on stdin (graph6).
//
// For each graph computes bip(G) = min over bipartitions of the number of
// monochromatic edges, by exhaustive search over all 2^(n-1) bipartitions
// (exact integer arithmetic).  Reports
//    * any graph with 5*bip(G) > |E|      -- these have an odd-cycle LP
//      integrality gap, because y == 1/5 is always a feasible fractional
//      odd-cycle edge cover of a triangle-free graph, so tau* <= |E|/5.
//    * any graph with 25*bip(G) >= N^2    -- these are tight for the conjecture.
//    * the maxima of bip and of bip/N^2.
//
// build:  clang++ -O3 -march=native -o scan.exe scan.cpp
// run:    geng -tcq 12 | ./scan.exe 12
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <iostream>
#include <vector>
using namespace std;

int main(int argc, char** argv) {
    int n = atoi(argv[1]);
    vector<uint32_t> adj(n);
    string line;
    long long count = 0;
    int bestBip = -1; string bestG;
    double bestRatio = -1; string bestRG; int bestRB = 0;
    long long gapCount = 0, tightCount = 0;
    uint32_t full = (n == 32) ? 0xffffffffu : ((1u << n) - 1u);
    while (getline(cin, line)) {
        if (line.empty()) continue;
        if (line[0] == '>') continue;
        // graph6 decode (n <= 62)
        const char* p = line.c_str();
        int nn = p[0] - 63;
        if (nn != n) continue;
        for (int i = 0; i < n; i++) adj[i] = 0;
        int bitpos = 0;
        int m = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                int byte = bitpos / 6, off = bitpos % 6;
                int val = (p[1 + byte] - 63) >> (5 - off) & 1;
                if (val) { adj[i] |= 1u << j; adj[j] |= 1u << i; m++; }
                bitpos++;
            }
        // bip by exhaustive search, vertex 0 pinned to side S
        int best = m;
        uint32_t half = 1u << (n - 1);
        for (uint32_t rest = 0; rest < half; rest++) {
            uint32_t S = 1u | (rest << 1);
            uint32_t T = full ^ S;
            int mono = 0;
            for (int v = 0; v < n; v++)
                mono += __builtin_popcount(adj[v] & (((S >> v) & 1u) ? S : T));
            mono >>= 1;
            if (mono < best) { best = mono; if (best == 0) break; }
        }
        count++;
        if (best > bestBip) { bestBip = best; bestG = line; }
        double r = (double)best / (double)(n * n);
        if (r > bestRatio) { bestRatio = r; bestRG = line; bestRB = best; }
        if (5 * best > m) {
            gapCount++;
            printf("LP-GAP  g6=%s  N=%d m=%d bip=%d  |E|/5=%.4f\n",
                   line.c_str(), n, m, best, m / 5.0);
        }
        if (25 * best >= n * n) {
            tightCount++;
            printf("TIGHT   g6=%s  N=%d m=%d bip=%d  N^2/25=%.4f\n",
                   line.c_str(), n, m, best, n * n / 25.0);
        }
    }
    printf("n=%d graphs=%lld  maxbip=%d (%s)  max bip/N^2=%.6f (bip=%d, %s)  "
           "LPgaps=%lld tight=%lld\n",
           n, count, bestBip, bestG.c_str(), bestRatio, bestRB, bestRG.c_str(),
           gapCount, tightCount);
    return 0;
}
