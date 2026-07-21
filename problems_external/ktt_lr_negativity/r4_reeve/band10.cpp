// band10.cpp -- BAND 10 of the r=4 Reeve-dimension sweep.
//
// TARGET (band assignment): unbounded weight, search directly for hive polytopes
// with  c = L(1) = 4  (equivalently h*_1 = 0 in dimension 3) and normalized
// volume V >= 2, and push V as high as possible.  A Reeve tetrahedron T_q is
// exactly such an object with V = q; a_1 = 2 - q/6 < 0 needs q >= 13.
//
// STRUCTURE USED (all exact, integers only, no floating point anywhere):
//   * Q(lam,mu,nu) = {h in R^3 : A h <= b}, A the FIXED 18x3 rhombus matrix,
//     b linear in the 9 gaps  a=(l1-l2,l2-l3,l3-l4), b=(m..), c=(n..).
//     The gap vector is realisable by partitions iff 4 | (Cw - Aw - Bw).
//   * c = 4 with dim Q = 3 and Q a LATTICE polytope  <=>  Q is an EMPTY lattice
//     3-simplex, i.e. 4 vertices, all lattice, and every edge lattice-primitive.
//     Then V = multiplicity of any vertex cone (White / Reeve).
//   So the cheap exact screen for the whole band is:
//     (i)   are all vertices lattice points?          (max denominator)
//     (ii)  4-vertex simplices: exact V = |det(edges)|
//     (iii) among those, all 6 edges primitive  =>  c = 4 CANDIDATE
//     (iv)  simple-vertex cone multiplicity m  (V of an empty simplex equals m)
//
// Modes
//   --exh G                exhaustive over gaps in [0,G]^9
//   --rand K N SEED        N uniform random gap vectors in [0,K]^9 (unbounded weight)
//   --one a1 a2 a3 b1 b2 b3 c1 c2 c3
//
// Build: clang++ -O3 -march=native -fopenmp -o band10.exe band10.cpp

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef long long ll;
typedef __int128 lll;

struct RowXYZ { int p, q, r; ll rhs; };

static int build_rows_xyz(const ll lam[4], const ll mu[4], const ll nu[4], RowXYZ out[24]) {
    ll B[5][5];
    for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) B[i][j] = 0;
    ll sl = lam[0] + lam[1] + lam[2] + lam[3];
    ll acc = 0; for (int y = 0; y <= 4; y++) { B[0][y] = acc; if (y < 4) acc += lam[y]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][4 - x] = sl + acc; if (x < 4) acc += mu[x]; }
    acc = 0; for (int x = 0; x <= 4; x++) { B[x][0] = acc; if (x < 4) acc += nu[x]; }
    B[0][0] = 0;
    auto isInt = [](int x, int y) { return (x == 1 && y == 1) || (x == 1 && y == 2) || (x == 2 && y == 1); };
    auto idx = [](int x, int y) { return (x == 1 && y == 1) ? 0 : (x == 1 && y == 2) ? 1 : 2; };
    int nr = 0; bool bad = false;
    auto add = [&](int px[2], int py[2], int mx[2], int my[2]) {
        ll co[3] = {0, 0, 0}; ll cst = 0;
        for (int t = 0; t < 2; t++) {
            if (isInt(px[t], py[t])) co[idx(px[t], py[t])] -= 1; else cst -= B[px[t]][py[t]];
            if (isInt(mx[t], my[t])) co[idx(mx[t], my[t])] += 1; else cst += B[mx[t]][my[t]];
        }
        if (!co[0] && !co[1] && !co[2]) { if (cst > 0) bad = true; return; }
        out[nr].p = (int)co[0]; out[nr].q = (int)co[1]; out[nr].r = (int)co[2]; out[nr].rhs = -cst; nr++;
    };
    for (int x = 0; x <= 4; x++) for (int y = 0; y <= 4; y++) {
        if (x + y <= 2) { int px[2] = {x + 1, x}, py[2] = {y, y + 1}, mx[2] = {x, x + 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
        if (y >= 1 && x + y <= 3) { int px[2] = {x, x + 1}, py[2] = {y, y}, mx[2] = {x, x + 1}, my[2] = {y + 1, y - 1}; add(px, py, mx, my); }
        if (x >= 1 && x + y <= 3) { int px[2] = {x, x}, py[2] = {y, y + 1}, mx[2] = {x + 1, x - 1}, my[2] = {y, y + 1}; add(px, py, mx, my); }
    }
    return bad ? -1 : nr;
}

static inline ll det3(ll a, ll b, ll c, ll d, ll e, ll f, ll g, ll h, ll i) {
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}
static inline lll det3L(const lll m[3][3]) {
    return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
         - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
         + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
}
static inline ll gcdl(ll a, ll b) { a = a < 0 ? -a : a; b = b < 0 ? -b : b; while (b) { ll t = a % b; a = b; b = t; } return a; }

struct Stat {
    ll realisable = 0, nonempty = 0;
    ll maxden = 1;             int argden[9] = {0};
    ll maxm = 1;               int argm[9] = {0};
    lll maxVsimplex = -1;      int argVs[9] = {0};
    lll maxVempty = -1;        int argVe[9] = {0};   // 4-vertex, lattice, ALL edges primitive
    ll nEmptyCand = 0;                                // ... with V >= 2
    ll nC4 = 0;                                       // unimodular primitive-edge simplices == exactly c=4
    ll nvhist[24] = {0};
    ll mhist[16] = {0};
    std::vector<std::vector<int> > cands;             // gap vectors, V >= 2 with primitive edges
};

static void merge(Stat &g, const Stat &l) {
    g.realisable += l.realisable; g.nonempty += l.nonempty; g.nEmptyCand += l.nEmptyCand; g.nC4 += l.nC4;
    if (l.maxden > g.maxden) { g.maxden = l.maxden; memcpy(g.argden, l.argden, sizeof(l.argden)); }
    if (l.maxm > g.maxm) { g.maxm = l.maxm; memcpy(g.argm, l.argm, sizeof(l.argm)); }
    if (l.maxVsimplex > g.maxVsimplex) { g.maxVsimplex = l.maxVsimplex; memcpy(g.argVs, l.argVs, sizeof(l.argVs)); }
    if (l.maxVempty > g.maxVempty) { g.maxVempty = l.maxVempty; memcpy(g.argVe, l.argVe, sizeof(l.argVe)); }
    for (int i = 0; i < 24; i++) g.nvhist[i] += l.nvhist[i];
    for (int i = 0; i < 16; i++) g.mhist[i] += l.mhist[i];
    for (size_t i = 0; i < l.cands.size() && g.cands.size() < 64; i++) g.cands.push_back(l.cands[i]);
}

// analyse one gap vector; returns false if not realisable / row system infeasible
static bool analyse(const int g[9], Stat &S) {
    ll Aw = 3LL * g[2] + 2LL * g[1] + g[0], Bw = 3LL * g[5] + 2LL * g[4] + g[3], Cw = 3LL * g[8] + 2LL * g[7] + g[6];
    ll D = Cw - Aw - Bw;
    if (((D % 4) + 4) % 4) return false;
    ll k = D / 4, l4 = 0, m4 = 0, n4 = 0;
    if (k >= 0) l4 = k; else n4 = -k;
    ll lam[4] = {l4 + g[2] + g[1] + g[0], l4 + g[2] + g[1], l4 + g[2], l4};
    ll mu[4] = {m4 + g[5] + g[4] + g[3], m4 + g[5] + g[4], m4 + g[5], m4};
    ll nu[4] = {n4 + g[8] + g[7] + g[6], n4 + g[8] + g[7], n4 + g[8], n4};
    RowXYZ R[24];
    int nr = build_rows_xyz(lam, mu, nu, R);
    S.realisable++;
    if (nr < 0) return true;   // boundary rhombus violated => Q empty

    // vertex enumeration over all triples of rows
    struct Vtx { ll n0, n1, n2, den; int ntd; int td[8][3]; };
    Vtx vs[40]; int nv = 0;
    for (int i = 0; i < nr && nv < 40; i++)
      for (int j = i + 1; j < nr && nv < 40; j++)
        for (int l = j + 1; l < nr && nv < 40; l++) {
            ll M[3][3] = {{R[i].p, R[i].q, R[i].r}, {R[j].p, R[j].q, R[j].r}, {R[l].p, R[l].q, R[l].r}};
            ll Dt = det3(M[0][0], M[0][1], M[0][2], M[1][0], M[1][1], M[1][2], M[2][0], M[2][1], M[2][2]);
            if (!Dt) continue;
            ll bb[3] = {R[i].rhs, R[j].rhs, R[l].rhs}, num[3];
            for (int cix = 0; cix < 3; cix++) {
                ll N[3][3];
                for (int rr = 0; rr < 3; rr++) for (int cc = 0; cc < 3; cc++) N[rr][cc] = (cc == cix) ? bb[rr] : M[rr][cc];
                num[cix] = det3(N[0][0], N[0][1], N[0][2], N[1][0], N[1][1], N[1][2], N[2][0], N[2][1], N[2][2]);
            }
            ll den = Dt; if (den < 0) { den = -den; for (int q = 0; q < 3; q++) num[q] = -num[q]; }
            bool feas = true; int ntd = 0; int td[8][3];
            for (int q = 0; q < nr; q++) {
                lll lhs = (lll)R[q].p * num[0] + (lll)R[q].q * num[1] + (lll)R[q].r * num[2];
                lll rr = (lll)R[q].rhs * den;
                if (lhs > rr) { feas = false; break; }
                if (lhs == rr) {
                    bool dup = false;
                    for (int z = 0; z < ntd; z++) if (td[z][0] == R[q].p && td[z][1] == R[q].q && td[z][2] == R[q].r) { dup = true; break; }
                    if (!dup && ntd < 8) { td[ntd][0] = R[q].p; td[ntd][1] = R[q].q; td[ntd][2] = R[q].r; ntd++; }
                    else if (!dup) ntd = 99;   // overflow marker
                }
            }
            if (!feas) continue;
            ll gg = den; for (int q = 0; q < 3; q++) gg = gcdl(gg, num[q]);
            if (gg > 1) { den /= gg; for (int q = 0; q < 3; q++) num[q] /= gg; }
            bool dup = false;
            for (int z = 0; z < nv; z++)
                if (vs[z].den == den && vs[z].n0 == num[0] && vs[z].n1 == num[1] && vs[z].n2 == num[2]) { dup = true; break; }
            if (dup) continue;
            Vtx &V = vs[nv++];
            V.n0 = num[0]; V.n1 = num[1]; V.n2 = num[2]; V.den = den; V.ntd = ntd;
            for (int z = 0; z < (ntd <= 8 ? ntd : 0); z++) { V.td[z][0] = td[z][0]; V.td[z][1] = td[z][1]; V.td[z][2] = td[z][2]; }
        }
    if (nv == 0) return true;
    S.nonempty++;
    S.nvhist[nv < 24 ? nv : 23]++;

    bool alllat = true;
    for (int z = 0; z < nv; z++) {
        if (vs[z].den > S.maxden) { S.maxden = vs[z].den; memcpy(S.argden, g, sizeof(int) * 9); }
        if (vs[z].den != 1) alllat = false;
    }
    // simple-vertex cone multiplicities
    for (int z = 0; z < nv; z++) {
        if (vs[z].ntd != 3) continue;
        ll dt = det3(vs[z].td[0][0], vs[z].td[0][1], vs[z].td[0][2],
                     vs[z].td[1][0], vs[z].td[1][1], vs[z].td[1][2],
                     vs[z].td[2][0], vs[z].td[2][1], vs[z].td[2][2]);
        if (!dt) continue;
        ll gen[3][3];
        for (int q = 0; q < 3; q++) {
            int a1 = (q + 1) % 3, a2 = (q + 2) % 3;
            ll cr[3] = {(ll)vs[z].td[a1][1] * vs[z].td[a2][2] - (ll)vs[z].td[a1][2] * vs[z].td[a2][1],
                        (ll)vs[z].td[a1][2] * vs[z].td[a2][0] - (ll)vs[z].td[a1][0] * vs[z].td[a2][2],
                        (ll)vs[z].td[a1][0] * vs[z].td[a2][1] - (ll)vs[z].td[a1][1] * vs[z].td[a2][0]};
            ll gd = gcdl(gcdl(cr[0], cr[1]), cr[2]); if (gd) for (int w = 0; w < 3; w++) cr[w] /= gd;
            ll s = (ll)vs[z].td[q][0] * cr[0] + (ll)vs[z].td[q][1] * cr[1] + (ll)vs[z].td[q][2] * cr[2];
            if (s > 0) for (int w = 0; w < 3; w++) cr[w] = -cr[w];
            for (int w = 0; w < 3; w++) gen[q][w] = cr[w];
        }
        ll m = det3(gen[0][0], gen[0][1], gen[0][2], gen[1][0], gen[1][1], gen[1][2], gen[2][0], gen[2][1], gen[2][2]);
        if (m < 0) m = -m;
        if (m < 16) S.mhist[m]++;
        if (m > S.maxm) { S.maxm = m; memcpy(S.argm, g, sizeof(int) * 9); }
    }

    // 4-vertex lattice simplex: exact normalized volume and edge primitivity
    if (nv == 4 && alllat) {
        lll E[3][3];
        for (int q = 0; q < 3; q++) {
            E[q][0] = (lll)vs[q + 1].n0 - vs[0].n0;
            E[q][1] = (lll)vs[q + 1].n1 - vs[0].n1;
            E[q][2] = (lll)vs[q + 1].n2 - vs[0].n2;
        }
        lll V = det3L(E); if (V < 0) V = -V;
        if (V > 0) {
            if (V > S.maxVsimplex) { S.maxVsimplex = V; memcpy(S.argVs, g, sizeof(int) * 9); }
            bool prim = true;
            for (int i = 0; i < 4 && prim; i++) for (int j = i + 1; j < 4 && prim; j++) {
                ll d0 = vs[j].n0 - vs[i].n0, d1 = vs[j].n1 - vs[i].n1, d2 = vs[j].n2 - vs[i].n2;
                ll gd = gcdl(gcdl(d0, d1), d2);
                if (gd != 1) prim = false;
            }
            if (prim) {
                if (V == 1) S.nC4++;
                if (V > S.maxVempty) { S.maxVempty = V; memcpy(S.argVe, g, sizeof(int) * 9); }
                if (V >= 2) {
                    S.nEmptyCand++;
                    if (S.cands.size() < 64) S.cands.push_back(std::vector<int>(g, g + 9));
                }
            }
        }
    }
    return true;
}

static void print128(const char *tag, lll v) {
    if (v < 0) { printf("%s=-1(none)", tag); return; }
    char buf[64]; int n = 0;
    if (v == 0) { buf[n++] = '0'; }
    while (v > 0) { buf[n++] = (char)('0' + (int)(v % 10)); v /= 10; }
    printf("%s=", tag);
    for (int i = n - 1; i >= 0; i--) putchar(buf[i]);
}

static void report(const Stat &G, const char *hdr) {
    printf("%s\n", hdr);
    printf("realisable(4|D)=%lld  nonempty Q=%lld\n", G.realisable, G.nonempty);
    printf("max vertex denominator = %lld  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n", G.maxden,
           G.argden[0], G.argden[1], G.argden[2], G.argden[3], G.argden[4], G.argden[5], G.argden[6], G.argden[7], G.argden[8]);
    printf("max simple-vertex multiplicity = %lld  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n", G.maxm,
           G.argm[0], G.argm[1], G.argm[2], G.argm[3], G.argm[4], G.argm[5], G.argm[6], G.argm[7], G.argm[8]);
    printf("multiplicity histogram: "); for (int i = 1; i < 16; i++) if (G.mhist[i]) printf("m=%d:%lld ", i, G.mhist[i]); printf("\n");
    printf("n_vertices histogram: "); for (int i = 0; i < 24; i++) if (G.nvhist[i]) printf("%d:%lld ", i, G.nvhist[i]); printf("\n");
    print128("max V over 4-vertex lattice simplices", G.maxVsimplex);
    printf("  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           G.argVs[0], G.argVs[1], G.argVs[2], G.argVs[3], G.argVs[4], G.argVs[5], G.argVs[6], G.argVs[7], G.argVs[8]);
    print128("max V over 4-vertex lattice simplices with ALL EDGES PRIMITIVE (c=4 candidates)", G.maxVempty);
    printf("  at a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           G.argVe[0], G.argVe[1], G.argVe[2], G.argVe[3], G.argVe[4], G.argVe[5], G.argVe[6], G.argVe[7], G.argVe[8]);
    printf("count of primitive-edge simplices with V>=2 (c=4 CANDIDATES) = %lld\n", G.nEmptyCand);
    printf("count of UNIMODULAR primitive-edge simplices (exactly c=4, V=1) = %lld\n", G.nC4);
    for (size_t i = 0; i < G.cands.size(); i++) {
        const std::vector<int> &g = G.cands[i];
        printf("CAND a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n", g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8]);
    }
    fflush(stdout);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: band10 --exh G | --rand K N SEED | --one g1..g9\n"); return 2; }
    if (!strcmp(argv[1], "--one")) {
        int g[9]; for (int i = 0; i < 9; i++) g[i] = atoi(argv[2 + i]);
        Stat S; bool ok = analyse(g, S);
        printf("realisable=%d\n", (int)ok);
        report(S, "ONE");
        return 0;
    }
    if (!strcmp(argv[1], "--exh")) {
        int G = atoi(argv[2]); ll W = G + 1, TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
        fprintf(stderr, "band10 exhaustive gaps in [0,%d]^9 : %lld vectors\n", G, TOT);
        Stat GS;
#pragma omp parallel
        {
            Stat LS;
#pragma omp for schedule(dynamic, 1024)
            for (ll code = 0; code < TOT; code++) {
                int g[9]; ll t = code;
                for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
                analyse(g, LS);
            }
#pragma omp critical
            merge(GS, LS);
        }
        char hdr[128]; snprintf(hdr, sizeof(hdr), "BAND10 EXHAUSTIVE GMAX=%d vectors=%lld", G, TOT);
        report(GS, hdr);
        return 0;
    }
    if (!strcmp(argv[1], "--rand")) {
        ll K = atoll(argv[2]), N = atoll(argv[3]);
        unsigned long long seed0 = (argc > 4) ? strtoull(argv[4], 0, 10) : 20260721ULL;
        Stat GS;
#pragma omp parallel
        {
            int tid = 0;
#ifdef _OPENMP
            tid = omp_get_thread_num();
#endif
            unsigned long long st = seed0 * 6364136223846793005ULL + 1442695040888963407ULL + (unsigned long long)tid * 0x9E3779B97F4A7C15ULL + 88172645463325252ULL;
            Stat LS;
#pragma omp for schedule(dynamic, 4096)
            for (ll it = 0; it < N; it++) {
                int g[9];
                for (int i = 0; i < 9; i++) {
                    st ^= st << 13; st ^= st >> 7; st ^= st << 17;
                    g[i] = (int)(st % (unsigned long long)(K + 1));
                }
                // steer onto the realisable lattice: fix g[6] so that 4 | D when possible
                ll Aw = 3LL * g[2] + 2LL * g[1] + g[0], Bw = 3LL * g[5] + 2LL * g[4] + g[3];
                ll rest = 3LL * g[8] + 2LL * g[7];
                ll need = ((Aw + Bw - rest) % 4 + 4) % 4;
                ll cand = g[6] - ((g[6] - need) % 4 + 4) % 4;
                if (cand >= 0) g[6] = (int)cand; else g[6] = (int)need;
                if (g[6] > K) g[6] -= 4;
                if (g[6] < 0) continue;
                analyse(g, LS);
            }
#pragma omp critical
            merge(GS, LS);
        }
        char hdr[160]; snprintf(hdr, sizeof(hdr), "BAND10 RANDOM K=%lld N=%lld seed=%llu", K, N, seed0);
        report(GS, hdr);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 2;
}
