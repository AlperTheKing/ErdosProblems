// ROOT-AGENT (Claude): keep only graphs that are NOT homomorphic to C5.
//
// If H -> C5 then max_x psi(H,x) <= 1/25 by the classical AM-GM-twice argument (accepted base), so
// C5-colourable patterns can never be counterexamples.  The counterexample search space is exactly
//     { maximal triangle-free, NOT C5-colourable }.
// Reads graph6 on stdin, writes the non-C5-colourable ones to stdout.
#include <cstdio>
#include <cstdint>
#include <cstring>

int n;
uint32_t adj[32];
int col[32];

static bool ok(int v, int c) {
    for (int u = 0; u < n; ++u)
        if ((adj[v] >> u) & 1u) {
            if (col[u] < 0) continue;
            int d = (col[u] - c + 5) % 5;
            if (d != 1 && d != 4) return false;         // edges must map to edges of C5
        }
    return true;
}

static bool rec(int v) {
    if (v == n) return true;
    int hi = (v == 0) ? 1 : 5;                          // fix vertex 0's colour by symmetry
    for (int c = 0; c < hi; ++c)
        if (ok(v, c)) { col[v] = c; if (rec(v + 1)) return true; col[v] = -1; }
    return false;
}

int main() {
    char line[512];
    long long total = 0, kept = 0;
    while (std::fgets(line, sizeof line, stdin)) {
        size_t len = std::strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (!len) continue;
        ++total;
        size_t p = 0;
        n = line[p++] - 63;
        if (n == 63) { n = 0; for (int k = 0; k < 3; ++k) n = (n << 6) | (line[p++] - 63); }
        if (n > 32) continue;
        for (int i = 0; i < n; ++i) { adj[i] = 0; col[i] = -1; }
        int cur = 0, bits = 0;
        for (int j = 1; j < n; ++j)
            for (int i = 0; i < j; ++i) {
                if (!bits) { cur = line[p++] - 63; bits = 6; }
                int b = (cur >> (bits - 1)) & 1; --bits;
                if (b) { adj[i] |= (1u << j); adj[j] |= (1u << i); }
            }
        if (!rec(0)) { ++kept; std::fputs(line, stdout); std::fputc('\n', stdout); }
    }
    std::fprintf(stderr, "not-C5-colourable: %lld of %lld\n", kept, total);
    return 0;
}
