// G9_mindrop_scan.cpp
// For every connected triangle-free graph on n vertices (read as graph6 from stdin) compute
//   bip(G), bip(G-v) for all v, drop(G,v) = bip(G)-bip(G-v),
//   delta = min degree,
//   A = min over MIN-DEGREE vertices v of drop(G,v)   (classical single-vertex induction)
//   B = min over ALL vertices v of drop(G,v)          (best possible single-vertex induction)
// and tabulate the MAXIMUM of A and of B over all graphs with given (n, delta),
// separately for all triangle-free graphs and for maximal triangle-free graphs.
//
// Build: clang++ -O3 -march=native -std=c++17 G9_mindrop_scan.cpp -o G9_mindrop_scan
#include <cstdio>
#include <string>
#include <vector>
#include <iostream>

static const int MAXN = 16;

static inline bool parse_g6(const std::string &s, int &n, int adj[MAXN]) {
    if (s.empty()) return false;
    int p = 0;
    int c0 = (int)(unsigned char)s[p++] - 63;
    if (c0 > 62) return false;
    n = c0;
    for (int i = 0; i < n; i++) adj[i] = 0;
    int nb = n * (n - 1) / 2;
    std::vector<int> bits(nb, 0);
    int bitpos = 0, idx = p;
    while (bitpos < nb) {
        if (idx >= (int)s.size()) return false;
        int b = (int)(unsigned char)s[idx++] - 63;
        for (int k = 5; k >= 0 && bitpos < nb; k--) bits[bitpos++] = (b >> k) & 1;
    }
    int q = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (bits[q]) { adj[i] |= 1 << j; adj[j] |= 1 << i; }
            q++;
        }
    return true;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::vector<int> bestA(MAXN + 1, -1), bestB(MAXN + 1, -1);
    std::vector<int> bestAm(MAXN + 1, -1), bestBm(MAXN + 1, -1);
    std::vector<std::string> wA(MAXN + 1), wB(MAXN + 1), wAm(MAXN + 1), wBm(MAXN + 1);
    long long cnt = 0, cntmax = 0;
    std::string line;
    std::vector<int> e;
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty()) continue;
        int n; int adj[MAXN];
        if (!parse_g6(line, n, adj)) continue;
        cnt++;
        bool maximal = true;
        for (int u = 0; u < n && maximal; u++)
            for (int v = u + 1; v < n && maximal; v++)
                if (!((adj[u] >> v) & 1) && (adj[u] & adj[v]) == 0) maximal = false;
        if (maximal) cntmax++;

        int full = (1 << n) - 1;
        e.assign(1 << n, 0);
        for (int S = 1; S <= full; S++) {
            int v = __builtin_ctz(S);
            int R = S & ~(1 << v);
            e[S] = e[R] + __builtin_popcount(adj[v] & R);
        }
        int bipG = 1 << 30;
        for (int S = 0; S <= full; S++) {
            if (!(S & 1)) continue;
            int val = e[S] + e[full ^ S];
            if (val < bipG) bipG = val;
        }
        int delta = 1 << 30;
        for (int v = 0; v < n; v++) { int d = __builtin_popcount(adj[v]); if (d < delta) delta = d; }
        int A = 1 << 30, B = 1 << 30;
        for (int v = 0; v < n; v++) {
            int V2 = full ^ (1 << v);
            int anchor = -1;
            for (int u = 0; u < n; u++) if (u != v) { anchor = u; break; }
            int bipv = 1 << 30;
            int am = 1 << anchor;
            for (int S = V2; ; S = (S - 1) & V2) {
                if (S & am) { int val = e[S] + e[V2 ^ S]; if (val < bipv) bipv = val; }
                if (S == 0) break;
            }
            int drop = bipG - bipv;
            if (drop < B) B = drop;
            if (__builtin_popcount(adj[v]) == delta && drop < A) A = drop;
        }
        if (A > bestA[delta]) { bestA[delta] = A; wA[delta] = line; }
        if (B > bestB[delta]) { bestB[delta] = B; wB[delta] = line; }
        if (maximal) {
            if (A > bestAm[delta]) { bestAm[delta] = A; wAm[delta] = line; }
            if (B > bestBm[delta]) { bestBm[delta] = B; wBm[delta] = line; }
        }
    }
    printf("n_graphs=%lld n_maximal=%lld\n", cnt, cntmax);
    printf("delta | maxA(all) floor(d/2) | maxB(all) | maxA(maxtf) | maxB(maxtf) | witnessB(maxtf)\n");
    for (int d = 0; d <= MAXN; d++) {
        if (bestA[d] < 0 && bestAm[d] < 0) continue;
        printf("%5d | %9d %10d | %9d | %11d | %11d | %s\n", d, bestA[d], d / 2, bestB[d],
               bestAm[d], bestBm[d], wBm[d].c_str());
    }
    return 0;
}
