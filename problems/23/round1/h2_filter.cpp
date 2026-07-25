// Filter graph6 lines: keep maximal triangle-free (every non-adjacent pair has a
// common neighbour) and, optionally, twin-free (no two vertices with equal
// neighbourhoods).  Both filters are sound for the H2 weighted-blow-up search:
//   g(H) <= g(H*) for any maximal triangle-free completion H* on the same vertices;
//   g(H) = g(H minus one of a twin pair).
// Build: clang++ -O3 -march=native -std=c++17 -o h2_filter.exe h2_filter.cpp
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <iostream>

// Backtracking test for a homomorphism H -> C5.
// If one exists then H[n] -> C5 for every weight vector, and the elementary C5 lemma
// gives bip(H[n]) <= N^2/25; such bases can never violate the conjecture, so they are
// dropped.  (bip is monotone under adding edges, and G -> K implies G subgraph of K[m],
// hence bip(G) <= bip(K[m]).)
static int NHOM;
static const uint64_t* HADJ;
static int hcol[64];

static bool hom_rec(int k) {
    if (k == NHOM) return true;
    int lo = (k == 0) ? 0 : 0, hi = (k == 0) ? 1 : 5;   // fix colour of vertex 0 to 0
    for (int c = lo; c < hi; ++c) {
        bool ok = true;
        for (int u = 0; u < k; ++u)
            if ((HADJ[k] >> u) & 1) {
                int d = (hcol[u] - c + 5) % 5;
                if (d != 1 && d != 4) { ok = false; break; }
            }
        if (ok) { hcol[k] = c; if (hom_rec(k + 1)) return true; }
    }
    return false;
}

static bool hom_to_C5(int n, const uint64_t* adj) {
    NHOM = n; HADJ = adj;
    return hom_rec(0);
}

int main(int argc, char** argv) {
    bool twinfree = false, quiet = false, dropc5 = false;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "-twinfree")) twinfree = true;
        if (!strcmp(argv[i], "-q")) quiet = true;
        if (!strcmp(argv[i], "-noC5hom")) dropc5 = true;
    }
    std::ios::sync_with_stdio(false);
    std::string line;
    uint64_t adj[64];
    long long seen = 0, kept = 0;
    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        if (line.empty()) continue;
        const char* p = line.c_str();
        int n = (int)p[0] - 63;
        if (n < 1 || n > 62) continue;
        ++p;
        for (int i = 0; i < n; ++i) adj[i] = 0;
        int cur = 0, nbits = 0;
        for (int j = 1; j < n; ++j)
            for (int i = 0; i < j; ++i) {
                if (nbits == 0) { cur = (int)(*p++) - 63; nbits = 6; }
                int bit = (cur >> (nbits - 1)) & 1; --nbits;
                if (bit) { adj[i] |= 1ull << j; adj[j] |= 1ull << i; }
            }
        ++seen;
        bool ok = true;
        for (int i = 0; i < n && ok; ++i)
            for (int j = i + 1; j < n; ++j) {
                bool e = (adj[i] >> j) & 1;
                if (e) { if (adj[i] & adj[j]) { ok = false; break; } }        // triangle
                else   { if (!(adj[i] & adj[j])) { ok = false; break; } }     // not maximal
            }
        if (ok && twinfree)
            for (int i = 0; i < n && ok; ++i)
                for (int j = i + 1; j < n; ++j)
                    if (adj[i] == adj[j]) { ok = false; break; }
        if (ok && dropc5 && hom_to_C5(n, adj)) ok = false;
        if (ok) { ++kept; if (!quiet) { std::fputs(line.c_str(), stdout); std::fputc('\n', stdout); } }
    }
    std::fprintf(stderr, "filter: seen=%lld kept=%lld\n", seen, kept);
    return 0;
}
