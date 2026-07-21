// vcheck.cpp -- exhaustive local check over the r=4 gap moduli box:
//   * is every vertex of every hive polytope a LATTICE point (denominator 1)?
//   * what lattice multiplicities m actually occur at SIMPLE vertices
//     (exactly three distinct tight row directions, independent)?
// The abstract bound from cone_atlas.py is m <= 4 (m in {1,2,4} over all 455
// triples of rows).  This measures which of those are realised by hive data.
//
// Build: g++ -O3 -fopenmp -o vcheck vcheck.cpp     Usage: vcheck GMAX

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif
typedef long long ll;

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
static ll det3(ll a, ll b, ll c, ll d, ll e, ll f, ll g, ll h, ll i) {
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}
static ll gcdl(ll a, ll b) { a = a < 0 ? -a : a; b = b < 0 ? -b : b; while (b) { ll t = a % b; a = b; b = t; } return a; }

int main(int argc, char **argv) {
    int G = atoi(argv[1]); ll W = G + 1, TOT = 1; for (int i = 0; i < 9; i++) TOT *= W;
    fprintf(stderr, "vcheck gaps in [0,%d]^9 : %lld vectors\n", G, TOT);
    ll gm[9] = {0}; ll gden = 1; ll gpoly = 0; int garg[9] = {0}; ll gworst = 1;
#pragma omp parallel
    {
        ll lm[9] = {0}; ll lden = 1, lpoly = 0, lworst = 1; int larg[9] = {0};
#pragma omp for schedule(dynamic, 512)
        for (ll code = 0; code < TOT; code++) {
            int g[9]; ll t = code;
            for (int i = 0; i < 9; i++) { g[i] = (int)(t % W); t /= W; }
            ll Aw = 3LL * g[2] + 2LL * g[1] + g[0], Bw = 3LL * g[5] + 2LL * g[4] + g[3], Cw = 3LL * g[8] + 2LL * g[7] + g[6];
            ll D = Cw - Aw - Bw; if (((D % 4) + 4) % 4) continue;
            ll k = D / 4, l4 = 0, m4 = 0, n4 = 0; if (k >= 0) l4 = k; else n4 = -k;
            ll lam[4] = {l4 + g[2] + g[1] + g[0], l4 + g[2] + g[1], l4 + g[2], l4};
            ll mu[4] = {m4 + g[5] + g[4] + g[3], m4 + g[5] + g[4], m4 + g[5], m4};
            ll nu[4] = {n4 + g[8] + g[7] + g[6], n4 + g[8] + g[7], n4 + g[8], n4};
            RowXYZ R[24]; int nr = build_rows_xyz(lam, mu, nu, R);
            if (nr < 0) continue;
            lpoly++;
            for (int i = 0; i < nr; i++) for (int j = i + 1; j < nr; j++) for (int l = j + 1; l < nr; l++) {
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
                bool feas = true;
                int tdir[24][3]; int ntd = 0;
                for (int q = 0; q < nr; q++) {
                    ll lhs = (ll)R[q].p * num[0] + (ll)R[q].q * num[1] + (ll)R[q].r * num[2];
                    ll rr = R[q].rhs * den;
                    if (lhs > rr) { feas = false; break; }
                    if (lhs == rr) {
                        bool dup = false;
                        for (int z = 0; z < ntd; z++) if (tdir[z][0] == R[q].p && tdir[z][1] == R[q].q && tdir[z][2] == R[q].r) { dup = true; break; }
                        if (!dup) { tdir[ntd][0] = R[q].p; tdir[ntd][1] = R[q].q; tdir[ntd][2] = R[q].r; ntd++; }
                    }
                }
                if (!feas) continue;
                // vertex denominator
                ll gg = den; for (int q = 0; q < 3; q++) gg = gcdl(gg, num[q]);
                ll d = den / gg; if (d > lden) lden = d;
                // simple vertex: exactly 3 distinct tight directions
                if (ntd != 3) continue;
                ll dt = det3(tdir[0][0], tdir[0][1], tdir[0][2], tdir[1][0], tdir[1][1], tdir[1][2], tdir[2][0], tdir[2][1], tdir[2][2]);
                if (!dt) continue;
                // primitive ray generators of {x : n_i.x <= 0}
                ll gen[3][3];
                for (int q = 0; q < 3; q++) {
                    int a1 = (q + 1) % 3, a2 = (q + 2) % 3;
                    ll cr[3] = {(ll)tdir[a1][1] * tdir[a2][2] - (ll)tdir[a1][2] * tdir[a2][1],
                                (ll)tdir[a1][2] * tdir[a2][0] - (ll)tdir[a1][0] * tdir[a2][2],
                                (ll)tdir[a1][0] * tdir[a2][1] - (ll)tdir[a1][1] * tdir[a2][0]};
                    ll gd = gcdl(gcdl(cr[0], cr[1]), cr[2]); if (gd) for (int z = 0; z < 3; z++) cr[z] /= gd;
                    ll s = (ll)tdir[q][0] * cr[0] + (ll)tdir[q][1] * cr[1] + (ll)tdir[q][2] * cr[2];
                    if (s > 0) for (int z = 0; z < 3; z++) cr[z] = -cr[z];
                    for (int z = 0; z < 3; z++) gen[q][z] = cr[z];
                }
                ll m = det3(gen[0][0], gen[0][1], gen[0][2], gen[1][0], gen[1][1], gen[1][2], gen[2][0], gen[2][1], gen[2][2]);
                if (m < 0) m = -m;
                if (m < 9) lm[m]++;
                if (m > lworst) { lworst = m; memcpy(larg, g, sizeof(g)); }
            }
        }
#pragma omp critical
        {
            for (int i = 0; i < 9; i++) gm[i] += lm[i];
            if (lden > gden) gden = lden;
            gpoly += lpoly;
            if (lworst > gworst) { gworst = lworst; memcpy(garg, larg, sizeof(larg)); }
        }
    }
    printf("GMAX=%d  nonempty-row-system polytopes=%lld\n", G, gpoly);
    printf("max vertex denominator over ALL vertices = %lld  (1 == every Q is a lattice polytope)\n", gden);
    printf("simple-vertex multiplicity histogram: ");
    for (int i = 1; i < 9; i++) if (gm[i]) printf("m=%d:%lld  ", i, gm[i]);
    printf("\nmax realised simple-vertex multiplicity = %lld at gaps a=(%d,%d,%d) b=(%d,%d,%d) c=(%d,%d,%d)\n",
           gworst, garg[0], garg[1], garg[2], garg[3], garg[4], garg[5], garg[6], garg[7], garg[8]);
    return 0;
}
