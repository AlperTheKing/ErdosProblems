// ROOT-AGENT (Claude): fast graph6 filter to MAXIMAL triangle-free graphs.
//
// The pattern space for the conjecture is complete at maximal triangle-free graphs: adding an edge
// raises every q_S, hence psi pointwise, so every pattern is dominated by a maximal one on the same
// vertex set.  geng -t gives triangle-free; maximality must be filtered:
//     G maximal triangle-free  <=>  triangle-free AND every non-adjacent pair has a common neighbour.
//
// Reads graph6 lines on stdin, writes the maximal ones to stdout.  Bitset adjacency, n <= 32.
#include <cstdio>
#include <cstdint>
#include <cstring>

int main() {
    char line[512];
    long long total = 0, kept = 0;
    while (std::fgets(line, sizeof line, stdin)) {
        size_t len = std::strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (!len) continue;
        ++total;
        size_t p = 0;
        int n = line[p++] - 63;
        if (n == 63) { n = 0; for (int k = 0; k < 3; ++k) n = (n << 6) | (line[p++] - 63); }
        if (n > 32) continue;
        uint32_t adj[32] = {0};
        int cur = 0, bits = 0;
        for (int j = 1; j < n; ++j)
            for (int i = 0; i < j; ++i) {
                if (!bits) { cur = line[p++] - 63; bits = 6; }
                int b = (cur >> (bits - 1)) & 1; --bits;
                if (b) { adj[i] |= (1u << j); adj[j] |= (1u << i); }
            }
        bool ok = true;
        for (int i = 0; i < n && ok; ++i)
            for (int j = i + 1; j < n; ++j) {
                uint32_t common = adj[i] & adj[j];
                bool nb = (adj[i] >> j) & 1u;
                if (nb) { if (common) { ok = false; break; } }     // triangle
                else    { if (!common) { ok = false; break; } }    // not maximal
            }
        if (ok) { ++kept; std::fputs(line, stdout); std::fputc('\n', stdout); }
    }
    std::fprintf(stderr, "kept %lld of %lld\n", kept, total);
    return 0;
}
