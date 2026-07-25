// G9_drop_scan.cpp
// Reads graph6 lines from stdin (expects triangle-free, connected graphs from geng -t -c).
// For each graph computes bip(G) = min over cuts of #monochromatic edges (exact integers),
// and bip(G-v) for every v, hence drop(G,v) = bip(G) - bip(G-v).
// Tabulates, separately for ALL triangle-free graphs and for MAXIMAL triangle-free graphs,
// the maximum drop observed for each degree d = deg(v), together with a witness graph6 string.
//
// Build: clang++ -O3 -march=native -std=c++17 G9_drop_scan.cpp -o G9_drop_scan
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>

static const int MAXN = 16;

int n_glob;
int adjv[MAXN];

static inline bool parse_g6(const std::string &s, int &n, int adj[MAXN]) {
    if (s.empty()) return false;
    int p = 0;
    int c0 = (int)(unsigned char)s[p++] - 63;
    if (c0 > 62) return false; // large format unsupported
    n = c0;
    for (int i = 0; i < n; i++) adj[i] = 0;
    int bitpos = 0;
    int nb = n * (n - 1) / 2;
    std::vector<int> bits(nb, 0);
    int idx = p;
    while (bitpos < nb) {
        if (idx >= (int)s.size()) return false;
        int b = (int)(unsigned char)s[idx++] - 63;
        for (int k = 5; k >= 0 && bitpos < nb; k--) {
            bits[bitpos++] = (b >> k) & 1;
        }
    }
    int q = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (bits[q]) { adj[i] |= 1 << j; adj[j] |= 1 << i; }
            q++;
        }
    return true;
}

int main(int argc, char **argv) {
    std::ios::sync_with_stdio(false);
    // tables: index by degree
    std::vector<int> best_all(MAXN + 1, -1), best_max(MAXN + 1, -1);
    std::vector<std::string> wit_all(MAXN + 1), wit_max(MAXN + 1);
    long long cnt = 0, cntmax = 0;
    std::string line;
    std::vector<int> e; // e[S]
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty()) continue;
        int n; int adj[MAXN];
        if (!parse_g6(line, n, adj)) { fprintf(stderr, "parse fail: %s\n", line.c_str()); continue; }
        cnt++;
        // triangle-free check
        bool tf = true;
        for (int u = 0; u < n && tf; u++)
            for (int v = u + 1; v < n && tf; v++)
                if ((adj[u] >> v) & 1) { if (adj[u] & adj[v]) tf = false; }
        if (!tf) { fprintf(stderr, "NOT triangle-free: %s\n", line.c_str()); continue; }
        // maximal triangle-free check
        bool maximal = true;
        for (int u = 0; u < n && maximal; u++)
            for (int v = u + 1; v < n && maximal; v++)
                if (!((adj[u] >> v) & 1)) { if ((adj[u] & adj[v]) == 0) maximal = false; }
        if (maximal) cntmax++;

        int full = (1 << n) - 1;
        e.assign(1 << n, 0);
        for (int S = 1; S <= full; S++) {
            int v = __builtin_ctz(S);
            int R = S & ~(1 << v);
            e[S] = e[R] + __builtin_popcount(adj[v] & R);
        }
        // bip(G): min over S containing vertex 0
        int bipG = 1 << 30;
        for (int S = 0; S <= full; S++) {
            if (!(S & 1)) continue;
            int val = e[S] + e[full ^ S];
            if (val < bipG) bipG = val;
        }
        for (int v = 0; v < n; v++) {
            int V2 = full ^ (1 << v);
            int anchor = -1;
            for (int u = 0; u < n; u++) if (u != v) { anchor = u; break; }
            int bipv = 1 << 30;
            if (anchor < 0) { bipv = 0; }
            else {
                // iterate subsets S of V2 containing anchor
                int am = 1 << anchor;
                for (int S = V2; ; S = (S - 1) & V2) {
                    if (S & am) {
                        int val = e[S] + e[V2 ^ S];
                        if (val < bipv) bipv = val;
                    }
                    if (S == 0) break;
                }
            }
            int d = __builtin_popcount(adj[v]);
            int drop = bipG - bipv;
            if (drop > best_all[d]) { best_all[d] = drop; wit_all[d] = line; }
            if (maximal && drop > best_max[d]) { best_max[d] = drop; wit_max[d] = line; }
        }
    }
    printf("n_graphs=%lld  n_maximal=%lld\n", cnt, cntmax);
    printf("--- ALL triangle-free ---\n");
    for (int d = 0; d <= MAXN; d++) if (best_all[d] >= 0)
        printf("d=%2d  maxdrop=%2d  floor(d/2)=%2d  %s  witness=%s\n", d, best_all[d], d / 2,
               (best_all[d] == d / 2 ? "TIGHT" : "slack"), wit_all[d].c_str());
    printf("--- MAXIMAL triangle-free ---\n");
    for (int d = 0; d <= MAXN; d++) if (best_max[d] >= 0)
        printf("d=%2d  maxdrop=%2d  floor(d/2)=%2d  %s  witness=%s\n", d, best_max[d], d / 2,
               (best_max[d] == d / 2 ? "TIGHT" : "slack"), wit_max[d].c_str());
    return 0;
}
