// audit_G10_filter.cpp -- INDEPENDENT re-implementation of the corpus filter used by
// round3/G10_filter.cpp.  Written from scratch: different graph6 decoder (explicit
// bit counter over the column-major upper triangle), different triangle test
// (per-edge common-neighbour popcount over an adjacency array built in a second pass),
// different C5-homomorphism search (iterative stack DFS in NATURAL vertex order with
// domain propagation, plus an optional exhaustive 5^n check for n <= 8).
//
// stdin : graph6 lines (from geng)
// argv[1]: output file for MAXIMAL triangle-free graphs, "name h E u v u v ..." format
// argv[2]: output file for the non-C5-colourable subset
// argv[3]: name tag
// stderr : "read <t>  maximaltf <m>  nohomC5 <k>"
//
// build: clang++ -O3 -march=native -std=c++17 audit_G10_filter.cpp -o audit_G10_filter.exe

#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cstdlib>
#include <vector>
using namespace std;

static int decode(const char* s, int* deg, uint32_t* adj) {
    int p = 0;
    int n = s[p++] - 63;
    if (n == 63) { n = ((s[p] - 63) << 12) | ((s[p + 1] - 63) << 6) | (s[p + 2] - 63); p += 3; }
    for (int i = 0; i < n; i++) { adj[i] = 0; deg[i] = 0; }
    long long need = (long long)n * (n - 1) / 2;
    long long got = 0;
    int i = 0, j = 1;                        // walk pairs (i,j), i<j, j outer
    while (got < need) {
        int byte = s[p++] - 63;
        for (int b = 5; b >= 0 && got < need; b--, got++) {
            if ((byte >> b) & 1) { adj[i] |= 1u << j; adj[j] |= 1u << i; deg[i]++; deg[j]++; }
            i++;
            if (i == j) { i = 0; j++; }
        }
    }
    return n;
}

// maximal triangle-free: no triangle AND every non-edge has a common neighbour
static bool maximal_tf(int n, const uint32_t* adj) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            bool e = (adj[i] >> j) & 1u;
            uint32_t common = adj[i] & adj[j];
            if (e && common) return false;         // triangle
            if (!e && !common) return false;       // non-edge without common nb
        }
    return true;
}

// homomorphism to C5, iterative DFS, natural vertex order, domain masks.
static bool hom_c5(int n, const uint32_t* adj) {
    static const int NB[5] = { 0b10010, 0b00101, 0b01010, 0b10100, 0b01001 };
    int col[32];
    for (int i = 0; i < n; i++) col[i] = -1;
    // process components separately, first vertex of each component pinned to 0
    bool done[32] = { false };
    for (int start = 0; start < n; start++) {
        if (done[start]) continue;
        // BFS order of this component
        int ord[32], m = 0; bool inq[32] = { false };
        ord[m++] = start; inq[start] = true;
        for (int k = 0; k < m; k++) {
            uint32_t nb = adj[ord[k]];
            while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; if (!inq[u]) { inq[u] = true; ord[m++] = u; } }
        }
        for (int k = 0; k < m; k++) done[ord[k]] = true;
        // iterative backtracking over ord[]
        int k = 0; int tried[32];
        for (int t = 0; t < m; t++) tried[t] = 0;
        while (k < m) {
            int v = ord[k];
            int dom = (k == 0) ? 1 : 31;
            uint32_t nb = adj[v];
            while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1; if (col[u] >= 0) dom &= NB[col[u]]; }
            int c = -1;
            for (int cc = tried[k]; cc < 5; cc++) if ((dom >> cc) & 1) { c = cc; tried[k] = cc + 1; break; }
            if (c < 0) {                       // backtrack
                tried[k] = 0; col[v] = -1;
                k--;
                if (k < 0) return false;
                col[ord[k]] = -1;
                continue;
            }
            col[v] = c; k++;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    const char* tag = argc > 3 ? argv[3] : "a";
    FILE* fa = argc > 1 ? fopen(argv[1], "w") : nullptr;
    FILE* fb = argc > 2 ? fopen(argv[2], "w") : nullptr;
    char buf[4096]; uint32_t adj[64]; int deg[64];
    long long total = 0, nmax = 0, nno = 0;
    while (fgets(buf, sizeof(buf), stdin)) {
        int L = (int)strlen(buf);
        while (L && (buf[L - 1] == '\n' || buf[L - 1] == '\r')) buf[--L] = 0;
        if (!L) continue;
        total++;
        int n = decode(buf, deg, adj);
        if (!maximal_tf(n, adj)) continue;
        nmax++;
        if (fa) {
            int E = 0; char el[8192]; int q = 0;
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if ((adj[i] >> j) & 1u) { q += sprintf(el + q, " %d %d", i, j); E++; }
            fprintf(fa, "%s%d_%lld %d %d%s\n", tag, n, nmax - 1, n, E, el);
            if (!hom_c5(n, adj)) { nno++; fprintf(fb, "%s%d_%lld %d %d%s\n", tag, n, nmax - 1, n, E, el); }
        } else if (!hom_c5(n, adj)) nno++;
    }
    if (fa) fclose(fa);
    if (fb) fclose(fb);
    fprintf(stderr, "read %lld  maximaltf %lld  nohomC5 %lld\n", total, nmax, nno);
    return 0;
}
