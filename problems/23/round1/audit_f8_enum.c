/* audit_f8_enum.c -- INDEPENDENT complete enumeration of LABELLED reduced patterns
   (maximal triangle-free + twin-free) on n vertices, in the restricted form
        deg(0) = Delta(G)  and  N(0) = {1,...,deg(0)}
   Every reduced pattern has such a labelling, so the count settles completeness of
   the claimed f8_rmtf_<n>.g6 lists when compared with
        sum_H  t_H * d_H! * (n-1-d_H)! / |Aut(H)|.
   Usage: audit_f8_enum.exe n
   Build:  gcc -O3 -march=native -o audit_f8_enum.exe audit_f8_enum.c              */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int n, d, nB;
static uint32_t adj[32];
static int deg[32], Bv[32], cand[32][32], ncand[32];
static long long cnt, nodes;

static int leafcheck(void) {
    for (int v = 0; v < n; v++) if (deg[v] < 3 || deg[v] > d) return 0;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++) {
            if (!((adj[u] >> v) & 1) && (adj[u] & adj[v]) == 0) return 0;  /* not maximal */
            if (adj[u] == adj[v]) return 0;                                /* twins */
        }
    return 1;
}

static void rec(int bi);

static void placeB(int bi, int p, uint32_t mask, int sz, int hasA, uint32_t forbid) {
    nodes++;
    int b = Bv[bi];
    int remB = nB - 1 - bi;             /* B vertices still to be placed after b */
    if (p == ncand[bi]) {
        if (sz > d || !hasA || sz + remB < 3) return;
        uint32_t mm = mask;
        while (mm) { int u = __builtin_ctz(mm); mm &= mm - 1;
                     adj[u] |= 1u << b; adj[b] |= 1u << u; deg[u]++; deg[b]++; }
        int ok = 1;
        for (int a = 1; a <= d && ok; a++) if (deg[a] + remB < 3) ok = 0;
        for (int k = 0; k <= bi && ok; k++) if (deg[Bv[k]] + remB < 3) ok = 0;
        if (ok) rec(bi + 1);
        mm = mask;
        while (mm) { int u = __builtin_ctz(mm); mm &= mm - 1;
                     adj[u] &= ~(1u << b); adj[b] &= ~(1u << u); deg[u]--; deg[b]--; }
        return;
    }
    if (sz + (ncand[bi] - p) < 3 - remB) return;
    placeB(bi, p + 1, mask, sz, hasA, forbid);                       /* skip */
    int u = cand[bi][p];
    if (!((forbid >> u) & 1) && deg[u] < d && sz + 1 <= d)
        placeB(bi, p + 1, mask | (1u << u), sz + 1, hasA || (u <= d),
               forbid | adj[u] | (1u << u));
}

static void rec(int bi) {
    if (bi == nB) { if (leafcheck()) cnt++; return; }
    ncand[bi] = 0;
    for (int a = 1; a <= d; a++) cand[bi][ncand[bi]++] = a;
    for (int k = 0; k < bi; k++) cand[bi][ncand[bi]++] = Bv[k];
    placeB(bi, 0, 0u, 0, 0, 0u);
}

int main(int argc, char **argv) {
    n = atoi(argv[1]);
    long long total = 0;
    for (d = 3; d <= n - 1; d++) {
        nB = n - 1 - d;
        if (nB < 0) continue;
        for (int i = 0; i < n; i++) { adj[i] = 0; deg[i] = 0; }
        for (int a = 1; a <= d; a++) { adj[0] |= 1u << a; adj[a] |= 1u; deg[a] = 1; }
        deg[0] = d;
        for (int k = 0; k < nB; k++) Bv[k] = d + 1 + k;
        cnt = 0; nodes = 0;
        rec(0);
        printf("n=%d d=%d : %lld labelled (restricted) reduced patterns   [nodes %lld]\n",
               n, d, cnt, nodes);
        fflush(stdout);
        total += cnt;
    }
    printf("n=%d TOTAL = %lld\n", n, total);
    return 0;
}
