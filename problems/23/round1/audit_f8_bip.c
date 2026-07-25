/* audit_f8_bip.c -- INDEPENDENT exact bip(G)=|E|-maxcut by enumerating all 2^(n-1)
   bipartitions.  Written from scratch for the adversarial audit (plain loop, no
   Gray code, so it shares no logic with f8_bip.c).  Reads graph6 on stdin.
   Build: gcc -O3 -march=native -o audit_f8_bip.exe audit_f8_bip.c            */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static char line[1 << 20];

int main(void) {
    while (fgets(line, sizeof line, stdin)) {
        int L = (int)strlen(line);
        while (L > 0 && (line[L-1]=='\n' || line[L-1]=='\r')) line[--L] = 0;
        if (L == 0 || line[0] == '>') continue;
        const unsigned char *p = (const unsigned char *)line;
        int n, off;
        if (p[0] == 126) { n = ((p[1]-63)<<12)|((p[2]-63)<<6)|(p[3]-63); off = 4; }
        else { n = p[0]-63; off = 1; }
        if (n > 32) { printf("%s n=%d SKIP\n", line, n); continue; }
        uint32_t adj[32];
        for (int i = 0; i < n; i++) adj[i] = 0;
        int bp = 0, m = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                if (((p[off + bp/6] - 63) >> (5 - bp%6)) & 1) {
                    adj[i] |= 1u<<j; adj[j] |= 1u<<i; m++;
                }
                bp++;
            }
        int best = m;
        uint64_t tot = 1ull << (n-1);
        for (uint64_t s = 0; s < tot; s++) {
            uint32_t side = (uint32_t)(s << 1);      /* vertex 0 on side 0 */
            int mono = 0;
            for (int v = 0; v < n; v++) {
                uint32_t same = (side >> v) & 1 ? (adj[v] & side)
                                                : (adj[v] & ~side);
                mono += __builtin_popcount(same);
            }
            mono >>= 1;
            if (mono < best) best = mono;
        }
        printf("%s n=%d m=%d bip=%d ratio=%.10f\n", line, n, m, best,
               (double)best/((double)n*(double)n));
        fflush(stdout);
    }
    return 0;
}
