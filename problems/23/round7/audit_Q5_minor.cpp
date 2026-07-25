// A8: INDEPENDENT odd-K5-minor decider for the ALL-NEGATIVE signed graph (G,E).
// Different algorithm from the target's: SWITCHING-FIRST.
//   for every switching class c: V -> {0,1}   (c[0]=0 fixed; c and its complement
//        give the same signature, so this is exhaustive)
//     positive edges = endpoints of different colour   (contractible)
//     negative edges = endpoints of the same colour    (K5 edges)
//     look for 5 disjoint sets, each connected in the POSITIVE subgraph, pairwise
//     joined by a NEGATIVE edge.
// Completeness: any signed minor is obtained by switching, deleting and contracting
// positive trees; and the contracted signed K5 is switching-equivalent to the
// all-negative K5 iff some flip of whole branch sets makes all 10 links negative,
// which is covered because flipping a whole branch set is itself one of the
// switchings c enumerated here.
//   usage: audit_Q5_minor.exe <graph6|C5[2]|V8|And4|And5> [plain]
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

int N;
vector<uint32_t> A;

static void decode(const string &s) {
    vector<int> d;
    for (char c : s) d.push_back((int)c - 63);
    N = d[0];
    vector<int> bits;
    for (size_t i = 1; i < d.size(); i++)
        for (int k = 5; k >= 0; k--) bits.push_back((d[i] >> k) & 1);
    A.assign(N, 0);
    int idx = 0;
    for (int j = 1; j < N; j++)
        for (int i = 0; i < j; i++) {
            if (bits[idx]) { A[i] |= 1u << j; A[j] |= 1u << i; }
            idx++;
        }
}

static void named(const string &g) {
    if (g == "V8") {
        N = 8; A.assign(8, 0);
        auto add = [&](int u, int v) { A[u] |= 1u << v; A[v] |= 1u << u; };
        for (int i = 0; i < 8; i++) { add(i, (i + 1) % 8); if (i < 4) add(i, i + 4); }
    } else if (g == "C5[2]") {
        N = 10; A.assign(10, 0);
        auto add = [&](int u, int v) { A[u] |= 1u << v; A[v] |= 1u << u; };
        for (int p = 0; p < 5; p++) for (int a = 0; a < 2; a++) for (int b = 0; b < 2; b++)
            add(p * 2 + a, ((p + 1) % 5) * 2 + b);
    } else if (g == "And4" || g == "And5" || g == "And3" || g == "And6") {
        int k = g[3] - '0'; N = 3 * k - 1; A.assign(N, 0);
        for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) {
            int d = min((j - i + N) % N, (i - j + N) % N);
            if (3 * d > N) { A[i] |= 1u << j; A[j] |= 1u << i; }
        }
    } else decode(g);
}

static bool conn(uint32_t m, const vector<uint32_t> &adj) {
    if (!m) return false;
    int s = __builtin_ctz(m);
    uint32_t seen = 1u << s, fr = 1u << s;
    while (fr) {
        uint32_t nx = 0, f = fr;
        while (f) { int v = __builtin_ctz(f); f &= f - 1; nx |= adj[v] & m & ~seen; }
        seen |= nx; fr = nx;
    }
    return seen == m;
}

// candidates for the current switching
struct Cand { uint32_t mask, negr; int mn; };
vector<Cand> cands;
uint32_t chosen[5];
uint32_t negr[5];

static bool dfs(int lvl, uint32_t used, int minv, size_t start) {
    if (lvl == 5) return true;
    for (size_t i = start; i < cands.size(); i++) {
        const Cand &c = cands[i];
        if (c.mn <= minv) continue;
        if (c.mask & used) continue;
        bool ok = true;
        for (int j = 0; j < lvl; j++)
            if (!(negr[j] & c.mask) || !(c.negr & chosen[j])) { ok = false; break; }
        if (!ok) continue;
        chosen[lvl] = c.mask; negr[lvl] = c.negr;
        if (dfs(lvl + 1, used | c.mask, c.mn, i + 1)) return true;
    }
    return false;
}

int main(int argc, char **argv) {
    if (argc < 2) { printf("need graph\n"); return 1; }
    named(argv[1]);
    bool plain = (argc > 2 && string(argv[2]) == "plain");
    long long E = 0;
    for (int v = 0; v < N; v++) E += __builtin_popcount(A[v]);
    E /= 2;
    printf("N=%d E=%lld  mode=%s\n", N, E, plain ? "PLAIN K5 minor" : "ODD-K5 minor");

    if (plain) {   // plain K5 minor: connected in A, pairwise adjacent in A
        cands.clear();
        for (uint32_t m = 1; m < (1u << N); m++) {
            if (__builtin_popcount(m) > N - 4) continue;
            if (!conn(m, A)) continue;
            uint32_t r = 0; uint32_t t = m;
            while (t) { int v = __builtin_ctz(t); t &= t - 1; r |= A[v]; }
            cands.push_back({m, (uint32_t)(r & ~m), __builtin_ctz(m)});
        }
        sort(cands.begin(), cands.end(), [](const Cand &a, const Cand &b) { return a.mn < b.mn; });
        bool f = dfs(0, 0, -1, 0);
        printf("candidates=%zu\nK5 MINOR: %s\n", cands.size(), f ? "YES" : "NO");
        if (f) { printf("  branch sets:"); for (int i = 0; i < 5; i++) {
                    printf(" {"); uint32_t b = chosen[i];
                    while (b) { printf("%d%s", __builtin_ctz(b), (b & (b - 1)) ? "," : ""); b &= b - 1; }
                    printf("}"); } printf("\n"); }
        return 0;
    }

    long long ncol = 0;
    for (uint32_t c = 0; c < (1u << (N - 1)); c++) {
        uint32_t col = c << 1;          // vertex 0 has colour 0
        vector<uint32_t> pos(N, 0), neg(N, 0);
        for (int v = 0; v < N; v++) {
            uint32_t same = ((col >> v) & 1) ? col : (~col & ((1u << N) - 1));
            neg[v] = A[v] & same;
            pos[v] = A[v] & ~same;
        }
        ncol++;
        cands.clear();
        for (uint32_t m = 1; m < (1u << N); m++) {
            if (__builtin_popcount(m) > N - 4) continue;
            if (!conn(m, pos)) continue;
            uint32_t r = 0, t = m;
            while (t) { int v = __builtin_ctz(t); t &= t - 1; r |= neg[v]; }
            r &= ~m;
            if (__builtin_popcount(r) < 4) continue;   // needs 4 negative partners
            cands.push_back({m, r, __builtin_ctz(m)});
        }
        sort(cands.begin(), cands.end(), [](const Cand &a, const Cand &b) { return a.mn < b.mn; });
        if (dfs(0, 0, -1, 0)) {
            printf("ODD-K5 MINOR: YES   switching P={");
            for (int v = 0; v < N; v++) if ((col >> v) & 1) printf("%d,", v);
            printf("}\n  branch sets:");
            for (int i = 0; i < 5; i++) {
                printf(" {"); uint32_t b = chosen[i];
                while (b) { printf("%d%s", __builtin_ctz(b), (b & (b - 1)) ? "," : ""); b &= b - 1; }
                printf("}");
            }
            printf("\n  switchings examined: %lld of %d\n", ncol, 1 << (N - 1));
            return 0;
        }
    }
    printf("switchings examined: %lld (= 2^%d, complete)\n", ncol, N - 1);
    printf("ODD-K5 MINOR: NO\n");
    return 0;
}
