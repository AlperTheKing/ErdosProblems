// G10_filter.cpp -- read graph6 on stdin (from geng -t), emit
//   (a) all MAXIMAL triangle-free graphs               -> file given by argv[1]
//   (b) those with NO homomorphism to C5               -> file given by argv[2]
// in the "name h E u1 v1 ..." format consumed by G10_hunt.exe.
//
// Rationale: fact 2 of the brief gives  H -> C5  =>  max_x psi(H,x) <= max_y psi(C5,y) = 1/25,
// so a counterexample pattern must NOT be homomorphic to C5.  Edge-monotonicity of psi
// (adding an edge adds a nonnegative term to every cut) makes maximal triangle-free WLOG.
//
// build: clang++ -O3 -march=native -std=c++17 G10_filter.cpp -o G10_filter.exe

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

static int decode_g6(const char* s, uint32_t* adj) {
    int p = 0;
    int n = s[p++] - 63;
    if (n == 63) { n = ((s[p] - 63) << 12) | ((s[p + 1] - 63) << 6) | (s[p + 2] - 63); p += 3; }
    for (int i = 0; i < n; i++) adj[i] = 0;
    int bit = 0, cur = 0, have = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
        if (have == 0) { cur = s[p++] - 63; have = 6; }
        have--;
        if ((cur >> have) & 1) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
    }
    (void)bit;
    return n;
}

static bool maximal_tf(int n, const uint32_t* adj) {
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            if ((adj[i] >> j) & 1u) { if (adj[i] & adj[j]) return false; }   // triangle
            else { if (!(adj[i] & adj[j])) return false; }                   // not maximal
        }
    return true;
}

// homomorphism to C5 : colours 0..4, edge uv needs |c_u-c_v| = 1 (mod 5)
static const int C5NB[5] = { (1 << 1) | (1 << 4), (1 << 0) | (1 << 2), (1 << 1) | (1 << 3), (1 << 2) | (1 << 4), (1 << 3) | (1 << 0) };

static int Hn; static const uint32_t* Hadj; static int order_[32]; static int colr[32];

static bool dfs_c5(int k) {
    if (k == Hn) return true;
    int v = order_[k];
    int dom = 31;
    uint32_t nb = Hadj[v];
    while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; if (colr[u] >= 0) dom &= C5NB[colr[u]]; }
    if (k == 0) dom &= 1;                    // fix first vertex colour 0 (C5 is vertex-transitive)
    while (dom) {
        int c = __builtin_ctz(dom); dom &= dom - 1;
        colr[v] = c;
        if (dfs_c5(k + 1)) return true;
        colr[v] = -1;
    }
    return false;
}

static bool hom_to_c5(int n, const uint32_t* adj) {
    Hn = n; Hadj = adj;
    // order: greedily pick the vertex with most already-ordered neighbours
    bool used[32] = { false };
    for (int k = 0; k < n; k++) {
        int best = -1, bs = -2;
        for (int v = 0; v < n; v++) {
            if (used[v]) continue;
            int s = 0; for (int j = 0; j < k; j++) if ((adj[v] >> order_[j]) & 1u) s++;
            s = s * 64 + __builtin_popcount(adj[v]);
            if (s > bs) { bs = s; best = v; }
        }
        order_[k] = best; used[best] = true;
    }
    for (int v = 0; v < n; v++) colr[v] = -1;
    return dfs_c5(0);
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: G10_filter allmax.txt noc5.txt [tag]\n"); return 1; }
    const char* tag = argc > 3 ? argv[3] : "g";
    FILE* fa = fopen(argv[1], "w");
    FILE* fb = fopen(argv[2], "w");
    char buf[256];
    uint32_t adj[32];
    long long total = 0, nmax = 0, nno = 0;
    while (fgets(buf, sizeof(buf), stdin)) {
        int L = (int)strlen(buf);
        while (L && (buf[L - 1] == '\n' || buf[L - 1] == '\r')) buf[--L] = 0;
        if (!L) continue;
        total++;
        int n = decode_g6(buf, adj);
        if (!maximal_tf(n, adj)) continue;
        nmax++;
        // emit edge list
        char line[4096]; int p = 0; int E = 0;
        char elist[4096]; int q = 0;
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if ((adj[i] >> j) & 1u) { q += sprintf(elist + q, " %d %d", i, j); E++; }
        p = sprintf(line, "%s%d_%lld %d %d%s\n", tag, n, nmax - 1, n, E, elist);
        fputs(line, fa);
        if (!hom_to_c5(n, adj)) { nno++; fputs(line, fb); }
    }
    fclose(fa); fclose(fb);
    fprintf(stderr, "read %lld  maximal-tf %lld  not-hom-C5 %lld\n", total, nmax, nno);
    return 0;
}
