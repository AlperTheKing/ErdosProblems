// f7_ratios.cpp -- exhaustive test of two candidate sharp inequalities for triangle-free G:
//
//   (A)  5*bip(G) <= e(G)                     [ maxcut >= 4e/5 ]
//   (B)  5*bip(G) + 4*e(G) <= N^2             [ stability form of Mantel ]
//
// Both are equalities for every balanced blow-up C5[n]. (A)&(B) together imply bip <= N^2/25.
//
// For each graph we early-exit the cut enumeration as soon as we find a bipartition with
// mono <= T where T = min( floor(e/5), floor((N^2-4e)/5) ): such a graph satisfies both (A),(B).
// Only graphs surviving that test get their exact bip computed and are reported.
//
// stdin: graph6 lines.  Output: violators, plus per-file maxima of 5*bip-e and 5*bip+4e-N^2.
#include <cstdio>
#include <cstdlib>
#include <string>
#include <iostream>
#include <vector>

static unsigned adj[32];

static bool decode_g6(const std::string &s, int &n, unsigned *A) {
    if (s.empty()) return false;
    size_t p = 0;
    int c = (unsigned char)s[p];
    if (c == 126) return false;
    n = c - 63; p++;
    for (int i = 0; i < n; i++) A[i] = 0;
    int nbits = n * (n - 1) / 2, bit = 0, i = 1, j = 0;
    for (int k = 0; k < nbits; k++) {
        if (bit == 0) { if (p >= s.size()) return false; c = (unsigned char)s[p++] - 63; bit = 6; }
        bit--;
        if ((c >> bit) & 1) { A[i] |= (1u << j); A[j] |= (1u << i); }
        j++; if (j == i) { j = 0; i++; }
    }
    return true;
}
static inline int pc(unsigned x) { return __builtin_popcount(x); }

int main() {
    std::string line;
    long long count = 0, survivors = 0;
    int maxA = -1000, maxB = -1000;             // max of 5bip-e and of 5bip+4e-N^2
    std::string argA, argB;
    std::ios::sync_with_stdio(false);
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty() || line[0] == '>') continue;
        int n;
        if (!decode_g6(line, n, adj)) continue;
        count++;
        unsigned full = (1u << n) - 1;
        int e = 0;
        for (int v = 0; v < n; v++) e += pc(adj[v]);
        e /= 2;
        int TA = e / 5;                                   // floor(e/5)
        int nn = n * n;
        int TB = (nn - 4 * e) >= 0 ? (nn - 4 * e) / 5 : -1;
        int T = TA < TB ? TA : TB;

        unsigned S = 1u;
        int mono = 0;
        for (int v = 1; v < n; v++) mono += pc(adj[v] & (~S) & full);
        mono /= 2;
        int bip = mono;
        bool ok = (bip <= T);
        if (!ok) {
            long long total = 1LL << (n - 1);
            for (long long g = 1; g < total; g++) {
                int v = __builtin_ctzll(g) + 1;
                unsigned bv = 1u << v;
                int a = pc(adj[v] & S), b = pc(adj[v] & (~S) & full);
                if (S & bv) { mono += b - a; S &= ~bv; } else { mono += a - b; S |= bv; }
                if (mono < bip) { bip = mono; if (bip <= T) { ok = true; break; } }
            }
        }
        if (ok) continue;                                  // satisfies both inequalities strictly enough
        survivors++;
        int vA = 5 * bip - e, vB = 5 * bip + 4 * e - nn;
        if (vA > maxA) { maxA = vA; argA = line; }
        if (vB > maxB) { maxB = vB; argB = line; }
        if (vA > 0 || vB > 0)
            printf("VIOLATION %s n=%d e=%d bip=%d 5bip-e=%d 5bip+4e-N^2=%d\n", line.c_str(), n, e, bip, vA, vB);
    }
    fprintf(stderr, "graphs=%lld survivors(bip>T)=%lld\n", count, survivors);
    printf("MAX 5bip-e = %d at %s ; MAX 5bip+4e-N^2 = %d at %s\n",
           maxA, argA.c_str(), maxB, argB.c_str());
    return 0;
}
