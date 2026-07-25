/* filter_rmtf.c  -- read graph6 lines on stdin (assumed triangle-free, connected),
   keep only REDUCED MAXIMAL TRIANGLE-FREE graphs:
     (M) maximal triangle-free  <=>  every non-adjacent pair u!=v has a common neighbour
     (T) twin-free              <=>  no two vertices have identical neighbourhoods
   Both conditions are justified in the write-up (Lemma R1/R2): passing to a
   maximal triangle-free supergraph never decreases psi, and merging twins
   (equivalently N(u) subset N(v)) never decreases psi.
   Prints the surviving graph6 lines verbatim.  n <= 64.
   Build:  gcc -O2 -o filter_rmtf.exe filter_rmtf.c
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static char line[4096];

int main(int argc, char **argv) {
    long long total = 0, kept = 0;
    while (fgets(line, sizeof(line), stdin)) {
        int L = (int)strlen(line);
        while (L > 0 && (line[L-1] == '\n' || line[L-1] == '\r')) line[--L] = 0;
        if (L == 0) continue;
        if (line[0] == '>') continue;           /* header */
        total++;
        const unsigned char *p = (const unsigned char *)line;
        int n, off;
        if (p[0] == 126) { fprintf(stderr, "n>62 unsupported\n"); return 1; }
        n = p[0] - 63; off = 1;
        if (n > 64) { fprintf(stderr, "n>64 unsupported\n"); return 1; }
        uint64_t adj[64];
        for (int i = 0; i < n; i++) adj[i] = 0;
        int bitpos = 0;
        int nbits = n * (n - 1) / 2;
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < j; i++) {
                int byte = off + bitpos / 6;
                int sh   = 5 - (bitpos % 6);
                int v = (p[byte] - 63) >> sh & 1;
                if (v) { adj[i] |= (uint64_t)1 << j; adj[j] |= (uint64_t)1 << i; }
                bitpos++;
            }
        }
        (void)nbits;
        int ok = 1;
        for (int u = 0; u < n && ok; u++)
            for (int v = u + 1; v < n && ok; v++) {
                int adjacent = (adj[u] >> v) & 1;
                if (!adjacent && (adj[u] & adj[v]) == 0) ok = 0;   /* not maximal */
                if (adj[u] == adj[v]) ok = 0;                      /* twins */
            }
        if (ok) { kept++; puts(line); }
    }
    fprintf(stderr, "read %lld kept %lld\n", total, kept);
    return 0;
}
