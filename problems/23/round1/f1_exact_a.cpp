// Exact a(N) = max { bip(G) : G triangle-free, |V(G)|=N }.
//
// Reduction used (proved in F1.md, Lemma C): bip is nondecreasing under edge
// addition, hence a(N) is attained by a MAXIMAL triangle-free graph, i.e. one in
// which every pair of non-adjacent vertices has a common neighbour.  We stream
// geng -tc output, keep only maximal graphs, and brute-force maxcut on those.
//
// build:  clang++ -O2 -std=c++17 -o exact_a exact_a.exe
// usage:  geng -tcq N | exact_a N
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <iostream>

int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    std::ios::sync_with_stdio(false);
    std::string line;
    uint32_t adj[32];
    long long total = 0, maximal = 0;
    int best = -1;
    std::string bestg;
    const uint32_t FULL = (n == 32) ? 0xffffffffu : ((1u << n) - 1u);
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        ++total;
        // decode graph6
        int nn = line[0] - 63;
        if (nn != n) { fprintf(stderr, "bad n\n"); return 1; }
        for (int i = 0; i < n; i++) adj[i] = 0;
        int bitpos = 0;
        size_t ci = 1;
        int cur = 0, have = 0;
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < j; i++) {
                if (have == 0) { cur = line[ci++] - 63; have = 6; }
                int b = (cur >> (have - 1)) & 1;
                have--;
                if (b) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
                bitpos++;
            }
        }
        // maximality: every non-adjacent pair has a common neighbour
        bool ok = true;
        for (int i = 0; i < n && ok; i++) {
            uint32_t non = FULL & ~adj[i] & ~(1u << i);
            while (non) {
                int j = __builtin_ctz(non);
                non &= non - 1;
                if (j < i) continue;
                if ((adj[i] & adj[j]) == 0) { ok = false; break; }
            }
        }
        if (!ok) continue;
        ++maximal;
        int m = 0;
        for (int i = 0; i < n; i++) m += __builtin_popcount(adj[i]);
        m /= 2;
        int bestcut = 0;
        uint32_t lim = 1u << (n - 1);
        for (uint32_t s = 0; s < lim; s++) {
            uint32_t S = (s << 1) | 1u;
            int cut = 0;
            uint32_t t = S;
            while (t) {
                int v = __builtin_ctz(t);
                t &= t - 1;
                cut += __builtin_popcount(adj[v] & ~S & FULL);
            }
            if (cut > bestcut) bestcut = cut;
        }
        int bip = m - bestcut;
        if (bip > best) { best = bip; bestg = line; }
    }
    printf("n=%d  scanned=%lld  maximal_trianglefree=%lld  a(n)=%d  witness=%s\n",
           n, total, maximal, best, bestg.c_str());
    printf("floor(n^2/25)=%d\n", (n * n) / 25);
    return 0;
}
