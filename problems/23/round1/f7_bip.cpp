// f7_bip.cpp -- exact bip(G) = |E| - maxcut(G) for graph6 graphs read from stdin.
//
// bip(G) = min over bipartitions (S, V\S) of ( e(G[S]) + e(G[V\S]) )  ("monochromatic edges").
// Exhaustive Gray-code enumeration over the 2^(n-1) bipartitions (vertex 0 fixed on side A).
// Exact integer arithmetic throughout.
//
// usage:  f7_bip [threshold]
//   no threshold : compute exact bip for every graph, print running max and all argmax graphs.
//   threshold T  : only report graphs with bip > T (early-exits as soon as a cut with <= T
//                  monochromatic edges is found, which is sound because bip is a MINIMUM).
//
// stdin: one graph6 string per line (e.g. from nauty geng -t -C n).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>

static int nverts;
static unsigned adj[32];

// graph6 decode
static bool decode_g6(const std::string &s, int &n, unsigned *A) {
    if (s.empty()) return false;
    size_t p = 0;
    int c = (unsigned char)s[p];
    if (c == 126) return false;           // n >= 63 unsupported (we never need it)
    n = c - 63; p++;
    for (int i = 0; i < n; i++) A[i] = 0;
    int nbits = n * (n - 1) / 2;
    int bit = 0;
    int i = 1, j = 0;                      // column-major upper triangle order of graph6
    for (int k = 0; k < nbits; k++) {
        if (bit == 0) {
            if (p >= s.size()) return false;
            c = (unsigned char)s[p++] - 63;
            bit = 6;
        }
        bit--;
        int v = (c >> bit) & 1;
        if (v) { A[i] |= (1u << j); A[j] |= (1u << i); }
        j++;
        if (j == i) { j = 0; i++; }
    }
    return true;
}

static inline int pc(unsigned x) { return __builtin_popcount(x); }

int main(int argc, char **argv) {
    long long threshold = -1;
    bool useThreshold = false;
    if (argc > 1) { threshold = atoll(argv[1]); useThreshold = true; }

    std::string line;
    long long count = 0;
    int best = -1;
    std::vector<std::string> bestGraphs;

    std::ios::sync_with_stdio(false);
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty() || line[0] == '>') continue;   // skip nauty header lines
        int n;
        if (!decode_g6(line, n, adj)) { fprintf(stderr, "bad g6: %s\n", line.c_str()); continue; }
        nverts = n;
        count++;

        unsigned full = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
        // start: S = {0}, everything else on side B
        unsigned S = 1u;
        int mono = 0;
        for (int v = 1; v < n; v++) mono += pc(adj[v] & (~S) & full);
        mono /= 2;                      // each B-B edge counted twice; A={0} has no internal edge
        int bip = mono;
        bool early = false;
        if (useThreshold && bip <= threshold) early = true;

        if (!early) {
            // Gray code over vertices 1..n-1
            long long total = 1LL << (n - 1);
            for (long long g = 1; g < total; g++) {
                int v = __builtin_ctzll(g) + 1;          // vertex to flip
                unsigned bv = 1u << v;
                int a = pc(adj[v] & S);                  // neighbours currently on side A
                int b = pc(adj[v] & (~S) & full);        // neighbours currently on side B
                if (S & bv) { mono += b - a; S &= ~bv; } // v moves A -> B
                else        { mono += a - b; S |= bv;  } // v moves B -> A
                if (mono < bip) {
                    bip = mono;
                    if (useThreshold && bip <= threshold) { early = true; break; }
                }
            }
        }
        if (early) continue;

        if (useThreshold) {
            printf("%s %d\n", line.c_str(), bip);
        } else {
            if (bip > best) { best = bip; bestGraphs.clear(); }
            if (bip == best) bestGraphs.push_back(line);
        }
    }

    if (!useThreshold) {
        fprintf(stderr, "graphs read: %lld\n", count);
        printf("MAXBIP %d  count_extremal %zu\n", best, bestGraphs.size());
        size_t lim = bestGraphs.size() < 400 ? bestGraphs.size() : 400;
        for (size_t i = 0; i < lim; i++) printf("EXTREMAL %s\n", bestGraphs[i].c_str());
    } else {
        fprintf(stderr, "graphs read: %lld\n", count);
    }
    return 0;
}
