// f7_c5col.cpp -- decide, for each graph6 graph on stdin, whether it admits a homomorphism to C5.
//
// G -> C5 exists  <=>  chi_c(G) <= 5/2.  If G -> C5 then (Theorem 1) bip(G) <= N^2/25 and
// bip(G) <= e(G)/5.  So the non-C5-colourable triangle-free graphs are exactly where those
// proofs stop.
//
// Backtracking over colours 0..4 with vertex 0 pinned to colour 0 (C5 is vertex-transitive).
// usage: f7_c5col [--list-bad]
#include <cstdio>
#include <cstring>
#include <string>
#include <iostream>

static unsigned adj[32];
static int col[32], N;

static bool decode_g6(const std::string &s, int &n, unsigned *A) {
    if (s.empty()) return false;
    size_t p = 0; int c = (unsigned char)s[p];
    if (c == 126) return false;
    n = c - 63; p++;
    for (int i = 0; i < n; i++) A[i] = 0;
    int nbits = n * (n - 1) / 2, bit = 0, i = 1, j = 0;
    for (int k = 0; k < nbits; k++) {
        if (bit == 0) { if (p >= s.size()) return false; c = (unsigned char)s[p++] - 63; bit = 6; }
        bit--;
        if ((c >> bit) & 1) { A[i] |= (1u << j); A[j] |= (1u << i); }
        j++; if (j == i) { j = 0; i++; }
    }
    return true;
}

// C5 adjacency: colours a,b adjacent iff (a-b) mod 5 in {1,4}
static inline bool c5adj(int a, int b) { int d = (a - b + 5) % 5; return d == 1 || d == 4; }

static bool solve(int v) {
    if (v == N) return true;
    for (int c = 0; c < 5; c++) {
        bool ok = true;
        unsigned nb = adj[v];
        while (nb) {
            int u = __builtin_ctz(nb); nb &= nb - 1;
            if (u < v && !c5adj(c, col[u])) { ok = false; break; }
        }
        if (!ok) continue;
        col[v] = c;
        if (solve(v + 1)) return true;
    }
    return false;
}

int main(int argc, char **argv) {
    bool listBad = (argc > 1 && strcmp(argv[1], "--list-bad") == 0);
    std::string line; long long tot = 0, bad = 0;
    std::ios::sync_with_stdio(false);
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
        if (line.empty() || line[0] == '>') continue;
        int n; if (!decode_g6(line, n, adj)) continue;
        N = n; tot++;
        col[0] = 0;
        bool ok = solve(1);
        if (!ok) { bad++; if (listBad) printf("%s\n", line.c_str()); }
    }
    fprintf(stderr, "graphs=%lld  NOT_C5_colourable=%lld\n", tot, bad);
    return 0;
}
