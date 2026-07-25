/* f8_bip.c -- exact bip(G) = |E| - maxcut(G) by Gray-code enumeration of all
   2^(n-1) bipartitions.  Reads graph6 lines on stdin, prints
       <graph6> n m bip  bip*  (bip as rational over n^2)
   Exact integer arithmetic throughout.  n <= 32 (2^31 states) -- practical n <= 30.
   Build: gcc -O3 -march=native -o f8_bip.exe f8_bip.c
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static char line[8192];

int main(int argc, char **argv) {
    int thresh = (argc > 1) ? atoi(argv[1]) : 0;   /* only print bip >= thresh */
    while (fgets(line, sizeof(line), stdin)) {
        int L = (int)strlen(line);
        while (L > 0 && (line[L-1] == '\n' || line[L-1] == '\r')) line[--L] = 0;
        if (L == 0 || line[0] == '>') continue;
        const unsigned char *p = (const unsigned char *)line;
        int n = p[0] - 63, off = 1;
        if (n > 32) { printf("%s n=%d SKIP(n>32)\n", line, n); continue; }
        uint32_t adj[32];
        for (int i = 0; i < n; i++) adj[i] = 0;
        int bitpos = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                int byte = off + bitpos / 6, sh = 5 - (bitpos % 6);
                if ((p[byte] - 63) >> sh & 1) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
                bitpos++;
            }
        int m = 0, deg[32];
        for (int i = 0; i < n; i++) { deg[i] = __builtin_popcount(adj[i]); m += deg[i]; }
        m /= 2;
        /* Gray code over subsets of {1..n-1}; vertex 0 fixed on side 0.
           side[] = current side, cnt[v] = #neighbours of v on side 1. */
        int side[32], cnt[32];
        for (int i = 0; i < n; i++) { side[i] = 0; cnt[i] = 0; }
        int mono = m;              /* all on side 0 -> every edge monochromatic */
        int best = mono;
        uint64_t total = 1ull << (n - 1);
        for (uint64_t g = 1; g < total; g++) {
            int v = __builtin_ctzll(g) + 1;      /* bit to flip (vertices 1..n-1) */
            /* flipping v: monochromatic edges at v change from
               (side[v]==1 ? cnt[v] : deg[v]-cnt[v]) to the complement */
            int same = side[v] ? cnt[v] : deg[v] - cnt[v];
            mono += deg[v] - 2 * same;
            side[v] ^= 1;
            uint32_t A = adj[v];
            if (side[v]) { while (A) { int u = __builtin_ctz(A); cnt[u]++; A &= A - 1; } }
            else         { while (A) { int u = __builtin_ctz(A); cnt[u]--; A &= A - 1; } }
            if (mono < best) best = mono;
        }
        if (best >= thresh) {
            printf("%s n=%d m=%d bip=%d ratio=%d/%d %.9f\n",
                   line, n, m, best, best, n * n, (double)best / (double)(n * n));
            fflush(stdout);
        }
    }
    return 0;
}
