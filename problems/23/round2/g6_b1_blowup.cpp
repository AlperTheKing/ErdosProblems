// G6 adversary test of (B1): weighted blow-up identity.
//   Claim: bip(H[a_1..a_h]) = min over S subset V(H) of sum_{uv in E(H), u,v same side} a_u a_v.
//   Also the balanced special case bip(H[t]) = t^2 * bip(H).
// LHS is computed by BRUTE FORCE over all 2^n bipartitions of the actual blown-up graph
// (exact integers, no shortcuts).  RHS by brute force over all 2^h cuts of H.
// Reads graph6 lines on stdin (from nauty geng).  Prints only mismatches, then a summary.
//
// build: clang++ -O3 -march=native -std=c++17 g6_b1_blowup.cpp -o g6_b1_blowup.exe
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <iostream>
#include <algorithm>
using namespace std;

// ---- graph6 decode ----
static int g6_decode(const string &s, uint32_t adj[]) {
    int p = 0;
    if (s[0] == '>') p = 10; // ">>graph6<<"
    int n = (int)(s[p] - 63); p++;
    if (n == 63) { // 63 means larger encoding; we never need it here
        fprintf(stderr, "graph6 n>=63 unsupported\n"); exit(1);
    }
    for (int i = 0; i < n; i++) adj[i] = 0;
    int bit = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            int byte = bit / 6, off = bit % 6;
            int val = (s[p + byte] - 63);
            if ((val >> (5 - off)) & 1) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
            bit++;
        }
    return n;
}

// ---- exact bip of an explicit graph by full enumeration of bipartitions ----
// bip(G) = min over S of ( e(S) + e(V\S) ).  Gray-code walk over all 2^n subsets.
static long long bip_bruteforce(int n, const uint64_t *adj) {
    if (n == 0) return 0;
    if (n > 26) { fprintf(stderr, "blowup too big: n=%d\n", n); exit(1); }
    long long deg[64];
    for (int i = 0; i < n; i++) deg[i] = __builtin_popcountll(adj[i]);
    long long total = 0;
    for (int i = 0; i < n; i++) total += deg[i];
    total /= 2;
    uint64_t S = 0;          // current side-A set
    long long eS = 0;        // edges inside S
    long long best = total;  // S = empty  =>  mono = total
    // Gray code over 2^n
    for (uint64_t k = 1; k < (1ull << n); k++) {
        int v = __builtin_ctzll(k);           // bit that flips
        if (S >> v & 1) {                     // v leaves S
            S &= ~(1ull << v);
            eS -= __builtin_popcountll(adj[v] & S);
        } else {                              // v enters S
            eS += __builtin_popcountll(adj[v] & S);
            S |= 1ull << v;
        }
        long long sizeS = __builtin_popcountll(S);
        (void)sizeS;
        // edges inside complement = total - eS - e(S, V\S); easier: recompute cross via degrees
        // e(S,V\S) = sum_{v in S} deg(v) - 2 eS
        long long degS = 0;
        uint64_t t = S;
        while (t) { int v2 = __builtin_ctzll(t); t &= t - 1; degS += deg[v2]; }
        long long cross = degS - 2 * eS;
        long long mono = total - cross;
        if (mono < best) best = mono;
    }
    return best;
}

// faster variant maintaining degS incrementally
static long long bip_bruteforce_fast(int n, const uint64_t *adj) {
    if (n == 0) return 0;
    long long deg[64];
    for (int i = 0; i < n; i++) deg[i] = __builtin_popcountll(adj[i]);
    long long total = 0;
    for (int i = 0; i < n; i++) total += deg[i];
    total /= 2;
    uint64_t S = 0;
    long long eS = 0, degS = 0;
    long long best = total;
    for (uint64_t k = 1; k < (1ull << n); k++) {
        int v = __builtin_ctzll(k);
        if (S >> v & 1) {
            S &= ~(1ull << v);
            eS -= __builtin_popcountll(adj[v] & S);
            degS -= deg[v];
        } else {
            eS += __builtin_popcountll(adj[v] & S);
            S |= 1ull << v;
            degS += deg[v];
        }
        long long mono = total - (degS - 2 * eS);
        if (mono < best) best = mono;
    }
    return best;
}

int main(int argc, char **argv) {
    int amax = 3, smax = 13;
    if (argc > 1) amax = atoi(argv[1]);
    if (argc > 2) smax = atoi(argv[2]);
    string line;
    long long nH = 0, ncase = 0, nbad = 0, nslow = 0;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty()) continue;
        uint32_t hadj[32];
        int h = g6_decode(line, hadj);
        nH++;
        // enumerate weight vectors a in {0..amax}^h with sum <= smax
        vector<int> a(h, 0);
        while (true) {
            int sum = 0; for (int i = 0; i < h; i++) sum += a[i];
            if (sum <= smax) {
                // ---- RHS: min over 2^h cuts of H of sum_{uv mono} a_u a_v
                long long rhs = -1;
                for (uint32_t S = 0; S < (1u << h); S++) {
                    long long m = 0;
                    for (int u = 0; u < h; u++)
                        for (int v = u + 1; v < h; v++)
                            if (hadj[u] >> v & 1) {
                                int su = (S >> u) & 1, sv = (S >> v) & 1;
                                if (su == sv) m += (long long)a[u] * a[v];
                            }
                    if (rhs < 0 || m < rhs) rhs = m;
                }
                // ---- LHS: build blow-up explicitly, brute-force bip
                int off[32], n = 0;
                for (int i = 0; i < h; i++) { off[i] = n; n += a[i]; }
                uint64_t badj[64];
                for (int i = 0; i < n; i++) badj[i] = 0;
                for (int u = 0; u < h; u++)
                    for (int v = u + 1; v < h; v++)
                        if (hadj[u] >> v & 1)
                            for (int x = 0; x < a[u]; x++)
                                for (int y = 0; y < a[v]; y++) {
                                    badj[off[u] + x] |= 1ull << (off[v] + y);
                                    badj[off[v] + y] |= 1ull << (off[u] + x);
                                }
                long long lhs = bip_bruteforce_fast(n, badj);
                ncase++;
                if (lhs != rhs) {
                    nbad++;
                    printf("MISMATCH H=%s a=[", line.c_str());
                    for (int i = 0; i < h; i++) printf("%d%s", a[i], i + 1 < h ? "," : "");
                    printf("] bip(H[a])=%lld  formula=%lld\n", lhs, rhs);
                    fflush(stdout);
                }
                // cross-check the two brute-force maxcut implementations occasionally
                if (n <= 14 && (ncase % 4001 == 0)) {
                    long long lhs2 = bip_bruteforce(n, badj);
                    nslow++;
                    if (lhs2 != lhs) { printf("INTERNAL DISAGREE H=%s\n", line.c_str()); nbad++; }
                }
            }
            // increment odometer
            int i = 0;
            while (i < h && a[i] == amax) { a[i] = 0; i++; }
            if (i == h) break;
            a[i]++;
        }
    }
    printf("SUMMARY graphs=%lld cases=%lld mismatches=%lld crosschecked=%lld amax=%d smax=%d\n",
           nH, ncase, nbad, nslow, amax, smax);
    return nbad ? 1 : 0;
}
