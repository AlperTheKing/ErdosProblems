// audit_G9_exh.cpp -- INDEPENDENT audit engine for G9 (written from scratch).
//
// Deliberately different implementation from G9_*.cpp:
//   * graph6 decoded into a byte adjacency matrix first, masks derived after
//     (a bit-order slip would show as a degree/edge-count mismatch);
//   * bip computed by iterating the side-A mask and popcounting adj&A, adj&B
//     (target used an edge list with early break / a subset-sum DP);
//   * every acceptance test is an integer comparison, no floating point anywhere.
//
// modes:
//   W1        : explicit C5[7,2,7,7,2] on 25 vertices, exhaustive 2^24 cuts:
//               bip(G), bip(G-v) for one vertex of each part, bip(G - P2 - P3),
//               bip(G - P0 - P2).
//   A         : reads graph6 on stdin, checks Theorem A
//                 bip <= m - max_v vol(N(v))    and    bip*N^2 <= m*N^2 - 4m^2
//               reports counts, failures, tightness, and triangle-freeness.
//   MINDROP   : reads graph6 on stdin, tabulates for each delta
//                 max over graphs of  min over all v of (bip(G)-bip(G-v))
//               and the same restricted to min-degree v, for all / maximal tf.
//
// Build: clang++ -O3 -march=native -std=c++17 audit_G9_exh.cpp -o audit_G9_exh
#include <cstdio>
#include <cstdint>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>

typedef unsigned long long u64;

static bool g6(const std::string &s, int &n, std::vector<std::vector<int>> &M) {
    if (s.empty()) return false;
    int n0 = (int)(unsigned char)s[0] - 63;
    if (n0 < 0 || n0 > 62) return false;
    n = n0;
    M.assign(n, std::vector<int>(n, 0));
    long long need = (long long)n * (n - 1) / 2;
    std::vector<int> bits;
    bits.reserve(need + 6);
    for (size_t i = 1; i < s.size() && (long long)bits.size() < need; i++) {
        int b = (int)(unsigned char)s[i] - 63;
        if (b < 0 || b > 63) return false;
        for (int k = 5; k >= 0; k--) bits.push_back((b >> k) & 1);
    }
    if ((long long)bits.size() < need) return false;
    long long p = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) { if (bits[p]) { M[i][j] = M[j][i] = 1; } p++; }
    return true;
}

static std::vector<u64> masks(int n, const std::vector<std::vector<int>> &M) {
    std::vector<u64> a(n, 0);
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (M[i][j]) a[i] |= 1ULL << j;
    return a;
}

// exhaustive min #monochromatic edges over all 2^(n-1) cuts, vertex 0 pinned to side A
static long long bip_exh(int n, const std::vector<u64> &adj) {
    if (n <= 1) return 0;
    u64 full = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
    long long best = -1;
    u64 lim = 1ULL << (n - 1);
    for (u64 S = 0; S < lim; S++) {
        u64 A = (S << 1) | 1ULL;
        u64 B = full ^ A;
        long long mono = 0;
        u64 x = A;
        while (x) { int v = __builtin_ctzll(x); mono += __builtin_popcountll(adj[v] & A); x &= x - 1; }
        u64 y = B;
        while (y) { int v = __builtin_ctzll(y); mono += __builtin_popcountll(adj[v] & B); y &= y - 1; }
        mono >>= 1;
        if (best < 0 || mono < best) best = mono;
    }
    return best;
}

static std::vector<u64> induced(int n, const std::vector<u64> &adj, u64 keep, int &n2) {
    std::vector<int> idx(n, -1);
    n2 = 0;
    for (int v = 0; v < n; v++) if (keep >> v & 1ULL) idx[v] = n2++;
    std::vector<u64> a2(n2, 0);
    for (int u = 0; u < n; u++) if (idx[u] >= 0)
        for (int v = 0; v < n; v++) if (idx[v] >= 0 && (adj[u] >> v & 1ULL))
            a2[idx[u]] |= 1ULL << idx[v];
    return a2;
}

int main(int argc, char **argv) {
    std::ios::sync_with_stdio(false);
    std::string mode = argc > 1 ? argv[1] : "A";

    if (mode == "W1") {
        int a[5] = {7, 2, 7, 7, 2};
        int off[5], c = 0;
        for (int i = 0; i < 5; i++) { off[i] = c; c += a[i]; }
        int n = c;
        std::vector<std::vector<int>> M(n, std::vector<int>(n, 0));
        std::vector<int> part(n, 0);
        for (int i = 0; i < 5; i++) for (int p = 0; p < a[i]; p++) part[off[i] + p] = i;
        for (int i = 0; i < 5; i++) {
            int j = (i + 1) % 5;
            for (int p = 0; p < a[i]; p++) for (int q = 0; q < a[j]; q++)
                M[off[i] + p][off[j] + q] = M[off[j] + q][off[i] + p] = 1;
        }
        std::vector<u64> adj = masks(n, M);
        long long m = 0; int delta = 1 << 30;
        for (int v = 0; v < n; v++) { int d = __builtin_popcountll(adj[v]); m += d; if (d < delta) delta = d; }
        m /= 2;
        // triangle-free check, from the matrix
        bool tf = true;
        for (int i = 0; i < n && tf; i++) for (int j = i + 1; j < n && tf; j++) if (M[i][j])
            for (int k = j + 1; k < n && tf; k++) if (M[i][k] && M[j][k]) tf = false;
        printf("W1: N=%d m=%lld delta=%d triangle_free=%d\n", n, m, delta, (int)tf);
        u64 full = (1ULL << n) - 1;
        printf("W1: bip = %lld   [exhaustive over 2^%d cuts]\n", bip_exh(n, adj), n - 1);
        for (int i = 0; i < 5; i++) {
            int v = off[i];
            int n2; std::vector<u64> a2 = induced(n, adj, full ^ (1ULL << v), n2);
            printf("W1 - (one vertex of part %d, deg %d): N=%d bip = %lld\n",
                   i, __builtin_popcountll(adj[v]), n2, bip_exh(n2, a2));
        }
        // S = P2 u P3
        u64 kill = 0;
        for (int v = 0; v < n; v++) if (part[v] == 2 || part[v] == 3) kill |= 1ULL << v;
        { int n2; std::vector<u64> a2 = induced(n, adj, full ^ kill, n2);
          printf("W1 - (P2 u P3), |S|=%d: N=%d bip = %lld\n",
                 __builtin_popcountll(kill), n2, bip_exh(n2, a2)); }
        kill = 0;
        for (int v = 0; v < n; v++) if (part[v] == 0 || part[v] == 2) kill |= 1ULL << v;
        { int n2; std::vector<u64> a2 = induced(n, adj, full ^ kill, n2);
          printf("W1 - (P0 u P2, independent), |S|=%d: N=%d bip = %lld\n",
                 __builtin_popcountll(kill), n2, bip_exh(n2, a2)); }
        // 5 from each of P0,P2,P3
        kill = 0;
        for (int i : {0, 2, 3}) for (int p = 0; p < 5; p++) kill |= 1ULL << (off[i] + p);
        { int n2; std::vector<u64> a2 = induced(n, adj, full ^ kill, n2);
          printf("W1 - (5 from each of P0,P2,P3), |S|=%d: N=%d bip = %lld\n",
                 __builtin_popcountll(kill), n2, bip_exh(n2, a2)); }
        return 0;
    }

    if (mode == "A") {
        long long cnt = 0, fail1 = 0, fail2 = 0, tight1 = 0, nottf = 0, nmax = 0;
        std::vector<long long> percnt(64, 0);
        std::string line;
        while (std::getline(std::cin, line)) {
            while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
            if (line.empty()) continue;
            int n; std::vector<std::vector<int>> M;
            if (!g6(line, n, M)) { printf("PARSEFAIL %s\n", line.c_str()); continue; }
            std::vector<u64> adj = masks(n, M);
            bool tf = true;
            for (int i = 0; i < n && tf; i++) for (int j = i + 1; j < n && tf; j++) if (M[i][j])
                for (int k = j + 1; k < n && tf; k++) if (M[i][k] && M[j][k]) tf = false;
            if (!tf) { nottf++; continue; }
            cnt++; percnt[n]++;
            bool maximal = true;
            for (int i = 0; i < n && maximal; i++) for (int j = i + 1; j < n && maximal; j++)
                if (!M[i][j] && (adj[i] & adj[j]) == 0) maximal = false;
            if (maximal) nmax++;
            long long m = 0; std::vector<int> deg(n);
            for (int v = 0; v < n; v++) { deg[v] = __builtin_popcountll(adj[v]); m += deg[v]; }
            m /= 2;
            long long volmax = 0;
            for (int v = 0; v < n; v++) {
                long long vol = 0;
                for (int w = 0; w < n; w++) if (adj[v] >> w & 1ULL) vol += deg[w];
                if (vol > volmax) volmax = vol;
            }
            long long b = bip_exh(n, adj);
            if (b > m - volmax) { fail1++; if (fail1 < 20) printf("FAIL-A-strong %s bip=%lld m=%lld volmax=%lld\n", line.c_str(), b, m, volmax); }
            if (b == m - volmax) tight1++;
            if (b * (long long)n * n > m * (long long)n * n - 4 * m * m) {
                fail2++; if (fail2 < 20) printf("FAIL-A-CS %s bip=%lld m=%lld n=%d\n", line.c_str(), b, m, n);
            }
        }
        printf("triangle-free graphs checked = %lld (maximal tf = %lld), rejected non-tf = %lld\n", cnt, nmax, nottf);
        for (int n = 0; n < 64; n++) if (percnt[n]) printf("   n=%2d : %lld\n", n, percnt[n]);
        printf("ThmA strong failures = %lld ; ThmA Cauchy-Schwarz failures = %lld ; strong form TIGHT on %lld\n",
               fail1, fail2, tight1);
        return 0;
    }

    if (mode == "MINDROP") {
        // bestB[delta] = max over graphs with that delta of  min over ALL v of drop
        // bestA[delta] = same but min only over min-degree v
        std::vector<long long> bestA(64, -1), bestB(64, -1), bestAm(64, -1), bestBm(64, -1);
        std::vector<std::string> wB(64), wBm(64);
        std::vector<long long> cntd(64, 0);
        long long cnt = 0;
        std::string line;
        while (std::getline(std::cin, line)) {
            while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
            if (line.empty()) continue;
            int n; std::vector<std::vector<int>> M;
            if (!g6(line, n, M)) continue;
            std::vector<u64> adj = masks(n, M);
            bool tf = true;
            for (int i = 0; i < n && tf; i++) for (int j = i + 1; j < n && tf; j++) if (M[i][j])
                for (int k = j + 1; k < n && tf; k++) if (M[i][k] && M[j][k]) tf = false;
            if (!tf) continue;
            cnt++;
            bool maximal = true;
            for (int i = 0; i < n && maximal; i++) for (int j = i + 1; j < n && maximal; j++)
                if (!M[i][j] && (adj[i] & adj[j]) == 0) maximal = false;
            int delta = 1 << 30;
            for (int v = 0; v < n; v++) delta = std::min(delta, __builtin_popcountll(adj[v]));
            cntd[delta]++;
            u64 full = (1ULL << n) - 1;
            long long b = bip_exh(n, adj);
            long long A = 1LL << 40, B = 1LL << 40;
            for (int v = 0; v < n; v++) {
                int n2; std::vector<u64> a2 = induced(n, adj, full ^ (1ULL << v), n2);
                long long drop = b - bip_exh(n2, a2);
                B = std::min(B, drop);
                if (__builtin_popcountll(adj[v]) == delta) A = std::min(A, drop);
            }
            if (A > bestA[delta]) bestA[delta] = A;
            if (B > bestB[delta]) { bestB[delta] = B; wB[delta] = line; }
            if (maximal) {
                if (A > bestAm[delta]) bestAm[delta] = A;
                if (B > bestBm[delta]) { bestBm[delta] = B; wBm[delta] = line; }
            }
        }
        printf("graphs=%lld\n", cnt);
        printf("delta | #graphs | maxA(all) | maxB(all) | floor(d/2) | maxB(maxtf) | witnessB(all) | witnessB(maxtf)\n");
        for (int d = 0; d < 64; d++) if (cntd[d])
            printf("%5d | %7lld | %9lld | %9lld | %10d | %11lld | %s | %s\n",
                   d, cntd[d], bestA[d], bestB[d], d / 2, bestBm[d], wB[d].c_str(), wBm[d].c_str());
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 1;
}
