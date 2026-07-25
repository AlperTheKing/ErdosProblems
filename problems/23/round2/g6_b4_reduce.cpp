// G6 adversary test of (B4): bip(G) <= bip(G-v) + floor(d(v)/2)  for every vertex v.
// Also: (a) monotonicity bip(G) >= bip(G-v);
//       (b) the strictly stronger candidate bip(G) <= bip(G-v) + floor((d(v)-1)/2)  [expect violations];
//       (c) exact a(n) = max bip over the input census, with a witness.
// Exact integer arithmetic; brute-force over all 2^n bipartitions.
// build: clang++ -O3 -march=native -std=c++17 g6_b4_reduce.cpp -o g6_b4_reduce.exe
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <vector>
#include <iostream>
using namespace std;

static int g6_decode(const string &s, uint64_t adj[]) {
    int p = 0;
    if (s[0] == '>') p = 10;
    int n = (int)(s[p] - 63); p++;
    for (int i = 0; i < n; i++) adj[i] = 0;
    int bit = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            int byte = bit / 6, off = bit % 6;
            int val = (s[p + byte] - 63);
            if ((val >> (5 - off)) & 1) { adj[i] |= 1ull << j; adj[j] |= 1ull << i; }
            bit++;
        }
    return n;
}

static long long bip_bf(int n, const uint64_t *adj) {
    if (n <= 1) return 0;
    long long deg[64];
    for (int i = 0; i < n; i++) deg[i] = __builtin_popcountll(adj[i]);
    long long total = 0;
    for (int i = 0; i < n; i++) total += deg[i];
    total /= 2;
    uint64_t S = 0; long long eS = 0, degS = 0, best = total;
    for (uint64_t k = 1; k < (1ull << n); k++) {
        int v = __builtin_ctzll(k);
        if (S >> v & 1) { S &= ~(1ull << v); eS -= __builtin_popcountll(adj[v] & S); degS -= deg[v]; }
        else { eS += __builtin_popcountll(adj[v] & S); S |= 1ull << v; degS += deg[v]; }
        long long mono = total - (degS - 2 * eS);
        if (mono < best) best = mono;
    }
    return best;
}

static bool has_triangle(int n, const uint64_t *adj) {
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++)
            if (adj[u] >> v & 1)
                if (adj[u] & adj[v]) return true;
    return false;
}

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    string line;
    long long ngraph = 0, nviol_b4 = 0, nviol_mono = 0, nviol_strong = 0, ntri = 0;
    long long best_bip = -1; string best_g6;
    long long tight_b4 = 0;                 // # (G,v) pairs with equality in B4
    long long tight_b4_mindeg = 0;          // equality at a minimum-degree vertex
    while (getline(cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty()) continue;
        uint64_t adj[64];
        int n = g6_decode(line, adj);
        ngraph++;
        if (has_triangle(n, adj)) { ntri++; continue; }
        long long b = bip_bf(n, adj);
        if (b > best_bip) { best_bip = b; best_g6 = line; }
        int mindeg = 1 << 30;
        for (int v = 0; v < n; v++) mindeg = min(mindeg, __builtin_popcountll(adj[v]));
        for (int v = 0; v < n; v++) {
            int d = __builtin_popcountll(adj[v]);
            // build G - v
            uint64_t sub[64]; int m = 0; int idx[64];
            for (int i = 0; i < n; i++) if (i != v) idx[i] = m++;
            for (int i = 0; i < m; i++) sub[i] = 0;
            for (int i = 0; i < n; i++) {
                if (i == v) continue;
                for (int j = i + 1; j < n; j++) {
                    if (j == v) continue;
                    if (adj[i] >> j & 1) { sub[idx[i]] |= 1ull << idx[j]; sub[idx[j]] |= 1ull << idx[i]; }
                }
            }
            long long bs = bip_bf(m, sub);
            if (b > bs + d / 2) {
                nviol_b4++;
                printf("B4 VIOLATION g6=%s v=%d d=%d bip(G)=%lld bip(G-v)=%lld floor(d/2)=%d\n",
                       line.c_str(), v, d, b, bs, d / 2);
            }
            if (b < bs) {
                nviol_mono++;
                printf("MONOTONICITY VIOLATION g6=%s v=%d bip(G)=%lld bip(G-v)=%lld\n", line.c_str(), v, b, bs);
            }
            if (d >= 1 && b > bs + (d - 1) / 2) nviol_strong++;
            if (b == bs + d / 2) { tight_b4++; if (d == mindeg) tight_b4_mindeg++; }
        }
    }
    printf("SUMMARY graphs=%lld skipped_with_triangle=%lld b4_violations=%lld monotonicity_violations=%lld "
           "strongerform_violations=%lld b4_tight_pairs=%lld b4_tight_at_mindeg=%lld a(n)=%lld witness=%s\n",
           ngraph, ntri, nviol_b4, nviol_mono, nviol_strong, tight_b4, tight_b4_mindeg, best_bip, best_g6.c_str());
    return (nviol_b4 || nviol_mono) ? 1 : 0;
}
