/* f8_heur.c -- heuristic UPPER bound on bip(G) (any cut certifies bip <= m-|cut|).
   Multi-restart steepest-descent + Kernighan-Lin style pass on the number of
   monochromatic edges.  Reads graph6 on stdin, prints
       <graph6> n m bipUB ratio
   Build: gcc -O3 -march=native -o f8_heur.exe f8_heur.c
   Usage: f8_heur.exe [restarts]      (default 4000)
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 512
static char line[262144];
static uint64_t rs = 88172645463325252ULL;
static inline uint64_t xr(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

int main(int argc, char **argv) {
    int RESTARTS = (argc > 1) ? atoi(argv[1]) : 4000;
    static int nb[MAXN][MAXN], deg[MAXN], side[MAXN], cnt[MAXN], best_side[MAXN];
    while (fgets(line, sizeof(line), stdin)) {
        int L = (int)strlen(line);
        while (L > 0 && (line[L-1]=='\n'||line[L-1]=='\r')) line[--L] = 0;
        if (L == 0 || line[0] == '>') continue;
        const unsigned char *p = (const unsigned char *)line;
        int n, off;
        if (p[0] == 126) {                       /* n >= 63 : 4-byte header */
            n = ((p[1]-63)<<12) | ((p[2]-63)<<6) | (p[3]-63); off = 4;
        } else { n = p[0]-63; off = 1; }
        if (n > MAXN) { printf("%s SKIP n=%d\n", line, n); continue; }
        for (int i = 0; i < n; i++) deg[i] = 0;
        int bitpos = 0, m = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                int byte = off + bitpos/6, sh = 5 - (bitpos%6);
                if ((p[byte]-63) >> sh & 1) { nb[i][deg[i]++]=j; nb[j][deg[j]++]=i; m++; }
                bitpos++;
            }
        int best = m;
        for (int r = 0; r < RESTARTS; r++) {
            for (int i = 0; i < n; i++) side[i] = (int)(xr() & 1);
            for (int i = 0; i < n; i++) { cnt[i]=0; }
            for (int i = 0; i < n; i++)
                for (int k = 0; k < deg[i]; k++) if (side[nb[i][k]]) cnt[i]++;
            int mono = 0;
            for (int i = 0; i < n; i++) mono += side[i] ? cnt[i] : deg[i]-cnt[i];
            mono /= 2;
            int improved = 1;
            while (improved) {
                improved = 0;
                for (int i = 0; i < n; i++) {
                    int same = side[i] ? cnt[i] : deg[i]-cnt[i];
                    int gain = 2*same - deg[i];      /* mono decreases by gain */
                    if (gain > 0) {
                        mono -= gain; side[i] ^= 1;
                        if (side[i]) for (int k=0;k<deg[i];k++) cnt[nb[i][k]]++;
                        else         for (int k=0;k<deg[i];k++) cnt[nb[i][k]]--;
                        improved = 1;
                    }
                }
            }
            if (mono < best) { best = mono; for(int i=0;i<n;i++) best_side[i]=side[i]; }
        }
        printf("%s n=%d m=%d bipUB=%d ratio=%d/%d %.9f\n",
               line, n, m, best, best, n*n, (double)best/((double)n*n));
        fflush(stdout);
    }
    return 0;
}
