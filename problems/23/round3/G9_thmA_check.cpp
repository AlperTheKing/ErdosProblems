// G9_thmA_check.cpp
// Two independent checks:
//   mode "W1": builds C5[7,2,7,7,2] on 25 vertices explicitly and brute-forces
//              bip(G) and bip(G-v) for a minimum-degree vertex v over all 2^24 cuts.
//   mode "A" : reads graph6 from stdin and verifies THEOREM A
//                  bip(G) <= m - max_v vol(N(v))     and     25*bip(G)*N^2 <= 25*(m*N^2 - 4m^2)
//              for every connected triangle-free graph supplied.
// Build: clang++ -O3 -march=native -std=c++17 G9_thmA_check.cpp -o G9_thmA_check
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>

static const int MAXN = 26;

static bool parse_g6(const std::string &s, int &n, unsigned int adj[MAXN]) {
    int c0 = (int)(unsigned char)s[0] - 63;
    if (c0 > 62) return false;
    n = c0;
    for (int i = 0; i < n; i++) adj[i] = 0;
    int nb = n * (n - 1) / 2, bitpos = 0, idx = 1;
    std::vector<int> bits(nb, 0);
    while (bitpos < nb) {
        int b = (int)(unsigned char)s[idx++] - 63;
        for (int k = 5; k >= 0 && bitpos < nb; k--) bits[bitpos++] = (b >> k) & 1;
    }
    int q = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) { if (bits[q]) { adj[i] |= 1u << j; adj[j] |= 1u << i; } q++; }
    return true;
}

// brute force min monochromatic edges over all cuts, vertex n-1 pinned to side 0
static long long bip_brute(int n, unsigned int *adj) {
    std::vector<std::pair<int,int>> E;
    for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if ((adj[u] >> v) & 1u) E.push_back({u, v});
    long long best = (long long)E.size();
    unsigned int lim = 1u << (n - 1);
    for (unsigned int S = 0; S < lim; S++) {
        long long c = 0;
        for (auto &e : E) {
            int a = (e.first  < n - 1) ? ((S >> e.first)  & 1u) : 0;
            int b = (e.second < n - 1) ? ((S >> e.second) & 1u) : 0;
            if (a == b) { c++; if (c >= best) break; }
        }
        if (c < best) best = c;
    }
    return best;
}

int main(int argc, char **argv) {
    std::ios::sync_with_stdio(false);
    std::string mode = argc > 1 ? argv[1] : "A";
    if (mode == "W1") {
        int a[5] = {7, 2, 7, 7, 2};
        int off[5], c = 0;
        for (int i = 0; i < 5; i++) { off[i] = c; c += a[i]; }
        int n = c;
        std::vector<unsigned int> adj(n, 0);
        for (int i = 0; i < 5; i++) {
            int j = (i + 1) % 5;
            for (int p = 0; p < a[i]; p++) for (int q = 0; q < a[j]; q++) {
                int u = off[i] + p, v = off[j] + q;
                adj[u] |= 1u << v; adj[v] |= 1u << u;
            }
        }
        int m = 0, delta = 999;
        for (int v = 0; v < n; v++) { int d = __builtin_popcount(adj[v]); m += d; if (d < delta) delta = d; }
        m /= 2;
        printf("W1: N=%d m=%d delta=%d\n", n, m, delta);
        printf("W1: bip = %lld  (blow-up identity predicts 14)\n", bip_brute(n, adj.data()));
        // delete vertex 0 (a part-0 vertex, degree 4)
        std::vector<unsigned int> adj2(n - 1, 0);
        for (int u = 1; u < n; u++) for (int v = 1; v < n; v++) if ((adj[u] >> v) & 1u) adj2[u - 1] |= 1u << (v - 1);
        printf("W1-v: bip = %lld  (blow-up identity predicts 12)\n", bip_brute(n - 1, adj2.data()));
        return 0;
    }
    long long cnt = 0, fail1 = 0, fail2 = 0, tight1 = 0;
    std::string line;
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty()) continue;
        int n; unsigned int adj[MAXN];
        if (!parse_g6(line, n, adj)) continue;
        cnt++;
        long long m = 0;
        int deg[MAXN];
        for (int v = 0; v < n; v++) { deg[v] = __builtin_popcount(adj[v]); m += deg[v]; }
        m /= 2;
        long long volmax = 0;
        for (int v = 0; v < n; v++) {
            long long vol = 0;
            for (int w = 0; w < n; w++) if ((adj[v] >> w) & 1u) vol += deg[w];
            if (vol > volmax) volmax = vol;
        }
        long long b = bip_brute(n, adj);
        if (b > m - volmax) { fail1++; printf("FAIL-A1 %s bip=%lld m=%lld volmax=%lld\n", line.c_str(), b, m, volmax); }
        if (b == m - volmax) tight1++;
        // 25*b*N^2 <= 25*(m*N^2 - 4m^2)  <=>  b <= m - 4m^2/N^2  (integers, exact)
        if (b * (long long)n * n > m * (long long)n * n - 4 * m * m) {
            fail2++; printf("FAIL-A2 %s bip=%lld m=%lld N=%d\n", line.c_str(), b, m, n);
        }
    }
    printf("checked=%lld  ThmA-strong failures=%lld  ThmA-CS failures=%lld  strong-form TIGHT on %lld\n",
           cnt, fail1, fail2, tight1);
    return 0;
}
