// Q3 PASS 2 -- exact scan: read graph6 on stdin, print  g6 n m bip dist
// bip  = |E| - maxcut, by full enumeration of all 2^(n-1) cuts (exact integer)
// dist = min over phi:V->Z5 of |E(G) symmetric-difference E(B_phi)|, exact B&B.
// build: clang++ -O3 -march=native -std=c++17 Q3_pass2_scan.cpp -o Q3_pass2_scan.exe
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
using namespace std;

static int N;
static uint32_t FULL;
static uint32_t adj[32];
static int T5[5][5];

static bool decode(const string& s) {
    if (s.empty()) return false;
    int p = 0;
    int n = s[p++] - 63;
    if (n == 63) { n = 0; for (int k = 0; k < 3; k++) n = (n << 6) | (s[p++] - 63); }
    N = n;
    memset(adj, 0, sizeof(adj));
    int bit = 0, cur = 0, have = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (have == 0) { cur = s[p++] - 63; have = 6; }
            int b = (cur >> (have - 1)) & 1; have--;
            if (b) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
            bit++;
        }
    return true;
}

static int nedges() { int s = 0; for (int v = 0; v < N; v++) s += __builtin_popcount(adj[v]); return s / 2; }

static int bip_exact() {
    int cur = nedges();
    uint32_t S = 0;
    int best = cur;
    uint64_t lim = 1ull << (N - 1);
    for (uint64_t i = 1; i < lim; i++) {
        int v = __builtin_ctzll(i) + 1;
        uint32_t bv = 1u << v;
        if (S & bv) { uint32_t Sm = S & ~bv;
            cur += __builtin_popcount(adj[v] & (FULL & ~S)) - __builtin_popcount(adj[v] & Sm); S = Sm; }
        else { cur += __builtin_popcount(adj[v] & S) - __builtin_popcount(adj[v] & (FULL & ~S & ~bv)); S |= bv; }
        if (cur < best) best = cur;
    }
    return best;
}

static int phi[32], bestd;

static int paircost(int u, int v, int a, int b) {
    int e = (adj[u] >> v) & 1;
    return (e != T5[a][b]) ? 1 : 0;
}

static void rec(int k, int cur) {
    if (cur >= bestd) return;
    if (k == N) { bestd = cur; return; }
    int lb = cur;
    for (int v = k; v < N; v++) {
        int mv = 1 << 20;
        for (int a = 0; a < 5; a++) {
            int c = 0;
            for (int u = 0; u < k; u++) c += paircost(u, v, phi[u], a);
            if (c < mv) mv = c;
        }
        lb += mv;
        if (lb >= bestd) return;
    }
    pair<int,int> cand[5];
    int nc = (k == 0) ? 1 : 5;
    for (int a = 0; a < nc; a++) {
        int c = 0;
        for (int u = 0; u < k; u++) c += paircost(u, k, phi[u], a);
        cand[a] = {c, a};
    }
    sort(cand, cand + nc);
    for (int t = 0; t < nc; t++) { phi[k] = cand[t].second; rec(k + 1, cur + cand[t].first); }
}

static int dist_greedy(mt19937& rng, int restarts) {
    int best = 1 << 20, ph[32];
    for (int r = 0; r < restarts; r++) {
        for (int v = 0; v < N; v++) ph[v] = rng() % 5;
        bool imp = true;
        while (imp) { imp = false;
            for (int v = 0; v < N; v++) {
                int bc = 1 << 20, ba = ph[v];
                for (int a = 0; a < 5; a++) { int c = 0;
                    for (int u = 0; u < N; u++) if (u != v) c += paircost(u, v, ph[u], a);
                    if (c < bc) { bc = c; ba = a; } }
                if (ba != ph[v]) { ph[v] = ba; imp = true; } } }
        int tot = 0;
        for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) tot += paircost(u, v, ph[u], ph[v]);
        if (tot < best) best = tot;
    }
    return best;
}

int main() {
    for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) { int d = (a - b + 5) % 5; T5[a][b] = (d == 1 || d == 4); }
    mt19937 rng(12345);
    char buf[4096];
    while (fgets(buf, sizeof(buf), stdin)) {
        string s(buf);
        while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
        if (s.empty()) continue;
        if (!decode(s)) continue;
        FULL = (N >= 32) ? 0xffffffffu : ((1u << N) - 1u);
        int m = nedges();
        int b = bip_exact();
        bestd = dist_greedy(rng, 30) + 1;
        rec(0, 0);
        printf("%s\t%d\t%d\t%d\t%d\n", s.c_str(), N, m, b, bestd);
    }
    return 0;
}
